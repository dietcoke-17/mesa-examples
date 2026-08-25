#!/usr/bin/env python3
#
# Sphinx configuration for the mesa-examples documentation.
#
# This site auto-discovers every example under examples/, gis/, and rl/ at the
# repo root and builds a page per example (from that example's own README) plus
# an overview page per category. Nothing here is hand-maintained: add or remove
# an example folder and the docs pick it up on the next build.

import os
import os.path as osp
from datetime import date

HERE = osp.abspath(osp.dirname(__file__))
REPO_ROOT = osp.abspath(osp.join(HERE, ".."))

# -- General configuration ------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

exclude_patterns = ["_build"]

master_doc = "index"

project = "Mesa Examples"
copyright = f"2015-{date.today().year}, Mesa Team"

# -- Options for HTML output ----------------------------------------------

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "navbar_start": ["navbar-logo"],
}
html_show_sphinx = False


# -- Auto-discovery of example pages ---------------------------------------

CATEGORIES = ["examples", "gis", "rl"]


def find_readme(example_dir):
    """Case-insensitively find a readme.md file directly inside example_dir."""
    try:
        entries = os.scandir(example_dir)
    except OSError:
        return None
    for entry in entries:
        if entry.is_file() and entry.name.lower() == "readme.md":
            return entry.path
    return None


def find_examples(category_dir):
    """Immediate subdirectories of category_dir that have a readme, sorted by name."""
    found = []
    try:
        entries = os.scandir(category_dir)
    except OSError:
        return found
    for entry in entries:
        if not entry.is_dir() or entry.name.startswith((".", "_")):
            continue
        readme_path = find_readme(entry.path)
        if readme_path:
            found.append((entry.name, readme_path))
    found.sort(key=lambda pair: pair[0])
    return found


def _is_setext_underline(stripped):
    """A Setext heading underline, e.g. '===' or '---' below a title line."""
    return bool(stripped) and (set(stripped) == {"="} or set(stripped) == {"-"})


def first_paragraph(readme_path):
    """First non-heading, non-blank paragraph of a readme, for a one-line blurb."""
    with open(readme_path, encoding="utf-8") as fh:
        text = fh.read()

    paragraph_lines = []
    started = False
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        next_stripped = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if not started:
            if (
                not stripped
                or stripped.startswith(("#", "![", "[!["))
                or _is_setext_underline(stripped)
                or _is_setext_underline(next_stripped)
            ):
                continue
            started = True
        if not stripped or stripped.startswith("#") or _is_setext_underline(stripped):
            break
        paragraph_lines.append(stripped)
    return " ".join(paragraph_lines)


def display_name(example_name):
    return " ".join(word.capitalize() for word in example_name.split("_"))


def write_example_page(category, example_name, readme_path):
    out_dir = osp.join(HERE, category)
    os.makedirs(out_dir, exist_ok=True)
    out_path = osp.join(out_dir, f"{example_name}.md")

    rel_readme = osp.relpath(readme_path, start=out_dir).replace(os.sep, "/")
    rel_dir = osp.relpath(osp.dirname(readme_path), start=out_dir).replace(
        os.sep, "/"
    )

    content = (
        f"# {display_name(example_name)}\n\n"
        f"```{{include}} {rel_readme}\n"
        f":relative-images:\n"
        f":relative-docs: {rel_dir}/\n"
        f"```\n"
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(content)


def write_category_page(category, examples):
    title = display_name(category) if category != "gis" else "GIS Examples"
    if category == "rl":
        title = "RL Examples"

    lines = [f"# {title}", ""]
    for name, readme_path in examples:
        blurb = first_paragraph(readme_path)
        lines.append(f"## [{display_name(name)}]({category}/{name}.md)")
        lines.append("")
        if blurb:
            lines.append(blurb)
            lines.append("")

    lines.append("```{toctree}")
    lines.append(":maxdepth: 1")
    lines.append(":hidden:")
    lines.append("")
    for name, _ in examples:
        lines.append(f"{category}/{name}")
    lines.append("```")
    lines.append("")

    out_path = osp.join(HERE, f"{category}.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def setup_examples_pages():
    for category in CATEGORIES:
        category_dir = osp.join(REPO_ROOT, category)
        examples = find_examples(category_dir)
        for name, readme_path in examples:
            write_example_page(category, name, readme_path)
        write_category_page(category, examples)


def setup(app):
    setup_examples_pages()


if __name__ == "__main__":
    setup_examples_pages()
