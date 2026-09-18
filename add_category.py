"""
add_category.py
---------------
Purpose
    Walk an Obsidian vault and, for Markdown notes whose YAML frontmatter
    breadcrumb contains the word "Astrology", fill an empty categories:
    field with:

        categories:
          - "[[Astrology]]"

    Everything else in the note is left alone: title, source, tags, body,
    key order, and spacing.

Why text-edit instead of a YAML library
    Libraries like PyYAML rewrite the whole frontmatter block. That can
    change quotes, key order, and blank lines. This script only splices
    in one list item when it is safe to do so.

How to use
    1. Edit VAULT below if your folder changes.
    2. Keep DRY_RUN = True and run the script. It prints paths it WOULD
       change but does not write files.
    3. Check that list. If it looks right, set DRY_RUN = False and run
       again to write the changes.
    4. Set DRY_RUN back to True when you are done.

Run from Command Prompt or PowerShell:
    python "C:\\Obsidian\\media\\python\\add_category.py"
    or:
    py "C:\\Obsidian\\media\\python\\add_category.py"
"""

from pathlib import Path
import re

# Folder that contains the notes to scan (your test vault).
# r"..." is a raw string so Windows backslashes are not treated as escapes.
# Quotes are required because the folder name has a space.
VAULT = Path(r"C:\Obsidian\Astrology test")

# True  = preview only (print files, write nothing)
# False = actually update the files on disk
DRY_RUN = True

# The exact YAML list item to insert under categories:
CATEGORY_ITEM = '  - "[[Astrology]]"'

# Match YAML frontmatter at the very start of a file:
# ---
# ...keys...
# ---
# \A     = start of the file
# \r?\n  = Windows (CRLF) or Unix (LF) line endings
# DOTALL = let "." match newlines so the middle group can span lines
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)


def update_frontmatter(fm: str) -> str | None:
    """
    Look at the text BETWEEN the --- markers.
    Return the updated frontmatter text, or None if this file
    should be skipped.
    """

    # Rule 1: breadcrumb (or any frontmatter text) must mention Astrology.
    # This is a simple substring check, same idea as "contains the word".
    if "Astrology" not in fm:
        return None

    # Rule 2: there should be a breadcrumb: key. (?im) = ignore case, multiline
    # so "breadcrumb:" at the start of a line matches.
    if not re.search(r"(?im)^breadcrumb:", fm):
        return None

    # Rule 3: do not add a duplicate if [[Astrology]] is already present.
    if "[[Astrology]]" in fm:
        return None

    # Rule 4: only touch an EMPTY categories field.
    # Matches either:
    #   categories:
    # or
    #   categories: []
    # and nothing after that on the same line.
    m = re.search(r"(?m)^(categories:\s*)(?:\[\s*\]\s*)?$", fm)
    if not m:
        return None

    # Splice the new list item in right after the categories: line.
    # fm[:end] is everything through "categories:"
    # fm[end:] is whatever follows (usually a newline then tags:)
    start, end = m.span()
    return fm[:end] + "\n" + CATEGORY_ITEM + fm[end:]


def main() -> None:
    changed = 0

    # rglob("*.md") finds .md files in this folder and all subfolders.
    for path in VAULT.rglob("*.md"):
        # Skip Obsidian's own settings folder if this vault has one.
        if ".obsidian" in path.parts:
            continue

        # Read the whole note as UTF-8 text (normal for Markdown).
        text = path.read_text(encoding="utf-8")

        # Does this file even have frontmatter?
        m = FM_RE.match(text)
        if not m:
            continue

        # m.group(1) is the YAML between the --- lines.
        new_fm = update_frontmatter(m.group(1))
        if new_fm is None:
            continue

        # Rebuild the file: same prefix/suffix, only the YAML middle changes.
        new_text = text[: m.start(1)] + new_fm + text[m.end(1) :]

        print(path)

        if not DRY_RUN:
            path.write_text(new_text, encoding="utf-8")

        changed += 1

    action = "Would update" if DRY_RUN else "Updated"
    print(f"{action} {changed} files")


# This runs main() only when you execute the file directly,
# not if some other script imports it.
if __name__ == "__main__":
    main()
    