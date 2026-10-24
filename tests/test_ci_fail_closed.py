"""Regression tests for a fail-closed GitHub Actions quality workflow."""

import re
from pathlib import Path
from typing import Any

import yaml

WORKFLOW = Path(".github/workflows/ci.yml")
ALLOWED_QUALITY_COMMANDS = {
    "lint": {"ruff check .", "python -m ruff check ."},
    "test": {"pytest -q", "python -m pytest -q"},
}
QUALITY_COMMAND_PATTERNS = {
    "lint": re.compile(r"(?:^|(?:&&|;)\s*)(?:python\s+-m\s+)?ruff\s+check(?:\s|$)"),
    "test": re.compile(r"(?:^|(?:&&|;)\s*)(?:python\s+-m\s+)?pytest(?:\s|$)"),
}


def _enabled(value: object) -> bool:
    return not (
        value is None
        or value is False
        or (isinstance(value, str) and value.strip().lower() == "false")
    )


def _load_workflow() -> dict[str, Any]:
    document = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(document, dict), "CI workflow must parse to a YAML mapping"
    return document


def test_quality_commands_are_executable_steps_and_fail_closed() -> None:
    workflow = _load_workflow()
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict) and jobs, "CI must define at least one job"

    observed: dict[str, list[str]] = {"lint": [], "test": []}
    quality_jobs: set[str] = set()

    for job_name, job in jobs.items():
        assert isinstance(job, dict), f"jobs.{job_name} must be a mapping"
        assert not _enabled(job.get("continue-on-error")), (
            f"jobs.{job_name} must not suppress job failures"
        )
        steps = job.get("steps") or []
        assert isinstance(steps, list), f"jobs.{job_name}.steps must be a list"

        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            assert not _enabled(step.get("continue-on-error")), (
                f"jobs.{job_name}.steps[{index}] must not suppress failures"
            )
            run = step.get("run")
            if not isinstance(run, str):
                continue

            assert "||" not in run, (
                f"jobs.{job_name}.steps[{index}] must not mask shell failures"
            )
            for raw_line in run.splitlines():
                command = " ".join(raw_line.split())
                if not command:
                    continue
                for gate_name, pattern in QUALITY_COMMAND_PATTERNS.items():
                    if not pattern.search(command):
                        continue
                    assert command in ALLOWED_QUALITY_COMMANDS[gate_name], (
                        f"{gate_name} must run as a standalone fail-closed command; "
                        f"found {command!r}"
                    )
                    allowed_conditions = {"", "success()", "${{ success() }}"}
                    step_condition = str(step.get("if") or "").strip().lower()
                    job_condition = str(job.get("if") or "").strip().lower()
                    assert step_condition in allowed_conditions, (
                        f"{gate_name} step has a condition that can skip the gate: "
                        f"{step_condition!r}"
                    )
                    assert job_condition in allowed_conditions, (
                        f"job {job_name} has a condition that can skip {gate_name}: "
                        f"{job_condition!r}"
                    )
                    observed[gate_name].append(job_name)
                    quality_jobs.add(job_name)

    for gate_name, job_names in observed.items():
        assert len(job_names) == 1, (
            f"expected exactly one executable {gate_name} command; found {job_names}"
        )

    # If a separate final gate is introduced, it must depend on every required
    # lint/test job, and the final gate itself cannot suppress failures.
    gate = jobs.get("gate")
    if isinstance(gate, dict):
        assert not _enabled(gate.get("continue-on-error")), (
            "the final gate job must not suppress failures"
        )
        needs = gate.get("needs") or []
        if isinstance(needs, str):
            needs = [needs]
        assert isinstance(needs, list), "jobs.gate.needs must be a list or string"
        assert quality_jobs <= set(needs), (
            f"jobs.gate.needs must include all quality jobs: {sorted(quality_jobs)}"
        )
