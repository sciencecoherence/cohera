#!/usr/bin/env python3
import argparse
import email
import html
import imaplib
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from email.header import decode_header
from pathlib import Path


def load_env(path: Path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k and k not in os.environ:
            os.environ[k] = v


def decode_mime(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


@dataclass
class MailItem:
    uid: str
    date: str
    sender: str
    subject: str
    snippet: str
    category: str


def html_to_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</p>|</div>|</li>|</tr>|</h[1-6]>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\r", "", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def extract_text(msg) -> str:
    plain_parts = []
    html_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get("Content-Disposition") or "")
            if "attachment" in cdisp.lower():
                continue

            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")

            if ctype == "text/plain":
                plain_parts.append(decoded)
            elif ctype == "text/html":
                html_parts.append(decoded)
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        decoded = payload.decode(charset, errors="replace")
        if msg.get_content_type() == "text/html":
            html_parts.append(decoded)
        else:
            plain_parts.append(decoded)

    if plain_parts:
        return "\n\n".join(plain_parts).strip()
    if html_parts:
        return html_to_text("\n\n".join(html_parts))
    return ""


def classify(sender: str, subject: str, body: str, rules: dict) -> str:
    text = clean_text(f"{sender} {subject} {body[:1500]}")

    for s in rules.get("urgent_senders", []):
        if s.lower() in sender.lower():
            return "urgent"
    for kw in rules.get("urgent_keywords", []):
        if kw.lower() in text:
            return "urgent"
    for kw in rules.get("ignore_keywords", []):
        if kw.lower() in text:
            return "ignore"
    for kw in rules.get("action_keywords", []):
        if kw.lower() in text:
            return "action"
    for kw in rules.get("research_keywords", []):
        if kw.lower() in text:
            return "research"
    return "general"


def main():
    parser = argparse.ArgumentParser(description="Hostinger mailbox poller")
    parser.add_argument("--once", action="store_true", help="Run one poll cycle")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    load_env(base / ".env")

    imap_host = os.getenv("MAIL_IMAP_HOST", "imap.hostinger.com")
    imap_port = int(os.getenv("MAIL_IMAP_PORT", "993"))
    username = os.getenv("MAIL_USERNAME", "")
    password = os.getenv("MAIL_PASSWORD", "")
    mailbox = os.getenv("MAILBOX", "INBOX")
    max_messages = int(os.getenv("MAX_MESSAGES", "25"))
    out_dir = Path(os.getenv("OUT_DIR", str(base / "out")))
    mark_seen = os.getenv("MARK_SEEN", "false").lower() == "true"

    if not username or not password:
        raise SystemExit("Missing MAIL_USERNAME/MAIL_PASSWORD in environment or .env")

    rules_path = base / "rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8")) if rules_path.exists() else {}

    out_dir.mkdir(parents=True, exist_ok=True)

    with imaplib.IMAP4_SSL(imap_host, imap_port) as M:
        M.login(username, password)
        M.select(mailbox)

        typ, data = M.search(None, "UNSEEN")
        if typ != "OK":
            raise SystemExit("Failed to search mailbox")

        ids = (data[0] or b"").decode().split()
        ids = ids[-max_messages:]

        items = []
        for uid in ids:
            typ, msg_data = M.fetch(uid, "(RFC822)")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            sender = decode_mime(msg.get("From", ""))
            subject = decode_mime(msg.get("Subject", ""))
            date = decode_mime(msg.get("Date", ""))
            body = extract_text(msg)
            snippet = re.sub(r"\s+", " ", body).strip()[:240]
            category = classify(sender, subject, body, rules)

            items.append(MailItem(
                uid=uid,
                date=date,
                sender=sender,
                subject=subject,
                snippet=snippet,
                category=category,
            ))

            if mark_seen:
                M.store(uid, "+FLAGS", "\\Seen")

    digest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "by_category": {},
        "items": [asdict(x) for x in items],
    }

    for item in items:
        digest["by_category"].setdefault(item.category, 0)
        digest["by_category"][item.category] += 1

    (out_dir / "latest.json").write_text(json.dumps(digest, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# Mail Digest ({digest['generated_at']})",
        f"Total unread processed: **{digest['count']}**",
        "",
        "## By category",
    ]
    for k, v in sorted(digest["by_category"].items()):
        lines.append(f"- {k}: {v}")

    lines.append("\n## Items")
    for it in items:
        lines.append(f"- [{it.category}] **{it.subject or '(no subject)'}** — {it.sender}")
        if it.snippet:
            lines.append(f"  - {it.snippet}")

    md = "\n".join(lines) + "\n"
    (out_dir / "latest.md").write_text(md, encoding="utf-8")

    print(md)

    if not args.once:
        print("Done.")


if __name__ == "__main__":
    main()
