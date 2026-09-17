from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent / "obsidian_notes"
OUT_FILE = Path(__file__).resolve().parent / "all_notes.md"

files = sorted(NOTES_DIR.glob("*.md"))
print("Notes found:", len(files))

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