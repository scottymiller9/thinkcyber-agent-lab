"""Findings store + report writer.

The agent calls note_finding() as it confirms issues, then generate_report()
at the end. This produces the Part-2 deliverable: a pen-test report with
severity, evidence, and steps to reproduce.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime

from . import config

_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


@dataclass
class Finding:
    title: str
    severity: str
    description: str
    evidence: str = ""
    repro_steps: str = ""


@dataclass
class FindingStore:
    items: list[Finding] = field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def add(self, title, severity, description, evidence="", repro_steps=""):
        self.items.append(Finding(title, severity, description, evidence, repro_steps))

    def to_markdown(self) -> str:
        ordered = sorted(self.items, key=lambda f: _SEV_ORDER.get(f.severity, 9))
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# Penetration Test Report",
            f"**Target:** {config.TARGET_URL}  ",
            f"**Date:** {now}  ",
            f"**Tool:** agentic-pentest-lab (workshop demo agent)",
            "",
            "## Summary of Findings",
            "",
            "| # | Severity | Finding |",
            "|---|----------|---------|",
        ]
        for i, f in enumerate(ordered, 1):
            lines.append(f"| {i} | {f.severity.upper()} | {f.title} |")
        lines += ["", "## Details", ""]
        for i, f in enumerate(ordered, 1):
            lines += [
                f"### {i}. {f.title}  —  {f.severity.upper()}",
                "",
                f.description,
                "",
            ]
            if f.evidence:
                lines += ["**Evidence**", "", "```", f.evidence.strip(), "```", ""]
            if f.repro_steps:
                lines += ["**Steps to reproduce**", "", f.repro_steps.strip(), ""]
        if not ordered:
            lines.append("_No findings were recorded._")
        return "\n".join(lines)

    def save(self) -> str:
        os.makedirs(config.REPORT_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(config.REPORT_DIR, f"report-{stamp}.md")
        with open(path, "w") as fh:
            fh.write(self.to_markdown())
        return path


# One shared store per run.
FINDINGS = FindingStore()
