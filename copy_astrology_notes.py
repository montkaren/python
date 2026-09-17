# copy_astrology_notes.py
#
# What this script does:
# 1. Reads every .md file in C:\Obsidian\vault\AMG-Vault
# 2. Checks whether "Astrology" appears in that note's breadcrumb
# 3. Copies matching notes into C:\Obsidian\media\python\AMG Astrology
# 4. Does not rename, move, or edit the original files
#
# You can move the "AMG Astrology" folder wherever you want afterward.

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
# import loads tools that come with Python.
# re      = regular expressions; used to search inside text
# shutil  = file helpers; shutil.copy2 copies a file
# Path    = a cleaner way to work with folders and filenames
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# r"C:\..." is a raw string. The r matters on Windows.
# Without r, Python treats \ as a special escape character.
#
# Path(...) turns the string into a path object so we can
# join folders with / and test whether they exist.
SOURCE = Path(r"C:\Obsidian\vault\AMG-Vault")

# Path(__file__) is this .py file.
# .resolve() makes it a full path.
# .parent is the folder that contains this script:
# C:\Obsidian\media\python
SCRIPT_DIR = Path(__file__).resolve().parent

# / on a Path means "add this name onto the path".
# Result: C:\Obsidian\media\python\AMG Astrology
DEST = SCRIPT_DIR / "AMG Astrology"


def has_astrology_breadcrumb(text):
    """
    Return True if this note should be copied.

    A function is a reusable block of code.
    text is one whole .md file loaded as a string.
    """

    # re.search looks through text for a pattern.
    # ^                 start of a line
    # breadcrumb:       the YAML field from the converter
    # \s*               optional spaces
    # [\"']?            optional quote character
    # (.*)              capture the rest of the line
    # re.IGNORECASE     "Astrology" and "astrology" both count
    # re.MULTILINE      ^ matches every line, not just line 1
    match = re.search(
        r"^breadcrumb:\s*[\"']?(.*)[\"']?\s*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )

    # match is None if that line was not found.
    # match.group(1) is the captured breadcrumb text.
    # .lower() makes the check case-insensitive.
    if match and "astrology" in match.group(1).lower():
        return True

    # Some notes also have a visible line like:
    # **Path:** [Astrology](astrology-2.md) > Houses
    if re.search(r"^\*\*Path:\*\*.*astrology", text, re.IGNORECASE | re.MULTILINE):
        return True

    # If neither check found Astrology, skip this file.
    return False


# ---------------------------------------------------------------------------
# Main program
# Code outside a function runs as soon as you start the script.
# ---------------------------------------------------------------------------
print("Reading original notes from:")
print(" ", SOURCE)
print("Writing copies to:")
print(" ", DEST)

# .exists() is True only if that folder is really on the computer.
if not SOURCE.exists():
    print("ERROR: the source folder does not exist.")
    print("Open File Explorer and confirm this path is correct:")
    print(" ", SOURCE)
else:
    # mkdir creates DEST if it is missing.
    # exist_ok=True means "don't crash if the folder already exists".
    DEST.mkdir(exist_ok=True)

    # glob("*.md") means "all files ending in .md in this one folder".
    # It does not look inside subfolders.
    # sorted(...) puts the filenames in A-Z order.
    files = sorted(SOURCE.glob("*.md"))
    print("Markdown files found:", len(files))

    # copied is a counter. Start at 0, add 1 each time we copy a file.
    copied = 0

    # This loop runs once for each .md file.
    # file is a Path object for that one note.
    for file in files:
        # read_text() loads the file into a string.
        # encoding="utf-8" handles ordinary English plus special characters.
        # errors="replace" keeps going if one odd character is found.
        text = file.read_text(encoding="utf-8", errors="replace")

        if has_astrology_breadcrumb(text):
            # DEST / file.name = destination folder + same filename.
            # Example: AMG Astrology\antiscia.md
            #
            # copy2 copies the file and keeps the original date.
            # The vault file is left exactly as it was.
            shutil.copy2(file, DEST / file.name)
            print("Copied", file.name)
            copied += 1
        else:
            print("Skip", file.name)

    print("Done.")
    print(copied, "of", len(files), "files copied.")
    print("Originals were not changed.")