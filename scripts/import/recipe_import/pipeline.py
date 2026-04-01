from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from .constants import (
    ARTIFACT_TYPE,
    DEFAULT_PREPROCESSING_PROMPT_PATH,
    DEFAULT_PREPROCESSING_SCHEMA_PATH,
    DEFAULT_PROMPT_PATH,
    DEFAULT_REPORT_DIR,
    DEFAULT_SCHEMA_PATH,
    SCHEMA_VERSION,
)
from .discovery import resolve_file_selection
from .models import AiMetadata, CandidateBundle, CandidateRecord, ImporterFailure, ReferenceMatchArtifact, SourceInfo
from .models import TranslationArtifact, TranslationSegment
from .normalization_request import build_normalization_request
from .reference_match import build_reference_match
from .references import collect_preprocessing_guardrails
from .reporting import (
    build_report_path,
    build_run_label,
    create_report,
    failure_result,
    finalize_report,
    success_result,
    utc_now_iso,
    write_report,
)
from .transport import (
    load_prompt_instructions,
    load_schema,
    run_preprocessing_contract,
    run_json_contract,
    schema_response_format,
    validate_normalization_payload,
    validate_preprocessing_payload,
)
from .transforms import build_candidate_payloads, serialize_path_for_bundle


DEFAULT_RENDER_PROFILE = "english_metric_strict"
DEFAULT_LOCALE = "en_generic"


def build_stage1_translation_artifact(*, source_language: str, source_text: str, translated_text: str) -> TranslationArtifact:
    return TranslationArtifact(
        source_language=source_language,
        output_language="en",
        translated_text=translated_text,
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="other",
                source_text=source_text,
                translated_text=translated_text,
                uncertainty_flags=[],
            )
        ],
    )


def _dedupe_preserving_order(items: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


_CONTEXTUAL_DRIFT_WARNING_MARKERS = (
    "lost the liquid/brine meaning",
    "collapsed pickle brine into relish",
    "drifted 'vitlökspulver' toward onion powder",
    "drifted 'lökpulver' away from onion powder",
    "lost the no-heat meaning",
    "dropped the rest/chill requirement",
    "did not preserve the preferred semantic target",
)


def _contextual_drift_terms(warnings: list[str]) -> set[str]:
    terms: set[str] = set()
    for warning in warnings:
        lowered = warning.casefold()
        if not any(marker in lowered for marker in _CONTEXTUAL_DRIFT_WARNING_MARKERS):
            continue
        matches = re.findall(r"'([^']+)'", warning)
        if matches:
            terms.add(matches[0].casefold())
        else:
            terms.add(lowered)
    return terms


def _count_contextual_drift_warnings(warnings: list[str]) -> int:
    return len(_contextual_drift_terms(warnings))


def assess_translation_quality(
    *,
    translation: TranslationArtifact,
    reference_match: ReferenceMatchArtifact,
    preprocessing_warnings: list[str] | None = None,
    preprocessing_review_flags: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    if not translation.translated_text.strip():
        raise ImporterFailure("preprocess", "Preprocessing returned an empty translated_text.")

    warnings: list[str] = []
    review_flags: list[str] = []
    preprocessing_warnings = preprocessing_warnings or []
    preprocessing_review_flags = preprocessing_review_flags or []

    measurement_flag = "Review preprocessing: source measurement parity changed between Swedish source and normalized input text."
    if "source_measurement_parity_changed" in reference_match.drift_signals and measurement_flag not in preprocessing_review_flags:
        warnings.append("Stage-1 translation changed measurement parity relative to the source.")

    if _count_contextual_drift_warnings(preprocessing_warnings) >= 2:
        warnings.append("Stage-1 translation contains multiple context-sensitive terms requiring semantic verification.")
        review_flags.append("Review preprocessing: translation quality review required due to multiple contextual-term risks.")

    return _dedupe_preserving_order(warnings), _dedupe_preserving_order(review_flags)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize recipe files with LM Studio and write intake-style candidate bundles."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        type=Path,
        help="Optional directory containing .txt/.md recipe files.",
    )
    parser.add_argument("output_dir", type=Path, help="Directory for emitted .candidate.json files")
    parser.add_argument(
        "--file",
        dest="input_files",
        action="append",
        type=Path,
        default=[],
        help="Add one recipe file to this run. Repeat to process multiple explicit files.",
    )
    parser.add_argument("--model", required=True, help="Loaded LM Studio model identifier")
    parser.add_argument(
        "--base-url",
        default="http://localhost:1234/v1",
        help="LM Studio OpenAI-compatible base URL (default: http://localhost:1234/v1)",
    )
    parser.add_argument(
        "--prompt-path",
        type=Path,
        default=DEFAULT_PROMPT_PATH,
        help=f"Path to runtime prompt markdown (default: {DEFAULT_PROMPT_PATH})",
    )
    parser.add_argument(
        "--schema-path",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"Path to output JSON schema (default: {DEFAULT_SCHEMA_PATH})",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help=f"Directory for emitted JSON run reports (default: {DEFAULT_REPORT_DIR})",
    )
    parser.add_argument(
        "--preprocess-only",
        action="store_true",
        help="Write saved .preprocessed.txt artifacts instead of candidate bundles.",
    )
    parser.add_argument(
        "--use-preprocessed-dir",
        type=Path,
        help="Read saved .preprocessed.txt artifacts from this directory instead of running inline preprocessing.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .candidate.json files")
    parser.add_argument("--temperature", type=float, default=0.0, help="LM Studio sampling temperature (default: 0.0)")
    parser.add_argument("--timeout-seconds", type=int, default=240, help="Request timeout in seconds (default: 240)")
    return parser.parse_args()


def build_user_prompt(filename: str, raw_source_text: str, source_type: str, source_url: str | None) -> str:
    envelope = {
        "raw_source_text": raw_source_text,
        "source_type": source_type,
        "source_url": source_url,
        "user_notes": None,
        "filename": filename,
    }
    return json.dumps(envelope, ensure_ascii=True, indent=2)


def build_bundle(
    *,
    source_path: Path,
    relative_source_path: Path,
    source_text: str,
    normalized_input_text: str,
    source_type: str,
    source_url: str | None,
    model: str,
    prompt_path: Path,
    schema_path: Path,
    raw_payload: dict[str, Any],
    raw_payload_json: str,
    preprocessing_applied: bool,
    preprocessing_input_path: Path | None,
    preprocessing_payload_json: str | None,
    preprocessing_prompt_path: Path | None,
    preprocessing_schema_path: Path | None,
    initial_warnings: list[str] | None = None,
    initial_review_flags: list[str] | None = None,
) -> CandidateBundle:
    candidate_update, candidate_extras, warnings, review_flags = build_candidate_payloads(
        raw_payload,
        initial_warnings=initial_warnings,
        initial_review_flags=initial_review_flags,
    )

    return CandidateBundle(
        artifact_type=ARTIFACT_TYPE,
        schema_version=SCHEMA_VERSION,
        source=SourceInfo(
            source_type=source_type,
            source_language=raw_payload.get("source_language"),
            output_language=raw_payload.get("output_language"),
            source_url=source_url,
            source_file=str(source_path),
            relative_source_path=str(relative_source_path),
            raw_source_text=source_text,
            normalized_input_text=normalized_input_text,
        ),
        candidate=CandidateRecord(
            candidate_status="pending",
            approval_required=True,
            candidate_update=candidate_update,
            candidate_extras=candidate_extras,
        ),
        ai_metadata=AiMetadata(
            provider="lm_studio",
            model=model,
            prompt_path=serialize_path_for_bundle(prompt_path),
            schema_path=serialize_path_for_bundle(schema_path),
            generated_at_unix=int(time.time()),
            ai_payload_json=raw_payload_json,
            preprocessing_applied=preprocessing_applied,
            preprocessing_input_path=serialize_path_for_bundle(preprocessing_input_path) if preprocessing_input_path else None,
            preprocessing_payload_json=preprocessing_payload_json,
            preprocessing_prompt_path=serialize_path_for_bundle(preprocessing_prompt_path) if preprocessing_prompt_path else None,
            preprocessing_schema_path=serialize_path_for_bundle(preprocessing_schema_path) if preprocessing_schema_path else None,
        ),
        review_flags=review_flags,
        warnings=warnings,
    )


def detect_source_language(source_text: str) -> str:
    lowered = source_text.casefold()
    swedish_markers = (
        "å",
        "ä",
        "ö",
        "ingredienser",
        "tillagning",
        "recept",
        "sås",
        "vitlökspulver",
        "lökpulver",
        "gurkrelish",
        "majonnäs",
        "för",
        "och",
        "ställ i kylen",
        "msk",
        "tsk",
        "krm",
        "nypa",
        "dl ",
    )
    if any(marker in lowered for marker in swedish_markers):
        return "sv"
    return "en"


def derive_input_root(source_paths: list[Path], input_dir: Path | None) -> Path:
    if input_dir is not None:
        return input_dir
    parent_paths = [str(path.parent.resolve()) for path in source_paths]
    return Path(os.path.commonpath(parent_paths))


def preprocessed_output_path(*, source_path: Path, input_root: Path, output_dir: Path) -> Path:
    relative_source_path = source_path.resolve().relative_to(input_root.resolve())
    return output_dir / relative_source_path.with_suffix(".preprocessed.txt")


def preprocess_file(
    *,
    input_root: Path,
    source_path: Path,
    output_dir: Path,
    base_url: str,
    model: str,
    preprocessing_system_prompt: str,
    preprocessing_schema: dict[str, Any],
    timeout_seconds: int,
    temperature: float,
    overwrite: bool,
) -> tuple[Path, str]:
    source_text = source_path.read_text(encoding="utf-8", errors="replace").strip()
    if not source_text:
        raise ImporterFailure("read_source", f"File is empty: {source_path}")

    source_type = "markdown_file" if source_path.suffix.lower() == ".md" else "text_file"
    source_language = detect_source_language(source_text)
    preprocessed_text = source_text

    if source_language != "en":
        preprocess_prompt = build_user_prompt(
            filename=source_path.name,
            raw_source_text=source_text,
            source_type=source_type,
            source_url=None,
        )
        preprocessing_payload, _ = run_preprocessing_contract(
            base_url=base_url,
            model=model,
            system_prompt=preprocessing_system_prompt,
            user_prompt=preprocess_prompt,
            source_text=source_text,
            source_lang_code=source_language,
            response_format=schema_response_format(preprocessing_schema, name="recipe_preprocessing_output"),
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )
        preprocessing_errors = validate_preprocessing_payload(preprocessing_payload, preprocessing_schema)
        if preprocessing_errors:
            raise ImporterFailure("preprocess", "; ".join(preprocessing_errors))
        preprocessed_text = preprocessing_payload["translated_text"].strip()
        if not preprocessed_text:
            raise ImporterFailure("preprocess", "Preprocessing returned an empty translated_text.")

    output_path = preprocessed_output_path(source_path=source_path, input_root=input_root, output_dir=output_dir)
    if output_path.exists() and not overwrite:
        raise ImporterFailure("emit_preprocessed", f"Refusing to overwrite existing file: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{preprocessed_text}\n", encoding="utf-8")
    return output_path, preprocessed_text


def process_file(
    *,
    input_root: Path,
    source_path: Path,
    output_dir: Path,
    base_url: str,
    model: str,
    prompt_path: Path,
    schema_path: Path,
    preprocessing_prompt_path: Path,
    preprocessing_schema_path: Path,
    system_prompt: str,
    schema: dict[str, Any],
    preprocessing_system_prompt: str,
    preprocessing_schema: dict[str, Any],
    overwrite: bool,
    temperature: float,
    timeout_seconds: int,
    preprocessed_input_text: str | None = None,
    preprocessing_artifact_path: Path | None = None,
) -> tuple[Path, CandidateBundle]:
    source_text = source_path.read_text(encoding="utf-8", errors="replace").strip()
    if not source_text:
        raise ImporterFailure("read_source", f"File is empty: {source_path}")

    resolved_source_path = source_path.resolve()
    resolved_input_root = input_root.resolve()
    source_type = "markdown_file" if source_path.suffix.lower() == ".md" else "text_file"
    relative_source_path = resolved_source_path.relative_to(resolved_input_root)
    source_language = detect_source_language(source_text)
    normalized_input_text = source_text
    preprocessing_applied = False
    preprocessing_payload_json: str | None = None
    effective_preprocessing_input_path = preprocessing_artifact_path.resolve() if preprocessing_artifact_path else None
    reference_warnings: list[str] = []
    reference_review_flags: list[str] = []
    translation_artifact: TranslationArtifact | None = None

    if preprocessed_input_text is not None:
        normalized_input_text = preprocessed_input_text.strip()
        preprocessing_applied = True
        if not normalized_input_text:
            raise ImporterFailure("preprocess_input", f"Saved preprocessing artifact is empty: {preprocessing_artifact_path}")
        translation_artifact = build_stage1_translation_artifact(
            source_language=source_language,
            source_text=source_text,
            translated_text=normalized_input_text,
        )
    elif source_language != "en":
        preprocess_prompt = build_user_prompt(
            filename=source_path.name,
            raw_source_text=source_text,
            source_type=source_type,
            source_url=None,
        )
        preprocessing_payload, preprocessing_payload_json = run_preprocessing_contract(
            base_url=base_url,
            model=model,
            system_prompt=preprocessing_system_prompt,
            user_prompt=preprocess_prompt,
            source_text=source_text,
            source_lang_code=source_language,
            response_format=schema_response_format(preprocessing_schema, name="recipe_preprocessing_output"),
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )
        preprocessing_errors = validate_preprocessing_payload(preprocessing_payload, preprocessing_schema)
        if preprocessing_errors:
            raise ImporterFailure("preprocess", "; ".join(preprocessing_errors))
        translation_artifact = TranslationArtifact.from_payload(preprocessing_payload)
        normalized_input_text = translation_artifact.translated_text.strip()
        preprocessing_applied = True
        if not normalized_input_text:
            raise ImporterFailure("preprocess", "Preprocessing returned an empty translated_text.")
    else:
        translation_artifact = build_stage1_translation_artifact(
            source_language=source_language,
            source_text=source_text,
            translated_text=normalized_input_text,
        )

    if translation_artifact is None:
        raise ImporterFailure("preprocess", "Unable to construct preprocessing translation artifact.")

    reference_warnings, reference_review_flags = collect_preprocessing_guardrails(
        source_text=source_text,
        normalized_input_text=normalized_input_text,
        source_language=source_language,
    )

    reference_match = build_reference_match(
        translation=translation_artifact,
        render_profile=DEFAULT_RENDER_PROFILE,
        locale=DEFAULT_LOCALE,
    )
    quality_warnings, quality_review_flags = assess_translation_quality(
        translation=translation_artifact,
        reference_match=reference_match,
        preprocessing_warnings=reference_warnings,
        preprocessing_review_flags=reference_review_flags,
    )
    normalization_request = build_normalization_request(
        translation=translation_artifact,
        reference_match=reference_match,
        render_profile=DEFAULT_RENDER_PROFILE,
        locale=DEFAULT_LOCALE,
    )

    user_prompt = json.dumps(normalization_request, ensure_ascii=True, indent=2)
    payload, raw_payload_json = run_json_contract(
        base_url=base_url,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_format=schema_response_format(schema, name="recipe_normalization_output"),
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )
    errors = validate_normalization_payload(payload, schema)
    if errors:
        raise ImporterFailure("normalize", "; ".join(errors))

    bundle = build_bundle(
        source_path=resolved_source_path,
        relative_source_path=relative_source_path,
        source_text=source_text,
        normalized_input_text=normalized_input_text,
        source_type=source_type,
        source_url=None,
        model=model,
        prompt_path=prompt_path,
        schema_path=schema_path,
        raw_payload=payload,
        raw_payload_json=raw_payload_json,
        preprocessing_applied=preprocessing_applied,
        preprocessing_input_path=effective_preprocessing_input_path,
        preprocessing_payload_json=preprocessing_payload_json,
        preprocessing_prompt_path=preprocessing_prompt_path if preprocessing_applied else None,
        preprocessing_schema_path=preprocessing_schema_path if preprocessing_applied else None,
        initial_warnings=reference_warnings + quality_warnings,
        initial_review_flags=reference_review_flags + quality_review_flags,
    )

    output_path = output_dir / relative_source_path.with_suffix(".candidate.json")
    if output_path.exists() and not overwrite:
        raise ImporterFailure("emit_bundle", f"Refusing to overwrite existing file: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=True), encoding="utf-8")
    return output_path, bundle


def main() -> int:
    args = parse_args()

    for path_arg, label in (
        (args.prompt_path, "Prompt file"),
        (args.schema_path, "Schema file"),
        (DEFAULT_PREPROCESSING_PROMPT_PATH, "Preprocessing prompt file"),
        (DEFAULT_PREPROCESSING_SCHEMA_PATH, "Preprocessing schema file"),
    ):
        if not path_arg.exists():
            print(f"{label} not found: {path_arg}")
            return 2

    try:
        selection = resolve_file_selection(args)
    except ImporterFailure as exc:
        print(exc.message)
        return 2

    input_root = derive_input_root(selection.source_paths, selection.input_dir)
    system_prompt = load_prompt_instructions(args.prompt_path)
    schema = load_schema(args.schema_path)
    preprocessing_system_prompt = load_prompt_instructions(DEFAULT_PREPROCESSING_PROMPT_PATH)
    preprocessing_schema = load_schema(DEFAULT_PREPROCESSING_SCHEMA_PATH)

    started_at = utc_now_iso()
    run_label = build_run_label()
    report_path = build_report_path(args.report_dir, run_label)
    report = create_report(
        output_dir=args.output_dir,
        report_path=report_path,
        selected_sources=selection.source_paths,
        run_label=run_label,
        started_at=started_at,
    )

    for source_path in selection.source_paths:
        start_ns = time.time_ns()
        try:
            if args.preprocess_only:
                output_path, preprocessed_text = preprocess_file(
                    input_root=input_root,
                    source_path=source_path,
                    output_dir=args.output_dir,
                    base_url=args.base_url,
                    model=args.model,
                    preprocessing_system_prompt=preprocessing_system_prompt,
                    preprocessing_schema=preprocessing_schema,
                    timeout_seconds=args.timeout_seconds,
                    temperature=args.temperature,
                    overwrite=args.overwrite,
                )
                duration_ms = int((time.time_ns() - start_ns) / 1_000_000)
                report.results.append(
                    success_result(
                        source_path=source_path,
                        stage="emit_preprocessed",
                        output_path=output_path,
                        warning_count=0,
                        review_flag_count=0,
                        duration_ms=duration_ms,
                    )
                )
                print(f"[OK] {source_path} -> {output_path}")
                continue

            preprocessed_input_text: str | None = None
            preprocessing_artifact_path: Path | None = None
            if args.use_preprocessed_dir is not None:
                candidate_path = preprocessed_output_path(
                    source_path=source_path,
                    input_root=input_root,
                    output_dir=args.use_preprocessed_dir,
                )
                if candidate_path.exists():
                    preprocessing_artifact_path = candidate_path
                    preprocessed_input_text = candidate_path.read_text(encoding="utf-8").strip()

            output_path, bundle = process_file(
                input_root=input_root,
                source_path=source_path,
                output_dir=args.output_dir,
                base_url=args.base_url,
                model=args.model,
                prompt_path=args.prompt_path,
                schema_path=args.schema_path,
                preprocessing_prompt_path=DEFAULT_PREPROCESSING_PROMPT_PATH,
                preprocessing_schema_path=DEFAULT_PREPROCESSING_SCHEMA_PATH,
                system_prompt=system_prompt,
                schema=schema,
                preprocessing_system_prompt=preprocessing_system_prompt,
                preprocessing_schema=preprocessing_schema,
                overwrite=args.overwrite,
                temperature=args.temperature,
                timeout_seconds=args.timeout_seconds,
                preprocessed_input_text=preprocessed_input_text,
                preprocessing_artifact_path=preprocessing_artifact_path,
            )
            duration_ms = int((time.time_ns() - start_ns) / 1_000_000)
            report.results.append(
                success_result(
                    source_path=source_path,
                    stage="emit_bundle",
                    output_path=output_path,
                    warning_count=len(bundle.warnings),
                    review_flag_count=len(bundle.review_flags),
                    duration_ms=duration_ms,
                )
            )
            print(f"[OK] {source_path} -> {output_path}")
        except ImporterFailure as exc:
            duration_ms = int((time.time_ns() - start_ns) / 1_000_000)
            report.results.append(
                failure_result(source_path=source_path, stage=exc.stage, error=exc.message, duration_ms=duration_ms)
            )
            print(f"[FAIL] {source_path} [{exc.stage}]: {exc.message}")
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.time_ns() - start_ns) / 1_000_000)
            report.results.append(
                failure_result(source_path=source_path, stage="unexpected", error=str(exc), duration_ms=duration_ms)
            )
            print(f"[FAIL] {source_path} [unexpected]: {exc}")

    report.completed_at = utc_now_iso()
    report = finalize_report(report)
    write_report(report)

    if report.summary is not None and report.summary.failed_files:
        print(f"\nCompleted with {report.summary.failed_files} failure(s). Report: {report.report_path}")
        return 1

    print(f"\nCompleted successfully. Report: {report.report_path}")
    return 0
