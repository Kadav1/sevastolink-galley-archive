from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .constants import DEFAULT_REPORT_DIR, REPORT_TYPE, SCHEMA_VERSION
from .models import FileResult, RunReport, RunSummary


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_run_label(started_at: datetime | None = None) -> str:
    ts = started_at or datetime.now(timezone.utc)
    return f"recipe-normalization-run-{ts.strftime('%Y%m%d-%H%M%S')}"


def build_report_path(report_dir: Path | None, run_label: str) -> Path:
    base = report_dir or DEFAULT_REPORT_DIR
    return base / f"{run_label}.json"


def finalize_report(report: RunReport) -> RunReport:
    successful = sum(1 for result in report.results if result.status == "success")
    failed = len(report.results) - successful
    warning_count = sum(result.warning_count for result in report.results)
    review_flag_count = sum(result.review_flag_count for result in report.results)
    report.summary = RunSummary(
        selected_files=len(report.selected_sources),
        successful_files=successful,
        failed_files=failed,
        emitted_candidates=successful,
        total_warnings=warning_count,
        total_review_flags=review_flag_count,
    )
    report.status = "success" if failed == 0 else ("failure" if successful == 0 else "partial_failure")
    return report


def create_report(*, output_dir: Path, report_path: Path, selected_sources: list[Path], run_label: str, started_at: str) -> RunReport:
    return RunReport(
        report_type=REPORT_TYPE,
        schema_version=SCHEMA_VERSION,
        run_label=run_label,
        started_at=started_at,
        completed_at=started_at,
        status="running",
        output_dir=str(output_dir),
        report_path=str(report_path),
        selected_sources=[str(path) for path in selected_sources],
    )


def write_report(report: RunReport) -> Path:
    path = Path(report.report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=True), encoding="utf-8")
    return path


def success_result(*, source_path: Path, stage: str, output_path: Path, warning_count: int, review_flag_count: int, duration_ms: int) -> FileResult:
    return FileResult(
        source_path=str(source_path),
        status="success",
        stage=stage,
        output_path=str(output_path),
        warning_count=warning_count,
        review_flag_count=review_flag_count,
        duration_ms=duration_ms,
    )


def failure_result(*, source_path: Path, stage: str, error: str, duration_ms: int | None) -> FileResult:
    return FileResult(
        source_path=str(source_path),
        status="failure",
        stage=stage,
        error=error,
        duration_ms=duration_ms,
    )
