from pathlib import Path
import re

VAULT = Path(r"C:\Obsidian\AMG-Vault")
DRY_RUN = False
  # set False after the count looks right

FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\s*\r?\n(.*?)\r?\n---", re.DOTALL)
ASTRO_LINE = re.compile(r'(?im)^[ \t]*-\s*"?\[\[Astrology\]\]"?\s*\r?\n')
DEF_LINE = re.compile(r'(?im)^[ \t]*-\s*"?definitions"?\s*\r?\n')

changed = 0
no_fm = 0

for path in VAULT.rglob("*.md"):
    if ".obsidian" in path.parts:
        continue

    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        no_fm += 1
        continue

    fm = m.group(1)
    new_fm, n1 = ASTRO_LINE.subn("", fm)
    new_fm, n2 = DEF_LINE.subn("", new_fm)
    if n1 == 0 and n2 == 0:
        continue

    print(f"{path}  Astrology={n1} definitions={n2}")
    if not DRY_RUN:
        path.write_text(
            f"---\n{new_fm.rstrip()}\n---" + text[m.end():],
            encoding="utf-8",
        )
    changed += 1

print("No frontmatter:", no_fm)
print(("Would change" if DRY_RUN else "Changed"), changed, "files")