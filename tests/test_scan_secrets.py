from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "dev" / "scan_secrets.sh"


def run_scan(repo_path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GALLEY_SECRET_SCAN_ROOT"] = str(repo_path)
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
        check=False,
    )


def test_secret_scan_passes_for_safe_tree(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("LM_STUDIO_ENABLED=false\n", encoding="utf-8")

    result = run_scan(tmp_path)

    assert result.returncode == 0
    assert "No high-confidence secret patterns found." in result.stdout


def test_secret_scan_fails_for_private_key_material(tmp_path: Path) -> None:
    private_key_header = "-----BEGIN " + "OPENSSH PRIVATE KEY-----\n"
    (tmp_path / "bad.pem").write_text(
        private_key_header + "fake\n",
        encoding="utf-8",
    )

    result = run_scan(tmp_path)

    assert result.returncode == 1
    assert "Potential secrets detected." in result.stdout
    assert "bad.pem" in result.stdout


def test_secret_scan_fails_for_assignment_style_secret(tmp_path: Path) -> None:
    secret_assignment = "API" + "_KEY=supersecretvalue123456\n"
    (tmp_path / ".env.production").write_text(
        secret_assignment,
        encoding="utf-8",
    )

    result = run_scan(tmp_path)

    assert result.returncode == 1
    assert "Potential secrets detected." in result.stdout
    assert ".env.production" in result.stdout
