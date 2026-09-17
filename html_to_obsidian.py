import re
from pathlib import Path
from urllib.parse import urlparse, unquote

FOLDER = Path(__file__).resolve().parent
OUT_DIR = FOLDER / "obsidian_notes"

START_MARK = r"<!--\s*Enter your text below this line\s*-->"
END_MARK = r"<!--\s*Enter your text above this line\s*-->"
SKIP_HREFS = {"#@toc", "#@related", "#"}

CONSTRUCTION_RE = re.compile(
    r"Page Under Construction\s*"
    r"Each of the pages in the Academie begins with research\.\s*"
    r"We first collect information from various sources that is then woven into an accurate and thorough account of the topic\.\s*"
    r"This page is still in the Note Taking Stage\.\s*"
    r"Feel free to add any relevant content\.?",
    re.IGNORECASE,
)


def first_caps(text):
    words = []
    for word in text.split():
        words.append(word[:1].upper() + word[1:] if word else word)
    return " ".join(words)


def decode_entities(text):
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&rsquo;", "'")
    text = text.replace("&lsquo;", "'")
    text = text.replace("&#39;", "'")
    text = text.replace("&apos;", "'")
    text = text.replace("&iquest;", "")
    text = re.sub(r"&#\d+;", " ", text)
    text = text.replace("&gt;", ">")
    text = text.replace("&lt;", "<")
    return text


def strip_images(html):
    html = re.sub(r"<img\b[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(
        r'<a\b[^>]*href=["\'][^"\']*images/[^"\']+["\'][^>]*>.*?</a>',
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def strip_edit_links(html):
    html = re.sub(
        r'<a\b[^>]*href=["\'][^"\']*/edit/[^"\']*["\'][^>]*>.*?</a>',
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def is_internal_page_link(href):
    if not href:
        return False
    href = href.strip()
    if href.lower() in SKIP_HREFS or href.startswith("#@"):
        return False
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", "mailto", "ftp"}:
        return False
    if "images/" in href.replace("\\", "/").lower():
        return False
    path = unquote(parsed.path)
    return path.lower().endswith((".html", ".htm")) or (
        path == "" and href.startswith("#")
    )


def html_href_to_obsidian(href):
    href = href.strip()
    parsed = urlparse(href)
    path = unquote(parsed.path)
    if path.lower().endswith(".html"):
        path = path[:-5] + ".md"
    elif path.lower().endswith(".htm"):
        path = path[:-4] + ".md"
    anchor = ""
    if parsed.fragment and not parsed.fragment.startswith("@"):
        anchor = "#" + parsed.fragment
    return path + anchor


def convert_links(html):
    def repl(match):
        href = match.group(1) or ""
        text = match.group(2) or ""
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not is_internal_page_link(href):
            return text
        target = html_href_to_obsidian(href)
        if not target:
            return text
        if not text:
            text = Path(target).stem.replace("_", " ")
        return "[" + text + "](" + target + ")"

    return re.sub(
        r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        repl,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def clean_cell(html):
    html = strip_edit_links(html)
    html = convert_links(html)
    html = re.sub(r"<br\s*/?>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", "", html)
    html = decode_entities(html)
    html = html.replace("|", "\\|")
    html = re.sub(r"\s+", " ", html).strip()
    return html


def table_to_markdown(table_html):
    rows = re.split(r"<tr\b[^>]*>", table_html, flags=re.IGNORECASE)
    md_rows = []
    for row in rows[1:]:
        cells = re.findall(
            r"<t[hd]\b[^>]*>(.*?)(?=<t[hd]\b|<tr\b|</tr\b|</table\b|$)",
            row,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not cells:
            continue
        md_rows.append([clean_cell(cell) for cell in cells])
    if not md_rows:
        return "\n\n"
    width = max(len(row) for row in md_rows)
    for row in md_rows:
        while len(row) < width:
            row.append("")
    lines = []
    lines.append("| " + " | ".join(md_rows[0]) + " |")
    lines.append("| " + " | ".join(["---"] * width) + " |")
    for row in md_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n\n" + "\n".join(lines) + "\n\n"


def convert_tables(html):
    return re.sub(
        r"<table\b[^>]*>.*?</table>",
        lambda m: table_to_markdown(m.group(0)),
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def heading_to_md(html, tag, hashes):
    def repl(match):
        text = re.sub(r"<[^>]+>", "", match.group(1))
        text = decode_entities(text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return ""
        return "\n\n" + hashes + " " + text + "\n\n"

    return re.sub(
        r"<" + tag + r"[^>]*>(.*?)</" + tag + r">",
        repl,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def html_to_markdown_text(html):
    html = strip_images(html)
    html = strip_edit_links(html)
    html = convert_tables(html)
    html = convert_links(html)
    html = heading_to_md(html, "h1", "#")
    html = heading_to_md(html, "h2", "##")
    html = heading_to_md(html, "h3", "###")
    html = heading_to_md(html, "h4", "####")
    html = heading_to_md(html, "h5", "#####")
    html = heading_to_md(html, "h6", "######")
    html = re.sub(r"<hr\s*/?>", "\n\n---\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p\s*>", "\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<p\b[^>]*>", "\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<li\b[^>]*>", "\n- ", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", "", html)
    html = decode_entities(html)
    html = re.sub(r"[ \t]+\n", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r"[ \t]{2,}", " ", html)
    return html.strip()


def remove_construction_note(text):
    text = CONSTRUCTION_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_title(content, fallback):
    match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if match:
        raw = re.sub(
            r"\s*-\s*Aux Mailles Godefroy\s*$",
            "",
            match.group(1).strip(),
            flags=re.IGNORECASE,
        )
        return first_caps(raw)
    return first_caps(fallback)


def extract_body(content):
    match = re.search(START_MARK + r"(.*?)" + END_MARK, content, re.IGNORECASE | re.DOTALL)
    if match:
        raw = match.group(1)
    else:
        start = 0
        qv = re.search(
            r"<div[^>]*class\s*=\s*['\"]?qvviki['\"]?[^>]*>",
            content,
            re.IGNORECASE,
        )
        if qv:
            start = qv.end()

        title_div = re.search(
            r"<div[^>]*class\s*=\s*['\"]?title['\"]?[^>]*>.*?</div>",
            content[start:],
            re.IGNORECASE | re.DOTALL,
        )
        if title_div:
            start = start + title_div.end()

        end_match = re.search(
            r"<strong[^>]*id\s*=\s*['\"]@related['\"]",
            content[start:],
            re.IGNORECASE,
        )
        if end_match:
            raw = content[start:start + end_match.start()]
        else:
            raw = content[start:]
            print("  warning: no comment markers and no related-pages footer")

        raw = re.sub(
            r"<div[^>]*id\s*=\s*['\"]@toc['\"][^>]*>.*?</ol>.*?</div>",
            "",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )

    return remove_construction_note(html_to_markdown_text(raw))


def extract_breadcrumb(content):
    block = re.search(
        r"<div[^>]*class\s*=\s*['\"]?path['\"]?[^>]*>.*?</div>",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    search_in = block.group(0) if block else content
    pres = re.findall(
        r"<pre[^>]*class\s*=\s*['\"]?path['\"]?[^>]*>(.*?)</pre>",
        search_in,
        re.IGNORECASE | re.DOTALL,
    )
    for pre in pres:
        text = html_to_markdown_text(pre)
        if text:
            return text
    return ""


def to_markdown(title, source_name, breadcrumb, body):
    safe_title = title.replace('"', "'")
    lines = [
        "---",
        'title: "' + safe_title + '"',
        'source: "' + source_name + '"',
    ]
    crumb_body = ""
    if breadcrumb:
        safe_crumb = breadcrumb.replace('"', "'")
        lines.append('breadcrumb: "' + safe_crumb + '"')
        crumb_body = "**Path:** " + breadcrumb + "\n\n"
    lines.extend([
        "categories:",
        '  - "[[Astrology]]"',
        "tags:",
        "  - definitions",
        "  - AMG",
        "---",
        "",
        "# " + title,
        "",
    ])
    return (
        "\n".join(lines)
        + "\n"
        + crumb_body
        + body
        + "\n\n### Backlinks\n![[Backlinks.base]]\n"
    )


print("Starting")
print("Folder:", FOLDER)

files = list(FOLDER.glob("*.html")) + list(FOLDER.glob("*.htm"))
print("HTML files found:", len(files))
for f in files:
    print(" ", f.name)

if not files:
    print("No HTML files found. Stop.")
else:
    OUT_DIR.mkdir(exist_ok=True)
    print("Writing to:", OUT_DIR)
    for file in files:
        print("Reading", file.name)
        content = file.read_text(encoding="utf-8", errors="replace")
        title = extract_title(content, file.stem)
        body = extract_body(content)
        breadcrumb = extract_breadcrumb(content)
        md = to_markdown(title, file.name, breadcrumb, body)
        out_path = OUT_DIR / (file.stem + ".md")
        out_path.write_text(md, encoding="utf-8")
        print("Wrote", out_path)

print("Done")