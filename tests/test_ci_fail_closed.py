from pathlib import Path


def test_ci_fails_closed_on_quality_gate_errors() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "|| true" not in workflow
    assert "|| echo" not in workflow
    assert "ruff check ." in workflow
    assert "pytest -q" in workflow
