"""Shared pytest fixtures for the jpq test suite."""

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def jpq_bin(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Build the wheel and install jpq into a throwaway venv.

    Returns the absolute path to the venv's `jpq` executable. The build
    output goes to a temp directory, not the project's `dist/`, so the
    repo stays clean and the user's globally installed `jpq` (if any)
    is left untouched.
    """
    out_dir = tmp_path_factory.mktemp("jpq-dist")
    subprocess.run(
        ["uv", "build", "--out-dir", str(out_dir)],
        cwd=PROJECT_ROOT,
        check=True,
    )
    wheels = list(out_dir.glob("jpq-*-py3-none-any.whl"))
    assert len(wheels) == 1, f"expected exactly one wheel, found: {wheels}"

    venv = tmp_path_factory.mktemp("jpq-venv") / ".venv"
    subprocess.run(["uv", "venv", str(venv)], check=True)
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(venv / "bin" / "python"),
            str(wheels[0]),
        ],
        check=True,
    )
    return str(venv / "bin" / "jpq")
