from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib import error, request

from .models import ImporterFailure, TranslationArtifact


def load_prompt_instructions(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```text\s*(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_response_format(schema: dict[str, Any], *, name: str) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": True,
            "schema": schema,
        },
    }


def validate_normalization_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Response root is not an object."]

    required = schema.get("required", [])
    for key in required:
        if key not in payload:
            errors.append(f"Missing required field: {key}")

    if errors:
        return errors

    if payload.get("output_language") != "en":
        errors.append("Field output_language must be 'en'.")

    array_fields = (
        "secondary_cuisines",
        "ingredient_families",
        "mood_tags",
        "storage_profile",
        "dietary_flags",
        "provision_tags",
        "ingredients",
        "steps",
        "uncertainty_notes",
    )
    for key in array_fields:
        if key in payload and not isinstance(payload[key], list):
            errors.append(f"Field {key} is not an array.")

    for idx, ingredient in enumerate(payload.get("ingredients", []), start=1):
        if not isinstance(ingredient, dict):
            errors.append(f"Ingredient {idx} is not an object.")
            continue
        for key in ("amount", "unit", "item", "note", "optional", "group"):
            if key not in ingredient:
                errors.append(f"Ingredient {idx} missing field: {key}")
        if "item" in ingredient and not isinstance(ingredient.get("item"), str):
            errors.append(f"Ingredient {idx} field item is not a string.")

    for idx, step in enumerate(payload.get("steps", []), start=1):
        if not isinstance(step, dict):
            errors.append(f"Step {idx} is not an object.")
            continue
        for key in ("step_number", "instruction", "time_note", "heat_note", "equipment_note"):
            if key not in step:
                errors.append(f"Step {idx} missing field: {key}")
        if "step_number" in step and not isinstance(step.get("step_number"), int):
            errors.append(f"Step {idx} step_number is not an integer.")
        if "instruction" in step and not isinstance(step.get("instruction"), str):
            errors.append(f"Step {idx} instruction is not a string.")

    return errors


def validate_preprocessing_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    payload_dict = payload.to_dict() if isinstance(payload, TranslationArtifact) else payload
    return TranslationArtifact.validate_payload(payload_dict, schema)


def lmstudio_post_json(*, url: str, payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            raw_response = response.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ImporterFailure("transport", f"LM Studio HTTP error {exc.code}: {body}") from exc
    except error.URLError as exc:
        raise ImporterFailure("transport", f"Could not connect to LM Studio at {url}: {exc}") from exc

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ImporterFailure("transport", f"Unexpected LM Studio response shape: {raw_response[:500]}") from exc


def lmstudio_chat_raw_content(*, base_url: str, payload: dict[str, Any], timeout_seconds: int) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    parsed = lmstudio_post_json(url=url, payload=payload, timeout_seconds=timeout_seconds)

    try:
        message = parsed["choices"][0]["message"]
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            content = message.get("reasoning_content")
    except (KeyError, IndexError, TypeError) as exc:
        raise ImporterFailure("transport", f"Unexpected LM Studio response shape: {parsed}") from exc

    if not isinstance(content, str) or not content.strip():
        raise ImporterFailure("transport", "LM Studio returned empty content.")

    return content


def lmstudio_completion_raw_text(*, base_url: str, payload: dict[str, Any], timeout_seconds: int) -> str:
    url = base_url.rstrip("/") + "/completions"
    parsed = lmstudio_post_json(url=url, payload=payload, timeout_seconds=timeout_seconds)

    try:
        text = parsed["choices"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ImporterFailure("transport", f"Unexpected LM Studio completion response shape: {parsed}") from exc

    if not isinstance(text, str) or not text.strip():
        raise ImporterFailure("transport", "LM Studio returned empty completion text.")

    return text


def build_translategemma_completion_prompt(*, source_text: str, source_lang_code: str, target_lang_code: str) -> str:
    language_names = {
        "en": "English",
        "sv": "Swedish",
    }
    source_lang = language_names.get(source_lang_code.replace("_", "-").casefold(), source_lang_code)
    target_lang = language_names.get(target_lang_code.replace("_", "-").casefold(), target_lang_code)
    return (
        "<bos><start_of_turn>user\n"
        f"You are a professional {source_lang} ({source_lang_code}) to "
        f"{target_lang} ({target_lang_code}) translator. Your goal is to accurately "
        f"convey the meaning and nuances of the original {source_lang} text while "
        f"adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.\n"
        f"Produce only the {target_lang} translation, without any additional "
        f"explanations or commentary. Please translate the following {source_lang} "
        f"text into {target_lang}:\n\n\n"
        f"{source_text.strip()}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )


def run_preprocessing_contract(
    *,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    source_text: str,
    source_lang_code: str,
    response_format: dict[str, Any],
    temperature: float,
    timeout_seconds: int,
) -> tuple[TranslationArtifact, str]:
    if "translategemma" in model.casefold():
        completion_payload = {
            "model": model,
            "prompt": build_translategemma_completion_prompt(
                source_text=source_text,
                source_lang_code=source_lang_code,
                target_lang_code="en",
            ),
            "temperature": temperature,
            "stream": False,
        }
        translated_text = lmstudio_completion_raw_text(
            base_url=base_url,
            payload=completion_payload,
            timeout_seconds=timeout_seconds,
        ).strip()
        raw_payload = {
            "source_language": source_lang_code,
            "output_language": "en",
            "translated_text": translated_text,
        }
        errors = validate_preprocessing_payload(raw_payload, response_format)
        if errors:
            raise ImporterFailure("preprocess", "; ".join(errors))
        return TranslationArtifact.from_payload(raw_payload), json.dumps(raw_payload, ensure_ascii=True)

    payload, raw_text = run_json_contract(
        base_url=base_url,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_format=response_format,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
        failure_stage="preprocess",
    )
    errors = validate_preprocessing_payload(payload, response_format)
    if errors:
        raise ImporterFailure("preprocess", "; ".join(errors))
    artifact = TranslationArtifact.from_payload(payload)
    return artifact, raw_text


def run_json_contract(
    *,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_format: dict[str, Any],
    temperature: float,
    timeout_seconds: int,
    failure_stage: str = "normalize",
) -> tuple[dict[str, Any], str]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": response_format,
        "temperature": temperature,
        "stream": False,
    }
    try:
        content = lmstudio_chat_raw_content(
            base_url=base_url,
            payload=payload,
            timeout_seconds=timeout_seconds,
        )
    except ImporterFailure as exc:
        if "conversations must start with a user prompt" not in exc.message.casefold():
            raise
        merged_prompt = "\n\n".join(
            [
                "Follow these instructions exactly.",
                system_prompt.strip(),
                "User input:",
                user_prompt,
            ]
        )
        fallback_payload = {
            "model": model,
            "messages": [{"role": "user", "content": merged_prompt}],
            "response_format": response_format,
            "temperature": temperature,
            "stream": False,
        }
        content = lmstudio_chat_raw_content(
            base_url=base_url,
            payload=fallback_payload,
            timeout_seconds=timeout_seconds,
        )

    try:
        return json.loads(content), content
    except json.JSONDecodeError as exc:
        raise ImporterFailure(failure_stage, f"LM Studio returned non-JSON content: {content[:500]}") from exc
