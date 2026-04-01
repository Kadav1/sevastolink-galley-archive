from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from pathlib import Path
from typing import Any


class ImporterFailure(RuntimeError):
    def __init__(self, stage: str, message: str):
        super().__init__(message)
        self.stage = stage
        self.message = message


_SEGMENT_ID_PATTERN = re.compile(r"^seg_[0-9]{4,}$")
_SEGMENT_TYPES = {
    "title",
    "ingredient_line",
    "instruction_line",
    "note",
    "other",
}
_UNCERTAINTY_FLAGS = {
    "unknown_token",
    "ambiguous_ingredient",
    "ambiguous_modifier",
    "unresolved_unit",
    "ocr_noise",
}
_STAGE1_ROOT_PROPERTIES = {
    "source_language",
    "output_language",
    "translated_text",
    "segments",
}
_STAGE1_SEGMENT_PROPERTIES = {
    "segment_id",
    "segment_type",
    "source_text",
    "translated_text",
    "uncertainty_flags",
}


def _resolve_stage1_schema(schema: Any | None) -> dict[str, Any] | None:
    if not isinstance(schema, dict):
        return None
    json_schema = schema.get("json_schema")
    if isinstance(json_schema, dict) and isinstance(json_schema.get("schema"), dict):
        return json_schema["schema"]
    return schema


@dataclass
class ParsedSource:
    title_lines: list[str] = field(default_factory=list)
    ingredient_lines: list[str] = field(default_factory=list)
    instruction_lines: list[str] = field(default_factory=list)
    note_lines: list[str] = field(default_factory=list)
    time_lines: list[str] = field(default_factory=list)
    difficulty_lines: list[str] = field(default_factory=list)
    method_lines: list[str] = field(default_factory=list)
    serving_lines: list[str] = field(default_factory=list)


@dataclass
class ProtectedToken:
    source_text: str
    quantity_text: str
    normalized_quantity: str
    unit_text: str
    normalized_unit: str
    line_role: str


@dataclass
class DriftCode:
    code: str
    severity: str
    message: str


@dataclass
class IngredientRecord:
    position: int
    group_heading: str | None
    quantity: str | None
    unit: str | None
    item: str
    preparation: str | None
    optional: bool
    display_text: str | None


@dataclass
class StepRecord:
    position: int
    instruction: str
    time_note: str | None
    equipment_note: str | None


@dataclass
class TranslationSegment:
    segment_id: str
    segment_type: str
    source_text: str
    translated_text: str
    uncertainty_flags: list[str]

    @classmethod
    def from_payload(
        cls,
        payload: Any,
        *,
        index: int | None = None,
    ) -> TranslationSegment:
        payload_dict = payload if isinstance(payload, dict) else {}
        uncertainty_flags = payload_dict.get("uncertainty_flags", [])
        parsed_flags = [flag for flag in uncertainty_flags if isinstance(flag, str)]
        return cls(
            segment_id=payload_dict["segment_id"],
            segment_type=payload_dict["segment_type"],
            source_text=payload_dict["source_text"],
            translated_text=payload_dict["translated_text"],
            uncertainty_flags=parsed_flags,
        )

    @classmethod
    def validate_payload(cls, payload: Any, *, index: int, errors: list[str]) -> None:
        prefix = f"Preprocessing segment {index}"
        if not isinstance(payload, dict):
            errors.append(f"{prefix} is not an object.")
            return

        for key in payload:
            if key not in _STAGE1_SEGMENT_PROPERTIES:
                errors.append(f"{prefix} has additional property: {key}")

        for key in ("segment_id", "segment_type", "source_text", "translated_text", "uncertainty_flags"):
            if key not in payload:
                errors.append(f"{prefix} missing field: {key}")

        segment_id = payload.get("segment_id")
        if "segment_id" in payload and (not isinstance(segment_id, str) or not _SEGMENT_ID_PATTERN.match(segment_id)):
            errors.append(f"{prefix} segment_id is invalid.")

        segment_type = payload.get("segment_type")
        if "segment_type" in payload and (not isinstance(segment_type, str) or segment_type not in _SEGMENT_TYPES):
            errors.append(f"{prefix} segment_type is invalid.")

        source_text = payload.get("source_text")
        if "source_text" in payload and (not isinstance(source_text, str) or not source_text.strip()):
            errors.append(f"{prefix} source_text must be a non-empty string.")

        translated_text = payload.get("translated_text")
        if "translated_text" in payload and (not isinstance(translated_text, str) or not translated_text.strip()):
            errors.append(f"{prefix} translated_text must be a non-empty string.")

        uncertainty_flags = payload.get("uncertainty_flags")
        if "uncertainty_flags" in payload:
            if not isinstance(uncertainty_flags, list):
                errors.append(f"{prefix} uncertainty_flags must be an array.")
                return
            seen_flags: set[str] = set()
            for flag in uncertainty_flags:
                if not isinstance(flag, str) or flag not in _UNCERTAINTY_FLAGS:
                    errors.append(f"{prefix} uncertainty flag is invalid.")
                    continue
                if flag in seen_flags:
                    errors.append(f"{prefix} has duplicate uncertainty flags.")
                    continue
                seen_flags.add(flag)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TranslationArtifact:
    source_language: str
    output_language: str
    translated_text: str
    segments: list[TranslationSegment] = field(default_factory=list)

    @classmethod
    def from_payload(
        cls,
        payload: Any,
    ) -> TranslationArtifact:
        if isinstance(payload, cls):
            return payload

        payload_dict = payload if isinstance(payload, dict) else {}
        segments_payload = payload_dict.get("segments", [])
        parsed_segments = [
            TranslationSegment.from_payload(segment_payload, index=index)
            for index, segment_payload in enumerate(segments_payload, start=1)
            if isinstance(segment_payload, dict)
        ]
        return cls(
            source_language=payload_dict["source_language"],
            output_language=payload_dict["output_language"],
            translated_text=payload_dict["translated_text"],
            segments=parsed_segments,
        )

    @classmethod
    def validate_payload(cls, payload: Any, schema: Any | None = None) -> list[str]:
        errors: list[str] = []
        if not isinstance(payload, dict):
            return ["Preprocessing response root is not an object."]

        schema = _resolve_stage1_schema(schema)
        allowed_root_properties = _STAGE1_ROOT_PROPERTIES
        if schema is not None:
            properties = schema.get("properties")
            if isinstance(properties, dict):
                allowed_root_properties = set(properties.keys())

        for key in ("source_language", "output_language", "translated_text"):
            if key not in payload:
                errors.append(f"Missing required preprocessing field: {key}")

        if errors:
            return errors

        for key in payload:
            if key not in allowed_root_properties:
                errors.append(f"Preprocessing field has additional property: {key}")

        source_language = payload.get("source_language")
        output_language = payload.get("output_language")
        translated_text = payload.get("translated_text")

        if not isinstance(source_language, str) or not source_language.strip():
            errors.append("Preprocessing field source_language must be a non-empty string.")
        if output_language != "en":
            errors.append("Preprocessing field output_language must be 'en'.")
        if not isinstance(translated_text, str) or not translated_text.strip():
            errors.append("Preprocessing field translated_text must be a non-empty string.")

        segments = payload.get("segments")
        if segments is not None:
            if not isinstance(segments, list):
                errors.append("Preprocessing field segments must be an array when present.")
            else:
                for index, segment in enumerate(segments, start=1):
                    TranslationSegment.validate_payload(segment, index=index, errors=errors)

        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass
class ReferenceMatchItem:
    source_token: str
    matched_entry_key: str
    deterministic: bool
    requires_review: bool = False


@dataclass
class ReferenceMatchArtifact:
    pipeline_stage: str
    render_profile: str
    locale: str
    unit_matches: list[ReferenceMatchItem] = field(default_factory=list)
    term_matches: list[ReferenceMatchItem] = field(default_factory=list)
    contextual_matches: list[ReferenceMatchItem] = field(default_factory=list)
    drift_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceInfo:
    source_type: str
    source_language: str | None
    output_language: str | None
    source_url: str | None
    source_file: str
    relative_source_path: str
    raw_source_text: str
    normalized_input_text: str


@dataclass
class CandidateUpdatePayload:
    title: str | None
    short_description: str | None
    dish_role: str | None
    primary_cuisine: str | None
    technique_family: str | None
    complexity: str | None
    time_class: str | None
    servings: str | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    notes: str | None
    service_notes: str | None
    source_credit: str | None
    ingredients: list[IngredientRecord]
    steps: list[StepRecord]


@dataclass
class CandidateExtrasPayload:
    secondary_cuisines: list[str]
    ingredient_families: list[str]
    service_format: str | None
    season: str | None
    mood_tags: list[str]
    storage_profile: list[str]
    dietary_flags: list[str]
    provision_tags: list[str]
    sector: str | None
    operational_class: str | None
    heat_window: str | None
    total_time_minutes: int | None
    yield_text: str | None
    uncertainty_notes: list[str]
    confidence_summary: str | None


@dataclass
class CandidateRecord:
    candidate_status: str
    approval_required: bool
    candidate_update: CandidateUpdatePayload
    candidate_extras: CandidateExtrasPayload


@dataclass
class AiMetadata:
    provider: str
    model: str
    prompt_path: str
    schema_path: str
    generated_at_unix: int
    ai_payload_json: str
    preprocessing_applied: bool = False
    preprocessing_input_path: str | None = None
    preprocessing_payload_json: str | None = None
    preprocessing_prompt_path: str | None = None
    preprocessing_schema_path: str | None = None


@dataclass
class CandidateBundle:
    artifact_type: str
    schema_version: str
    source: SourceInfo
    candidate: CandidateRecord
    ai_metadata: AiMetadata
    review_flags: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FileSelection:
    source_paths: list[Path]
    input_dir: Path | None = None


@dataclass
class FileResult:
    source_path: str
    status: str
    stage: str
    output_path: str | None = None
    warning_count: int = 0
    review_flag_count: int = 0
    error: str | None = None
    duration_ms: int | None = None


@dataclass
class RunSummary:
    selected_files: int
    successful_files: int
    failed_files: int
    emitted_candidates: int
    total_warnings: int
    total_review_flags: int


@dataclass
class RunReport:
    report_type: str
    schema_version: str
    run_label: str
    started_at: str
    completed_at: str
    status: str
    output_dir: str
    report_path: str
    selected_sources: list[str]
    results: list[FileResult] = field(default_factory=list)
    summary: RunSummary | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
