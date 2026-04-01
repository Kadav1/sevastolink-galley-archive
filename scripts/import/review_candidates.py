#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = REPO_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from src.db.database import SessionLocal, engine  # noqa: E402
from src.db.init_db import init_db  # noqa: E402
from src.models.intake import IntakeJob  # noqa: E402
from src.schemas.intake import ApproveIntakeIn, CandidateUpdate, IntakeJobCreate  # noqa: E402
from src.schemas.recipe import IngredientIn, SourceType, StepIn, VerificationState  # noqa: E402
from src.services import intake_service  # noqa: E402


DEFAULT_CANDIDATES_DIR = REPO_ROOT / "data" / "imports" / "parsed" / "recipes-candidates"
engine.echo = False


class ReviewFailure(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review and import normalized recipe candidate bundles into the local intake database."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List candidate bundle files.")
    list_parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=DEFAULT_CANDIDATES_DIR,
        help=f"Directory containing .candidate.json files (default: {DEFAULT_CANDIDATES_DIR})",
    )

    show_parser = subparsers.add_parser("show", help="Show one candidate bundle summary.")
    show_parser.add_argument("bundle", type=Path, help="Path to a .candidate.json file")

    edit_parser = subparsers.add_parser(
        "edit",
        help="Apply a JSON patch file to a candidate bundle in place.",
    )
    edit_parser.add_argument("bundle", type=Path, help="Path to a .candidate.json file")
    edit_parser.add_argument(
        "--patch",
        required=True,
        type=Path,
        help="Path to a JSON file containing candidate_update/candidate_extras edits.",
    )
    edit_parser.add_argument(
        "--clear-review-flags",
        action="store_true",
        help="Clear existing review_flags after applying the patch.",
    )
    edit_parser.add_argument(
        "--clear-warnings",
        action="store_true",
        help="Clear existing warnings after applying the patch.",
    )

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Import a candidate bundle into intake_jobs/structured_candidates for review.",
    )
    ingest_parser.add_argument("bundle", type=Path, help="Path to a .candidate.json file")
    ingest_parser.add_argument(
        "--force-new",
        action="store_true",
        help="Create a fresh intake job even if this bundle has already been ingested.",
    )

    approve_parser = subparsers.add_parser(
        "approve",
        help="Import a candidate bundle and approve it into recipes through the intake service.",
    )
    approve_parser.add_argument("bundle", type=Path, help="Path to a .candidate.json file")
    approve_parser.add_argument(
        "--force-new",
        action="store_true",
        help="Create a fresh intake job even if this bundle has already been ingested.",
    )
    approve_parser.add_argument(
        "--verification-state",
        choices=[state.value for state in VerificationState],
        default=VerificationState.unverified.value,
        help="Verification state for the approved recipe (default: Unverified)",
    )
    approve_parser.add_argument(
        "--source-type",
        choices=[source.value for source in SourceType],
        default=SourceType.ai_normalized.value,
        help="Source type for the approved recipe (default: AI-Normalized)",
    )
    approve_parser.add_argument("--source-title", type=str, default=None)
    approve_parser.add_argument("--source-author", type=str, default=None)
    approve_parser.add_argument("--source-notes", type=str, default=None)
    approve_parser.add_argument(
        "--allow-review-flags",
        action="store_true",
        help="Allow approval even when the candidate bundle contains review_flags.",
    )

    return parser.parse_args()


def candidate_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*.candidate.json") if path.is_file())


def load_bundle(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise ReviewFailure(f"Bundle does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("artifact_type") != "intake_candidate_bundle":
        raise ReviewFailure(f"File is not an intake candidate bundle: {path}")
    return data


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def summarize_bundle(path: Path, bundle: dict[str, Any]) -> str:
    candidate = bundle.get("candidate", {})
    update = candidate.get("candidate_update", {})
    flags = bundle.get("review_flags", [])
    warnings = bundle.get("warnings", [])
    return " | ".join(
        [
            rel_path(path),
            update.get("title") or "(untitled)",
            f"flags={len(flags)}",
            f"warnings={len(warnings)}",
            f"ingredients={len(update.get('ingredients', []))}",
            f"steps={len(update.get('steps', []))}",
        ]
    )


def print_bundle_details(path: Path, bundle: dict[str, Any]) -> None:
    candidate = bundle.get("candidate", {})
    update = candidate.get("candidate_update", {})
    extras = candidate.get("candidate_extras", {})
    source = bundle.get("source", {})

    print(f"Bundle: {rel_path(path)}")
    print(f"Title: {update.get('title') or '(untitled)'}")
    print(f"Candidate status: {candidate.get('candidate_status', 'pending')}")
    print(f"Source file: {source.get('relative_source_path') or source.get('source_file')}")
    print(f"Source language: {source.get('source_language')} -> {source.get('output_language')}")
    print(f"Review flags: {len(bundle.get('review_flags', []))}")
    print(f"Warnings: {len(bundle.get('warnings', []))}")
    if extras.get("confidence_summary"):
        print(f"Confidence: {extras['confidence_summary']}")
    print()

    if bundle.get("review_flags"):
        print("Review flags:")
        for flag in bundle["review_flags"]:
            print(f"- {flag}")
        print()

    if bundle.get("warnings"):
        print("Warnings:")
        for warning in bundle["warnings"]:
            print(f"- {warning}")
        print()

    print("Ingredients:")
    for ingredient in update.get("ingredients", []):
        print(f"- {ingredient.get('display_text') or ingredient.get('item') or '(missing item)'}")
    print()

    print("Steps:")
    for step in update.get("steps", []):
        print(f"- {step.get('position')}. {step.get('instruction')}")


def load_patch(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise ReviewFailure(f"Patch file does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ReviewFailure("Patch file must contain a top-level JSON object.")
    return data


def build_display_text(ingredient: dict[str, Any]) -> str:
    parts: list[str] = []
    quantity = ingredient.get("quantity")
    unit = ingredient.get("unit")
    item = ingredient.get("item")
    preparation = ingredient.get("preparation")
    optional = bool(ingredient.get("optional", False))

    if quantity:
        parts.append(str(quantity))
        if unit:
            parts.append(str(unit))
    if item:
        parts.append(str(item))
    if preparation:
        parts.append(f"({preparation})")
    if optional:
        parts.append("[optional]")
    return " ".join(parts).strip()


def normalize_patch_ingredients(values: Any) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise ReviewFailure("candidate_update.ingredients patch must be an array.")

    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(values, start=1):
        if not isinstance(raw, dict):
            raise ReviewFailure("Each patched ingredient must be an object.")
        item = raw.get("item")
        if not item:
            raise ReviewFailure(f"Patched ingredient {index} is missing item.")
        ingredient = {
            "position": int(raw.get("position", index)),
            "group_heading": raw.get("group_heading"),
            "quantity": raw.get("quantity"),
            "unit": raw.get("unit"),
            "item": item,
            "preparation": raw.get("preparation"),
            "optional": bool(raw.get("optional", False)),
            "display_text": raw.get("display_text"),
        }
        if not ingredient["display_text"]:
            ingredient["display_text"] = build_display_text(ingredient)
        normalized.append(ingredient)
    return normalized


def normalize_patch_steps(values: Any) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise ReviewFailure("candidate_update.steps patch must be an array.")

    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(values, start=1):
        if not isinstance(raw, dict):
            raise ReviewFailure("Each patched step must be an object.")
        instruction = raw.get("instruction")
        if not instruction:
            raise ReviewFailure(f"Patched step {index} is missing instruction.")
        normalized.append(
            {
                "position": int(raw.get("position", index)),
                "instruction": instruction,
                "time_note": raw.get("time_note"),
                "equipment_note": raw.get("equipment_note"),
            }
        )
    return normalized


def apply_bundle_patch(
    bundle_path: Path,
    patch_path: Path,
    *,
    clear_review_flags: bool,
    clear_warnings: bool,
) -> None:
    bundle = load_bundle(bundle_path)
    patch = load_patch(patch_path)

    candidate = bundle.setdefault("candidate", {})
    candidate_update = candidate.setdefault("candidate_update", {})
    candidate_extras = candidate.setdefault("candidate_extras", {})

    update_patch = patch.get("candidate_update", {})
    if update_patch is not None:
        if not isinstance(update_patch, dict):
            raise ReviewFailure("candidate_update patch must be an object.")
        for key, value in update_patch.items():
            if key == "ingredients":
                candidate_update[key] = normalize_patch_ingredients(value)
            elif key == "steps":
                candidate_update[key] = normalize_patch_steps(value)
            else:
                candidate_update[key] = value

    extras_patch = patch.get("candidate_extras", {})
    if extras_patch is not None:
        if not isinstance(extras_patch, dict):
            raise ReviewFailure("candidate_extras patch must be an object.")
        for key, value in extras_patch.items():
            candidate_extras[key] = value

    if "review_flags" in patch:
        if not isinstance(patch["review_flags"], list):
            raise ReviewFailure("review_flags patch must be an array.")
        bundle["review_flags"] = [str(item) for item in patch["review_flags"]]
    elif clear_review_flags:
        bundle["review_flags"] = []

    if "warnings" in patch:
        if not isinstance(patch["warnings"], list):
            raise ReviewFailure("warnings patch must be an array.")
        bundle["warnings"] = [str(item) for item in patch["warnings"]]
    elif clear_warnings:
        bundle["warnings"] = []

    bundle_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def candidate_update_from_bundle(bundle: dict[str, Any]) -> CandidateUpdate:
    update = bundle["candidate"]["candidate_update"]
    ingredients = [
        IngredientIn(
            position=int(ingredient["position"]),
            group_heading=ingredient.get("group_heading"),
            quantity=ingredient.get("quantity"),
            unit=ingredient.get("unit"),
            item=ingredient.get("item") or "",
            preparation=ingredient.get("preparation"),
            optional=bool(ingredient.get("optional", False)),
            display_text=ingredient.get("display_text"),
        )
        for ingredient in update.get("ingredients", [])
    ]
    steps = [
        StepIn(
            position=int(step["position"]),
            instruction=step.get("instruction") or "",
            time_note=step.get("time_note"),
            equipment_note=step.get("equipment_note"),
        )
        for step in update.get("steps", [])
    ]
    return CandidateUpdate(
        title=update.get("title"),
        short_description=update.get("short_description"),
        dish_role=update.get("dish_role"),
        primary_cuisine=update.get("primary_cuisine"),
        technique_family=update.get("technique_family"),
        complexity=update.get("complexity"),
        time_class=update.get("time_class"),
        servings=update.get("servings"),
        prep_time_minutes=update.get("prep_time_minutes"),
        cook_time_minutes=update.get("cook_time_minutes"),
        notes=update.get("notes"),
        service_notes=update.get("service_notes"),
        source_credit=update.get("source_credit"),
        ingredients=ingredients,
        steps=steps,
    )


def sync_candidate_extras(candidate, bundle: dict[str, Any]) -> None:
    extras = bundle.get("candidate", {}).get("candidate_extras", {})
    candidate.candidate_status = bundle.get("candidate", {}).get("candidate_status", "pending")
    candidate.service_format = extras.get("service_format")
    candidate.season = extras.get("season")
    candidate.secondary_cuisines = json.dumps(extras.get("secondary_cuisines", []), ensure_ascii=False)
    candidate.ingredient_families = json.dumps(extras.get("ingredient_families", []), ensure_ascii=False)
    candidate.mood_tags = json.dumps(extras.get("mood_tags", []), ensure_ascii=False)
    candidate.storage_profile = json.dumps(extras.get("storage_profile", []), ensure_ascii=False)
    candidate.dietary_flags = json.dumps(extras.get("dietary_flags", []), ensure_ascii=False)
    candidate.provision_tags = json.dumps(extras.get("provision_tags", []), ensure_ascii=False)
    candidate.sector = extras.get("sector")
    candidate.operational_class = extras.get("operational_class")
    candidate.heat_window = extras.get("heat_window")
    candidate.total_time_minutes = extras.get("total_time_minutes")
    candidate.rest_time_minutes = extras.get("rest_time_minutes")
    candidate.ai_payload_json = bundle.get("ai_metadata", {}).get("ai_payload_json")


def find_existing_job(db, snapshot_path: str) -> IntakeJob | None:
    statement = (
        select(IntakeJob)
        .where(IntakeJob.source_snapshot_path == snapshot_path)
        .order_by(IntakeJob.created_at.desc(), IntakeJob.id.desc())
    )
    return db.execute(statement).scalars().first()


def ingest_bundle(bundle_path: Path, *, force_new: bool) -> tuple[str, str]:
    bundle = load_bundle(bundle_path)
    snapshot_path = rel_path(bundle_path)
    source = bundle.get("source", {})

    init_db()
    with SessionLocal() as db:
        job = None if force_new else find_existing_job(db, snapshot_path)
        if job and job.status == "approved":
            raise ReviewFailure(
                f"Bundle already imported and approved under intake job {job.id}. Use --force-new to create a separate job."
            )

        if job is None:
            intake_type = "paste_text" if source.get("raw_source_text") else "file"
            create = IntakeJobCreate(
                intake_type=intake_type,
                raw_source_text=source.get("raw_source_text"),
                source_url=source.get("source_url"),
            )
            job = intake_service.create_intake_job(db, create)

        candidate = intake_service.update_candidate(db, job.id, candidate_update_from_bundle(bundle))
        if candidate is None:
            raise ReviewFailure(f"Failed to create candidate for intake job {job.id}")

        job.status = "structured"
        job.parse_status = "complete"
        job.ai_status = "ready" if bundle.get("ai_metadata", {}).get("provider") == "lm_studio" else "not_requested"
        job.review_status = "in_progress"
        job.raw_source_text = source.get("raw_source_text")
        job.source_url = source.get("source_url")
        job.source_snapshot_path = snapshot_path
        sync_candidate_extras(candidate, bundle)

        db.commit()
        return job.id, candidate.id


def approve_bundle(
    bundle_path: Path,
    *,
    force_new: bool,
    verification_state: str,
    source_type: str,
    source_title: str | None,
    source_author: str | None,
    source_notes: str | None,
    allow_review_flags: bool,
) -> tuple[str, str]:
    bundle = load_bundle(bundle_path)
    if bundle.get("review_flags") and not allow_review_flags:
        raise ReviewFailure(
            "Candidate has review_flags. Resolve them first or rerun with --allow-review-flags to force approval."
        )

    job_id, _ = ingest_bundle(bundle_path, force_new=force_new)

    init_db()
    with SessionLocal() as db:
        body = ApproveIntakeIn(
            verification_state=VerificationState(verification_state),
            source_type=SourceType(source_type),
            source_title=source_title,
            source_author=source_author,
            source_notes=source_notes,
        )
        recipe = intake_service.approve_intake_job(db, job_id, body)
        if recipe is None:
            raise ReviewFailure(f"Approval failed for intake job {job_id}")
        db.commit()
        return job_id, recipe.id


def main() -> int:
    args = parse_args()

    try:
        if args.command == "list":
            files = candidate_files(args.directory)
            if not files:
                print(f"No candidate bundles found in {args.directory}")
                return 0
            for path in files:
                print(summarize_bundle(path, load_bundle(path)))
            return 0

        if args.command == "show":
            print_bundle_details(args.bundle, load_bundle(args.bundle))
            return 0

        if args.command == "edit":
            apply_bundle_patch(
                args.bundle,
                args.patch,
                clear_review_flags=args.clear_review_flags,
                clear_warnings=args.clear_warnings,
            )
            print(f"Updated {rel_path(args.bundle)}")
            print(f"Patch: {rel_path(args.patch)}")
            return 0

        if args.command == "ingest":
            job_id, candidate_id = ingest_bundle(args.bundle, force_new=args.force_new)
            print(f"Ingested {rel_path(args.bundle)}")
            print(f"intake_job_id: {job_id}")
            print(f"candidate_id: {candidate_id}")
            return 0

        if args.command == "approve":
            job_id, recipe_id = approve_bundle(
                args.bundle,
                force_new=args.force_new,
                verification_state=args.verification_state,
                source_type=args.source_type,
                source_title=args.source_title,
                source_author=args.source_author,
                source_notes=args.source_notes,
                allow_review_flags=args.allow_review_flags,
            )
            print(f"Approved {rel_path(args.bundle)}")
            print(f"intake_job_id: {job_id}")
            print(f"recipe_id: {recipe_id}")
            return 0

        raise ReviewFailure(f"Unknown command: {args.command}")
    except ReviewFailure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
