from __future__ import annotations

import importlib
from pathlib import Path
import tomllib


def test_api_build_backend_is_importable() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "apps" / "api" / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    backend = data["build-system"]["build-backend"]

    module_name, _, object_path = backend.partition(":")
    module = importlib.import_module(module_name)

    current = module
    if object_path:
        for part in object_path.split("."):
            current = getattr(current, part)

    assert current is not None
