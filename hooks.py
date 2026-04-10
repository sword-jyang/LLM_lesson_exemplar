"""
MkDocs hooks for LLM_lesson_exemplar.

on_pre_build: Copies harmonized_visualization.png from each project's output/
              directory into docs/assets/ so MkDocs can serve them.

on_nav:       Dynamically injects docs/workflows/*.md pages into a "Workflows"
              nav section so mkdocs.yml never needs per-workflow edits.
"""

import shutil
from pathlib import Path

from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page


def on_pre_build(config):
    """Copy PNGs from examples/*/output/ and workflows/*/output/ into docs/assets/."""
    repo_root = Path(config["docs_dir"]).parent
    docs_assets = repo_root / "docs" / "assets"

    for kind in ("examples", "workflows"):
        source_root = repo_root / kind
        if not source_root.exists():
            continue
        for output_dir in source_root.glob("*/output"):
            png = output_dir / "harmonized_visualization.png"
            if not png.exists():
                continue
            project_name = output_dir.parent.name
            dest_dir = docs_assets / kind / project_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(png, dest_dir / "harmonized_visualization.png")


def on_nav(nav, config, files):
    """Inject docs/workflows/*.md pages into a Workflows section in the nav."""
    docs_dir = Path(config["docs_dir"])
    workflows_dir = docs_dir / "workflows"
    if not workflows_dir.exists():
        return nav

    workflow_pages = sorted(
        p for p in workflows_dir.glob("*.md") if p.name != ".gitkeep"
    )
    if not workflow_pages:
        return nav

    workflow_items = []
    for page_path in workflow_pages:
        rel_path = f"workflows/{page_path.name}"
        f = files.get_file_from_path(rel_path)
        if f is None:
            continue
        title = page_path.stem.replace("_", " ").title()
        workflow_items.append(Page(title, f, config))

    if not workflow_items:
        return nav

    workflows_section = Section("Workflows", workflow_items)

    # Insert Workflows before the last section (Reference)
    new_items = list(nav.items)
    new_items.insert(-1, workflows_section)
    nav.items = new_items
    return nav
