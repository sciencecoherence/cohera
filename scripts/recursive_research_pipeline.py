#!/usr/bin/env python3
"""
Append-only Cohera recursive research pipeline.

Safety rule:
- Never rewrite website structure/CSS/layout.
- Only append new cards/entries into existing Home/Research/Publications grids.
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
TZ = dt.timezone(dt.timedelta(hours=-5))

TOPICS = [
    "time crystal biology",
    "metabolic health systems biology",
    "chaos control biological systems",
    "self-organization nonequilibrium thermodynamics",
    "digital twins uncertainty",
]

MAX_FETCH_PER_TOPIC = 8
MAX_NEW_PER_RUN = 8
MAX_HOME_NEWS = 1
MAX_RESEARCH_FEED = 1
MAX_PUBLICATIONS = 24


def now_lima() -> dt.datetime:
    return dt.datetime.now(TZ)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:90] or "item"


def ensure_dirs() -> None:
    for p in [STATE_DIR, SOURCES_DIR, DIGESTS_DIR, SITE / "publications" / "pdf"]:
        p.mkdir(parents=True, exist_ok=True)


def strip_html_text(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"items": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"items": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


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
    out: list[dict] = []

    for e in root.findall("atom:entry", ns):
        title = strip_html_text(e.findtext("atom:title", default="", namespaces=ns))
        summary = strip_html_text(e.findtext("atom:summary", default="", namespaces=ns))
        paper_id = e.findtext("atom:id", default="", namespaces=ns).strip()
        published = e.findtext("atom:published", default="", namespaces=ns).strip()
        links = [ln.get("href", "") for ln in e.findall("atom:link", ns)]
        pdf = next((x for x in links if x.endswith(".pdf")), "")
        authors = [strip_html_text(a.findtext("atom:name", default="", namespaces=ns)) for a in e.findall("atom:author", ns)]
        if not paper_id or not title:
            continue
        out.append(
            {
                "id": paper_id,
                "title": title,
                "summary": summary,
                "published": published,
                "authors": [a for a in authors if a],
                "pdf": pdf,
                "topic": topic,
                "source": "arXiv",
            }
        )
    return out


def discover_arxiv() -> list[dict]:
    items: list[dict] = []
    for t in TOPICS:
        try:
            items.extend(fetch_arxiv_topic(t))
        except Exception:
            continue
    dedup = {x["id"]: x for x in items}
    return sorted(dedup.values(), key=lambda x: x.get("published", ""), reverse=True)


def integrate_new_items(discovered: list[dict], state: dict) -> tuple[list[dict], dict]:
    known = {x.get("id") for x in state.get("items", [])}
    new: list[dict] = []
    run_ts = now_lima().isoformat()
    for item in discovered:
        if item["id"] in known:
            continue
        x = dict(item)
        x["addedAt"] = run_ts
        x["kind"] = "paper"
        x["status"] = "discovered"
        new.append(x)
        if len(new) >= MAX_NEW_PER_RUN:
            break
    state["items"] = (new + state.get("items", []))[:400]
    return new, state


def write_sources_snapshot(discovered: list[dict]) -> pathlib.Path:
    stamp = now_lima().strftime("%Y-%m-%d_%H%M%S")
    out = SOURCES_DIR / f"{stamp}.json"
    out.write_text(json.dumps(discovered, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def citation_line(item: dict) -> str:
    authors = ", ".join(item.get("authors", [])[:4])
    if len(item.get("authors", [])) > 4:
        authors += " et al."
    return f"{authors} ({item.get('published','')[:10]}). {item.get('title','')}. arXiv. {item.get('id','')}"


def write_digest(new_items: list[dict], source_file: pathlib.Path) -> pathlib.Path:
    out = DIGESTS_DIR / f"{now_lima().strftime('%Y-%m-%d')}-arxiv-digest.md"
    lines = [
        f"# Cohera Research Digest — {now_lima().strftime('%Y-%m-%d %H:%M')} (Lima)",
        "",
        f"Source snapshot: `{source_file.relative_to(ROOT)}`",
        "",
        "## New discoveries",
        "",
    ]
    if not new_items:
        lines.append("No new unique papers discovered in this run.")
    else:
        for i, it in enumerate(new_items, 1):
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


def write_synthesis_brief(items: list[dict]) -> pathlib.Path:
    out = RESEARCH / "synthesis-latest.md"
    lines = [
        f"# Cohera Synthesis Brief — {now_lima().strftime('%Y-%m-%d %H:%M')} (Lima)",
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


def render_card(date_str: str, tag: str, title: str, body: str, link: str | None = None) -> str:
    date_str = html.escape(date_str)
    tag = html.escape(tag)
    title = html.escape(title)
    body = html.escape(body)
    link_html = f'<p><a href="{html.escape(link)}" target="_blank" rel="noopener">Primary source ↗</a></p>' if link else ""
    return f"""
                <div class=\"card\">
                    <div class=\"card-meta\">
                        <span class=\"accent-text\">{date_str}</span>
                        <span>[{tag}]</span>
                    </div>
                    <h2 class=\"card-title\">{title}</h2>
                    <div class=\"card-body\">{body}{link_html}</div>
                </div>"""


def find_grid_div_bounds(text: str, grid_class_snippet: str) -> tuple[int, int] | None:
    """Return [start, end) bounds for the first <div class="...grid..."> block."""
    open_pat = re.compile(rf'<div\s+class="[^"]*{re.escape(grid_class_snippet)}[^"]*">')
    m = open_pat.search(text)
    if not m:
        return None

    # Find matching </div> using depth counting from the matched opening div.
    token_pat = re.compile(r'<div\b[^>]*>|</div>', re.IGNORECASE)
    depth = 0
    end_pos = None
    for t in token_pat.finditer(text, m.start()):
        tok = t.group(0).lower()
        if tok.startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end_pos = t.end()
                break

    if end_pos is None:
        return None
    return (m.start(), end_pos)


def insert_blocks_after_grid_open(file_path: pathlib.Path, grid_class_snippet: str, blocks: list[tuple[str, str]]) -> int:
    """
    blocks: list of (unique_marker_id, html_block)
    Inserts right after opening <div class="..."> of matching grid class.

    Boundary contract:
    - only mutate inside the matched grid <div>...</div>
    - everything before/after that block must stay byte-identical
    """
    if not file_path.exists() or not blocks:
        return 0

    text = file_path.read_text(encoding="utf-8")

    old_bounds = find_grid_div_bounds(text, grid_class_snippet)
    if not old_bounds:
        return 0

    open_pat = re.compile(rf'(<div\s+class="[^"]*{re.escape(grid_class_snippet)}[^"]*">)')
    m = open_pat.search(text)
    if not m:
        return 0

    inject_chunks = []
    for marker_id, block in blocks:
        marker = f"<!-- PIPELINE:{marker_id} -->"
        if marker in text:
            continue
        inject_chunks.append(marker + "\n" + block)

    if not inject_chunks:
        return 0

    insertion = "\n" + "\n".join(inject_chunks) + "\n"
    idx = m.end()
    new_text = text[:idx] + insertion + text[idx:]

    # Boundary safety check: no mutations allowed outside target grid block.
    new_bounds = find_grid_div_bounds(new_text, grid_class_snippet)
    if not new_bounds:
        raise RuntimeError(f"Boundary check failed: cannot locate grid in updated file {file_path}")

    old_start, old_end = old_bounds
    new_start, new_end = new_bounds

    if text[:old_start] != new_text[:new_start] or text[old_end:] != new_text[new_end:]:
        raise RuntimeError(
            f"Boundary check failed for {file_path}: detected modifications outside .{grid_class_snippet} block"
        )

    file_path.write_text(new_text, encoding="utf-8")
    return len(inject_chunks)


RELEVANCE_KEYWORDS = [
    "time crystal",
    "time-crystalline",
    "coherence",
    "metabolic",
    "metabolism",
    "regeneration",
    "bioelectric",
    "chemiosmosis",
    "holographic",
]

THREAD_STATE_FILE = STATE_DIR / "thread_state.json"
THREADS = [
    {
        "id": "substrate-boundaries",
        "tag": "Time-Crystalline Holographic Substrate",
        "title": "Defining substrate boundaries against decoherence",
        "hypothesis": "Boundary constraints can be modeled as coherence-preserving operators coupling metabolic feedback loops to environmental oscillations.",
        "source": "http://arxiv.org/abs/2412.02651",
    },
    {
        "id": "metabolic-regeneration",
        "tag": "Metabolic Regeneration",
        "title": "Metabolic phase-locking as regeneration mechanism",
        "hypothesis": "Regenerative pathways may be stabilized by phase-locking between intracellular pumps and external oscillatory fields.",
        "source": "http://arxiv.org/abs/2309.10837",
    },
]


def is_relevant_to_cohera(item: dict) -> bool:
    text = f"{item.get('title','')} {item.get('summary','')} {item.get('topic','')}".lower()
    return any(k in text for k in RELEVANCE_KEYWORDS)


def pick_relevant_item(candidates: list[dict]) -> dict | None:
    for it in candidates:
        if is_relevant_to_cohera(it):
            return it
    return None


def load_thread_state() -> dict:
    if not THREAD_STATE_FILE.exists():
        return {"run": 0, "cursor": 0}
    try:
        return json.loads(THREAD_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"run": 0, "cursor": 0}


def save_thread_state(state: dict) -> None:
    THREAD_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def next_thread_update() -> dict:
    st = load_thread_state()
    run = int(st.get("run", 0)) + 1
    cursor = int(st.get("cursor", 0)) % len(THREADS)
    thread = THREADS[cursor]

    step = (run - 1) % 4 + 1
    step_text = [
        "Refined boundary assumptions and isolated dominant constraints.",
        "Mapped source claims into testable variables for the model.",
        "Updated falsification hooks and decoherence stress scenarios.",
        "Consolidated interim synthesis toward publication candidate framing.",
    ][step - 1]

    st["run"] = run
    st["cursor"] = (cursor + 1) % len(THREADS)
    save_thread_state(st)

    return {
        "thread": thread,
        "step": step,
        "step_text": step_text,
        "run": run,
    }


def append_home_and_research(new_items: list[dict], feed_items: list[dict], digest_file: pathlib.Path, source_file: pathlib.Path) -> tuple[int, int]:
    home_file = SITE / "index.html"
    research_file = SITE / "research" / "index.html"

    run_stamp = now_lima().strftime("%Y%m%d-%H%M%S")
    run_date = now_lima().strftime("%d/%m/%Y")

    # Only promote a paper when it is NEW in this run.
    # Prevents reposting the same source card across multiple cron cycles.
    chosen = pick_relevant_item(new_items)

    if not chosen:
        # Continue internal thread development even when no new relevant source appears.
        upd = next_thread_update()
        thread = upd["thread"]
        pid = slugify(thread["id"] + f"-r{upd['run']}")

        home_blocks: list[tuple[str, str]] = [
            (
                f"home:run:{run_stamp}",
                render_card(
                    run_date,
                    "Scientific News",
                    f"{thread['title']} — progress step {upd['step']}",
                    f"{thread['hypothesis']} {upd['step_text']}",
                    thread["source"],
                ),
            )
        ]

        process_body = (
            f"Development step {upd['step']}: {upd['step_text']} "
            f"Evidence log: {digest_file.relative_to(ROOT)} | Source snapshot: {source_file.relative_to(ROOT)}."
        )
        research_blocks: list[tuple[str, str]] = [
            (
                f"research:run:{run_stamp}:{pid}",
                render_card(
                    run_date,
                    "Research Development",
                    f"{thread['title']} — model iteration",
                    process_body,
                    thread["source"],
                ),
            )
        ]
    else:
        pid = slugify(chosen.get("id", chosen.get("title", "")))
        home_blocks = [
            (
                f"home:run:{run_stamp}",
                render_card(
                    chosen.get("published", "")[:10].replace("-", "/") or run_date,
                    "Scientific News",
                    chosen.get("title", "Untitled"),
                    textwrap.shorten(chosen.get("summary", ""), width=320, placeholder="…"),
                    chosen.get("id", ""),
                ),
            )
        ]

        process_body = (
            "Development step: this source was integrated into the active Cohera research thread, claims were extracted, "
            f"and evidence was logged in {digest_file.relative_to(ROOT)} (snapshot: {source_file.relative_to(ROOT)})."
        )
        research_blocks = [
            (
                f"research:run:{run_stamp}:{pid}",
                render_card(
                    chosen.get("published", "")[:10].replace("-", "/") or run_date,
                    "Research Development",
                    f"Development step — {chosen.get('title', 'Untitled')}",
                    process_body,
                    chosen.get("id", ""),
                ),
            )
        ]

    h = insert_blocks_after_grid_open(home_file, "grid-1", home_blocks)
    r = insert_blocks_after_grid_open(research_file, "grid-2", research_blocks)
    return h, r


def sync_publication_pdfs() -> list[pathlib.Path]:
    """
    Only sync Cohera-authored final publications.
    Source of truth: research/publications/final/*.pdf
    """
    src = RESEARCH / "publications" / "final"
    dst = SITE / "publications" / "pdf"
    copied: list[pathlib.Path] = []

    if not src.exists():
        # Ensure destination exists but do not auto-import external resource PDFs.
        dst.mkdir(parents=True, exist_ok=True)
        return copied

    for f in sorted(src.glob("*.pdf")):
        t = dst / f.name
        t.write_bytes(f.read_bytes())
        copied.append(t)
    return copied


def append_publication_cards(pdf_files: list[pathlib.Path]) -> int:
    pub_file = SITE / "publications" / "index.html"
    blocks: list[tuple[str, str]] = []
    # newest first
    for p in sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True)[:MAX_PUBLICATIONS]:
        pid = slugify(p.name)
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=TZ).strftime("%d/%m/%Y")
        title = p.stem.replace("_", " ")
        rel = f"pdf/{p.name}"
        body = f"Final publication artifact from synthesis pipeline. Download: {rel}"
        block = render_card(mtime, "Publication", title, body, link=rel)
        blocks.append((f"pub:{pid}", block))

    return insert_blocks_after_grid_open(pub_file, "grid", blocks)


def main() -> None:
    ensure_dirs()

    discovered = discover_arxiv()
    source_file = write_sources_snapshot(discovered)

    state = load_state()
    new_items, state = integrate_new_items(discovered, state)
    save_state(state)

    digest_file = write_digest(new_items, source_file)
    write_synthesis_brief(new_items)

    feed_items = state.get("items", [])
    home_added, research_added = append_home_and_research(new_items, feed_items, digest_file, source_file)

    synced_pdfs = sync_publication_pdfs()
    pub_added = append_publication_cards(synced_pdfs)

    print(f"Pipeline complete. discovered={len(discovered)} new={len(new_items)}")
    print(f"Digest: {digest_file}")
    print(f"Added cards -> home:{home_added} research:{research_added} publications:{pub_added}")


if __name__ == "__main__":
    main()
