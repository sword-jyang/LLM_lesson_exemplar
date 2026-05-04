"""
MkDocs hooks for LLM_lesson_exemplar.

on_pre_build: Copies harmonized_visualization.png from each project's output/
              directory into docs/assets/ so MkDocs can serve them.

on_nav:       Dynamically injects workflow pages or output image links into a
              "Workflows" nav section so mkdocs.yml never needs per-workflow
              edits.
"""

import shutil
from pathlib import Path

from mkdocs.structure.nav import Link, Section
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


def _workflow_title(project_name):
    return project_name.replace("_", " ").title()


def on_nav(nav, config, files):
    """Append workflow pages or output image links in a final Workflows section."""
    repo_root = Path(config["docs_dir"]).parent
    docs_dir = Path(config["docs_dir"])
    workflows_dir = docs_dir / "workflows"
    output_dirs = sorted((repo_root / "workflows").glob("*/output"))

    project_names = {
        p.stem for p in workflows_dir.glob("*.md") if workflows_dir.exists() and p.name != ".gitkeep"
    }
    project_names.update(output_dir.parent.name for output_dir in output_dirs)

    workflow_items = []
    for project_name in sorted(project_names):
        title = _workflow_title(project_name)
        rel_page = f"workflows/{project_name}.md"
        f = files.get_file_from_path(rel_page)
        if f is not None:
            workflow_items.append(Page(title, f, config))
            continue

        output_png = repo_root / "workflows" / project_name / "output" / "harmonized_visualization.png"
        if output_png.exists():
            workflow_items.append(
                Link(
                    title,
                    f"assets/workflows/{project_name}/harmonized_visualization.png",
                )
            )

    if not workflow_items:
        return nav

    workflows_section = Section("Workflows", workflow_items)

    # Keep Workflows as the final sidebar section and avoid duplicate injection.
    nav.items = [
        item for item in nav.items if getattr(item, "title", None) != "Workflows"
    ]
    nav.items.append(workflows_section)
    return nav
