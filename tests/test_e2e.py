"""End-to-end smoke tests against an installed jpq binary."""

import json
import subprocess

import pytest

pytestmark = pytest.mark.e2e


def _run(jpq_bin: str, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [jpq_bin, *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_version(jpq_bin: str) -> None:
    """`jpq --version` exits 0 and prints `jpq <version>`."""
    result = _run(jpq_bin, "--version")
    assert result.returncode == 0
    assert result.stdout.startswith("jpq "), result.stdout


def test_identity_default(jpq_bin: str) -> None:
    """Bare `jpq` with piped input echoes the parsed JSON back."""
    result = _run(jpq_bin, stdin='{"x": 1}')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"x": 1}


def test_basic_eval(jpq_bin: str) -> None:
    """A simple field access expression returns the field value as JSON."""
    result = _run(jpq_bin, 'this["name"]', stdin='{"name": "alice"}')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == "alice"


def test_compact_output(jpq_bin: str) -> None:
    """`-c` produces compact JSON with no whitespace separators."""
    result = _run(jpq_bin, "-c", stdin='{"a": 1, "b": 2}')
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == '{"a":1,"b":2}'


def test_invalid_json_exits_3(jpq_bin: str) -> None:
    """Malformed stdin yields exit code 3 (StdinError) and a `jpq:` prefixed stderr."""
    result = _run(jpq_bin, "this", stdin="not json")
    assert result.returncode == 3
    assert result.stderr.startswith("jpq:"), result.stderr
