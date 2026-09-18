"""
combine_notes.py
----------------
Combines every .md file in ONE folder into a single all_notes.md.

How this path logic works
    __file__                 = this script's filename
    Path(__file__).resolve() = full path to this script
    .parent                  = the folder that CONTAINS this script

    If the script lives here:
        C:\\Obsidian\\Astrology test\\combine_notes.py

    then NOTES_DIR becomes:
        C:\\Obsidian\\Astrology test

    That is the folder whose .md files get merged.

What went wrong before
    The old line was:

        NOTES_DIR = Path(__file__).resolve().parent / "obsidian_notes"

    The "/ 'obsidian_notes'" part means "look in a SUBFOLDER named
    obsidian_notes". If you drop the script into the notes folder
    itself, that subfolder does not exist, so it finds 0 files.

How to use
    1. Copy this .py file into the folder that already has the .md notes.
    2. In VS Code or Command Prompt, run:

           python combine_notes.py

       or:

           py combine_notes.py

    3. It writes all_notes.md in that same folder.

    Do not point it at a different folder by moving only the notes.
    Move the script INTO the folder you want to combine, or change
    NOTES_DIR below.
"""

from pathlib import Path

# Folder to scan = the folder this script is sitting in.
# Change this ONLY if the notes live somewhere else, for example:
#   NOTES_DIR = Path(r"C:\Obsidian\Astrology test")
NOTES_DIR = Path(__file__).resolve().parent

# Combined output is written next to the script.
OUT_FILE = NOTES_DIR / "all_notes.md"

# *.md in THIS folder only (not subfolders).
# Use rglob("*.md") instead of glob if you also want nested folders.
files = sorted(
    path
    for path in NOTES_DIR.glob("*.md")
    if path.name.lower() != OUT_FILE.name.lower()  # do not include a previous output
)

print("Looking in:", NOTES_DIR)
print("Notes found:", len(files))

if not files:
    print("No .md files found in that folder.")
    print("Put this script in the folder with the notes, or set NOTES_DIR to that folder.")
    raise SystemExit(1)

parts = []
for file in files:
    text = file.read_text(encoding="utf-8", errors="replace").strip()
    parts.append(
        "\n\n---\n\n"
        + "# File: " + file.name + "\n\n"
        + text
    )

OUT_FILE.write_text("".join(parts).strip() + "\n", encoding="utf-8")
print("Wrote", OUT_FILE)
print("Characters:", OUT_FILE.stat().st_size)