from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent
OUT_FILE = NOTES_DIR / "all_notes.md"

files = sorted(
    path
    for path in NOTES_DIR.rglob("*.md")
    if path.resolve() != OUT_FILE.resolve()
)

print("Looking in:", NOTES_DIR)
print("Including child folders: yes (rglob)")
print("Notes found:", len(files))
for path in files:
    print(" ", path.relative_to(NOTES_DIR))

if not files:
    print("No .md files found.")
    raise SystemExit(1)

parts = []
for file in files:
    text = file.read_text(encoding="utf-8", errors="replace").strip()
    rel = file.relative_to(NOTES_DIR).as_posix()
    parts.append(
        "\n\n---\n\n"
        + "# File: " + rel + "\n\n"
        + text
    )

OUT_FILE.write_text("".join(parts).strip() + "\n", encoding="utf-8")
print("Wrote", OUT_FILE)
print("Characters:", OUT_FILE.stat().st_size)