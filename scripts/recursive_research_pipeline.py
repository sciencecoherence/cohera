#!/usr/bin/env python3
"""
Cohera recursive research + publishing pipeline.

Flow:
1) Discover recent arXiv papers for configured topics
2) Store structured notes + citations
3) Generate digest artifacts
4) Render site pages:
   - Home: important news
   - Research Hub: research feed
   - Publications: PDF ledger + synthesis status
"""

from __future__ import annotations

import datetime as dt
import html
import json
import pathlib
import re
import textwrap
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("/home/xavier/.openclaw/workspace/cohera-repo")
SITE = ROOT / "site"
RESEARCH = ROOT / "research"
STATE_DIR = RESEARCH / "pipeline"
SOURCES_DIR = RESEARCH / "sources" / "arxiv"
DIGESTS_DIR = RESEARCH / "digests"

STATE_FILE = STATE_DIR / "feed.json"

TZ = dt.timezone(dt.timedelta(hours=-5))  # America/Lima offset

TOPICS = [
    "time crystal biology",
    "metabolic health systems biology",
    "chaos control biological systems",
    "self-organization nonequilibrium thermodynamics",
    "digital twins uncertainty",
]

MAX_FETCH_PER_TOPIC = 8
MAX_NEW_PER_RUN = 8
MAX_HOME_NEWS = 5
MAX_RESEARCH_FEED = 16
MAX_PUBLICATIONS = 24


# ---------- Utilities ----------

def now_lima() -> dt.datetime:
    return dt.datetime.now(TZ)


def fmt_date(d: dt.datetime) -> str:
    return d.strftime("%d/%m/%Y")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80] or "item"


def ensure_dirs() -> None:
    for p in [STATE_DIR, SOURCES_DIR, DIGESTS_DIR, SITE / "publications" / "pdf"]:
        p.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"items": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"items": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_html_text(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


# ---------- arXiv discovery ----------

def fetch_arxiv_topic(topic: str, max_results: int = MAX_FETCH_PER_TOPIC) -> list[dict]:
    query = urllib.parse.quote(f"all:{topic}")
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    )
    with urllib.request.urlopen(url, timeout=25) as resp:
        data = resp.read()

    root = ET.fromstring(data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items: list[dict] = []

    for e in root.findall("atom:entry", ns):
        title = strip_html_text(e.findtext("atom:title", default="", namespaces=ns))
        summary = strip_html_text(e.findtext("atom:summary", default="", namespaces=ns))
        paper_id = e.findtext("atom:id", default="", namespaces=ns).strip()
        published = e.findtext("atom:published", default="", namespaces=ns).strip()
        updated = e.findtext("atom:updated", default="", namespaces=ns).strip()
        links = [ln.get("href", "") for ln in e.findall("atom:link", ns)]
        pdf = next((x for x in links if x.endswith(".pdf")), "")
        authors = [strip_html_text(a.findtext("atom:name", default="", namespaces=ns)) for a in e.findall("atom:author", ns)]

        if not paper_id or not title:
            continue

        items.append(
            {
                "id": paper_id,
                "title": title,
                "summary": summary,
                "published": published,
                "updated": updated,
                "authors": [a for a in authors if a],
                "pdf": pdf,
                "topic": topic,
                "source": "arXiv",
            }
        )

    return items


def discover_arxiv() -> list[dict]:
    discovered: list[dict] = []
    for topic in TOPICS:
        try:
            discovered.extend(fetch_arxiv_topic(topic))
        except Exception as ex:
            discovered.append(
                {
                    "id": f"error:{slugify(topic)}",
                    "title": f"Discovery error for topic: {topic}",
                    "summary": str(ex),
                    "published": now_lima().isoformat(),
                    "updated": now_lima().isoformat(),
                    "authors": ["pipeline"],
                    "pdf": "",
                    "topic": topic,
                    "source": "arXiv",
                    "error": True,
                }
            )

    by_id: dict[str, dict] = {}
    for it in discovered:
        if it["id"].startswith("error:"):
            continue
        by_id[it["id"]] = it

    def sort_key(x: dict) -> str:
        return x.get("published", "")

    return sorted(by_id.values(), key=sort_key, reverse=True)


# ---------- State update + artifacts ----------

def integrate_new_items(discovered: list[dict], state: dict) -> tuple[list[dict], dict]:
    known = {x.get("id") for x in state.get("items", [])}
    run_ts = now_lima().isoformat()
    new_items: list[dict] = []

    for item in discovered:
        if item["id"] in known:
            continue
        item = dict(item)
        item["addedAt"] = run_ts
        item["kind"] = "paper"
        item["status"] = "discovered"
        new_items.append(item)
        if len(new_items) >= MAX_NEW_PER_RUN:
            break

    state_items = state.get("items", [])
    state_items = new_items + state_items
    state["items"] = state_items[:300]

    return new_items, state


def write_run_sources(discovered: list[dict]) -> pathlib.Path:
    stamp = now_lima().strftime("%Y-%m-%d_%H%M%S")
    out = SOURCES_DIR / f"{stamp}.json"
    out.write_text(json.dumps(discovered, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def citation_line(item: dict) -> str:
    authors = ", ".join(item.get("authors", [])[:4])
    if len(item.get("authors", [])) > 4:
        authors += " et al."
    published = item.get("published", "")[:10]
    link = item.get("id", "")
    return f"{authors} ({published}). {item.get('title','')}. arXiv. {link}"


def write_digest(new_items: list[dict], source_file: pathlib.Path) -> pathlib.Path:
    d = now_lima()
    out = DIGESTS_DIR / f"{d.strftime('%Y-%m-%d')}-arxiv-digest.md"

    lines = [
        f"# Cohera Research Digest — {d.strftime('%Y-%m-%d %H:%M')} (Lima)",
        "",
        f"Source snapshot: `{source_file.relative_to(ROOT)}`",
        "",
        "## New discoveries",
        "",
    ]

    if not new_items:
        lines.append("No new unique papers discovered in this run.")
    else:
        for i, it in enumerate(new_items, start=1):
            lines.extend(
                [
                    f"### {i}. {it['title']}",
                    f"- Topic: {it.get('topic','')}",
                    f"- Published: {it.get('published','')[:10]}",
                    f"- URL: {it.get('id','')}",
                    f"- PDF: {it.get('pdf','') or 'n/a'}",
                    f"- Summary: {it.get('summary','')}",
                    f"- Citation: {citation_line(it)}",
                    "",
                ]
            )

    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out


# ---------- HTML rendering ----------

def render_card(date_str: str, tag: str, title: str, body: str, link: str | None = None) -> str:
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    safe_tag = html.escape(tag)
    safe_date = html.escape(date_str)
    link_html = f'<p><a href="{html.escape(link)}" target="_blank" rel="noopener">Primary source ↗</a></p>' if link else ""
    return f"""
                <div class=\"card\">
                    <div class=\"card-meta\">
                        <span class=\"accent-text\">{safe_date}</span>
                        <span>[{safe_tag}]</span>
                    </div>
                    <h2 class=\"card-title\">{safe_title}</h2>
                    <div class=\"card-body\">{safe_body}{link_html}</div>
                </div>"""


def write_home_page(items: list[dict]) -> None:
    cards = []
    for it in items[:MAX_HOME_NEWS]:
        body = textwrap.shorten(it.get("summary", ""), width=320, placeholder="…")
        cards.append(render_card(it.get("published", "")[:10].replace("-", "/"), "Paper Discovery", it["title"], body, it.get("id")))

    cards_html = "\n".join(cards) if cards else render_card(fmt_date(now_lima()), "Pipeline", "No fresh discoveries", "The scheduler ran, but no new unique entries were found.")

    html_doc = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Home - Cohera Lab</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;800&family=JetBrains+Mono:wght@400;700&display=swap\" rel=\"stylesheet\">
    <link rel=\"stylesheet\" href=\"assets/style.css\">
</head>
<body>
    <div class=\"wrapper\">
        <header>
            <a href=\"index.html\" class=\"logo\">COHERA<span>.</span></a>
            <nav>
                <a href=\"index.html\" class=\"active\">Home</a>
                <a href=\"research/index.html\">Research Hub</a>
                <a href=\"publications/index.html\">Publications</a>
            </nav>
        </header>

        <main>
            <p class=\"mission\">
                <span class=\"highlight\">Build a coherent model of reality</span> — with evidence, iteration, and clarity. Cohera Lab is the experimentation space behind Science Coherence.
            </p>

            <div class=\"section-title\">
                <span>LATEST NEWS & FINDINGS</span>
                <span>STATUS: OPERATIONAL</span>
            </div>

            <div class=\"grid grid-1\">
{cards_html}
            </div>
        </main>

        <footer>
            <span>&copy; 2026 COHERA LAB</span>
            <span>EVIDENCE / ITERATION / CLARITY</span>
        </footer>
    </div>
</body>
</html>
"""
    (SITE / "index.html").write_text(html_doc, encoding="utf-8")


def write_research_page(items: list[dict], digest_file: pathlib.Path) -> None:
    cards = []
    for it in items[:MAX_RESEARCH_FEED]:
        body = textwrap.shorten(it.get("summary", ""), width=600, placeholder="…")
        tag = f"{it.get('source', 'Source')} · {it.get('topic', 'General')}"
        cards.append(render_card(it.get("published", "")[:10].replace("-", "/"), tag, it["title"], body, it.get("id")))

    cards_html = "\n".join(cards) if cards else render_card(fmt_date(now_lima()), "Pipeline", "Research feed empty", "No entries yet. Run the pipeline.")

    html_doc = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Research Hub - Cohera Lab</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;800&family=JetBrains+Mono:wght@400;700&display=swap\" rel=\"stylesheet\">
    <link rel=\"stylesheet\" href=\"../assets/style.css\">
</head>
<body>
    <div class=\"wrapper\">
        <header>
            <a href=\"../index.html\" class=\"logo\">COHERA<span>.</span></a>
            <nav>
                <a href=\"../index.html\">Home</a>
                <a href=\"index.html\" class=\"active\">Research Hub</a>
                <a href=\"../publications/index.html\">Publications</a>
            </nav>
        </header>

        <main>
            <p class=\"mission\">
                Chronological feed of source-grounded research stubs generated by the <span class=\"highlight\">recursive pipeline</span>.
                Latest digest: <code>{html.escape(str(digest_file.relative_to(ROOT)))}</code>
            </p>

            <div class=\"section-title\">
                <span>RESEARCH HUB</span>
                <span>STATUS: MONITORING</span>
            </div>

            <div class=\"grid grid-2\">
{cards_html}
            </div>
        </main>

        <footer>
            <span>&copy; 2026 COHERA LAB</span>
            <span>EVIDENCE / ITERATION / CLARITY</span>
        </footer>
    </div>
</body>
</html>
"""
    (SITE / "research" / "index.html").write_text(html_doc, encoding="utf-8")


def sync_publication_pdfs() -> list[pathlib.Path]:
    src = RESEARCH / "pdf"
    dst = SITE / "publications" / "pdf"
    copied: list[pathlib.Path] = []
    if not src.exists():
        return copied

    for f in sorted(src.glob("*.pdf")):
        target = dst / f.name
        target.write_bytes(f.read_bytes())
        copied.append(target)
    return copied


def write_publications_page() -> None:
    pdf_dir = SITE / "publications" / "pdf"
    pdfs = sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)

    cards = []
    for p in pdfs[:MAX_PUBLICATIONS]:
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=TZ)
        title = p.stem.replace("_", " ")
        rel = f"pdf/{p.name}"
        body = f"Final publication artifact from synthesis pipeline. <a href=\"{html.escape(rel)}\" target=\"_blank\" rel=\"noopener\">Download PDF ↗</a>"
        cards.append(render_card(fmt_date(mtime), "Publication", title, body))

    if not cards:
        cards.append(render_card(fmt_date(now_lima()), "Archive", "No PDFs published yet", "Run synthesis and PDF build to populate the publication ledger."))

    cards_html = "\n".join(cards)

    html_doc = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Publications - Cohera Lab</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;800&family=JetBrains+Mono:wght@400;700&display=swap\" rel=\"stylesheet\">
    <link rel=\"stylesheet\" href=\"../assets/style.css\">
</head>
<body>
    <div class=\"wrapper\">
        <header>
            <a href=\"../index.html\" class=\"logo\">COHERA<span>.</span></a>
            <nav>
                <a href=\"../index.html\">Home</a>
                <a href=\"../research/index.html\">Research Hub</a>
                <a href=\"index.html\" class=\"active\">Publications</a>
            </nav>
        </header>

        <main>
            <p class=\"mission\">
                Repository for peer-ready <span class=\"highlight\">PDF manuscripts</span> generated from research synthesis.
            </p>

            <div class=\"section-title\">
                <span>MANUSCRIPT LEDGER</span>
                <span>STATUS: LIVE</span>
            </div>

            <div class=\"grid\">
{cards_html}
            </div>
        </main>

        <footer>
            <span>&copy; 2026 COHERA LAB</span>
            <span>EVIDENCE / ITERATION / CLARITY</span>
        </footer>
    </div>
</body>
</html>
"""
    (SITE / "publications" / "index.html").write_text(html_doc, encoding="utf-8")


def write_synthesis_brief(items: list[dict]) -> pathlib.Path:
    out = RESEARCH / "synthesis-latest.md"
    lines = [
        f"# Cohera Synthesis Brief — {now_lima().strftime('%Y-%m-%d %H:%M')} (Lima)",
        "",
        "This brief consolidates the latest research discoveries into publication candidates.",
        "",
        "## Priority candidates",
        "",
    ]

    if not items:
        lines.append("- No new items this cycle.")
    else:
        for it in items[:6]:
            lines.extend(
                [
                    f"- **{it['title']}**",
                    f"  - Topic: {it.get('topic','')}",
                    f"  - Claim to test: {textwrap.shorten(it.get('summary',''), width=180, placeholder='…')}",
                    f"  - Citation: {citation_line(it)}",
                ]
            )

    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out


def main() -> None:
    ensure_dirs()

    discovered = discover_arxiv()
    source_file = write_run_sources(discovered)

    state = load_state()
    new_items, state = integrate_new_items(discovered, state)
    save_state(state)

    digest_file = write_digest(new_items, source_file)
    write_synthesis_brief(new_items)

    feed_items = state.get("items", [])
    write_home_page(feed_items)
    write_research_page(feed_items, digest_file)

    sync_publication_pdfs()
    write_publications_page()

    print(f"Pipeline complete. discovered={len(discovered)} new={len(new_items)}")
    print(f"Digest: {digest_file}")
    print(f"State: {STATE_FILE}")


if __name__ == "__main__":
    main()
