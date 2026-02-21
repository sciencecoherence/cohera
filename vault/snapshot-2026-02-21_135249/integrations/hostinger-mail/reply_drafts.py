#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path


def main():
    base = Path(__file__).resolve().parent
    out_dir = base / "out"
    digest_path = out_dir / "latest.json"
    drafts_dir = out_dir / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)

    if not digest_path.exists():
        raise SystemExit("No digest found. Run poller.py first.")

    digest = json.loads(digest_path.read_text(encoding="utf-8"))
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    created = 0
    for item in digest.get("items", []):
        if item.get("category") not in {"urgent", "action", "research"}:
            continue

        subject = item.get("subject") or "(no subject)"
        sender = item.get("sender") or ""
        snippet = item.get("snippet") or ""
        category = item.get("category")

        body = f"""# Reply Draft ({category})

To: {sender}
Subject: Re: {subject}

Hi,

Thanks for your message.

(Use this section to add the exact response based on context.)

---
Original snippet:
{snippet}
"""

        safe_name = "".join(c for c in subject if c.isalnum() or c in ("-", "_", " ")).strip().replace(" ", "_")[:60] or "message"
        path = drafts_dir / f"{ts}-{category}-{safe_name}.md"
        path.write_text(body, encoding="utf-8")
        created += 1

    print(f"Created {created} draft(s) in {drafts_dir}")


if __name__ == "__main__":
    main()
