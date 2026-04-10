"""Lint test — ensure no placeholder text remains in committed workflow doc pages."""

import re
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / "docs" / "workflows"

# Matches angle-bracket placeholders like <PROJECT_NAME> or <TARGET_CRS>
PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z_\s]{2,}>")


def test_no_placeholder_text_in_workflow_docs():
    pages = [p for p in WORKFLOWS_DIR.glob("*.md") if p.name != ".gitkeep"]
    violations = []
    for page in pages:
        text = page.read_text()
        for match in PLACEHOLDER_RE.finditer(text):
            violations.append(f"  {page.name}: '{match.group()}'")
    assert not violations, (
        "Placeholder text found in workflow docs — LLM did not fill in all fields:\n"
        + "\n".join(violations)
    )


def test_workflow_docs_have_required_sections():
    """Every workflow doc should have Prompt, Datasets, and Result sections."""
    pages = [p for p in WORKFLOWS_DIR.glob("*.md") if p.name != ".gitkeep"]
    for page in pages:
        text = page.read_text()
        assert "## Prompt" in text, f"{page.name}: missing '## Prompt' section"
        assert "## Datasets" in text, f"{page.name}: missing '## Datasets' section"
        assert "## Result" in text, f"{page.name}: missing '## Result' section"
