# Hostinger Mailbox Integration (Mode B)

This integration connects to `cohera@sciencecoherence.com` via IMAP, reads unread emails, classifies them, and generates a digest for review.

## What this gives you

- Poll unread emails on Hostinger IMAP
- Lightweight classification: `urgent`, `action`, `research`, `ignore`, `general`
- Save digest as JSON + Markdown
- Optional reply draft generation (manual approval before sending)

---

## 1) Create local secrets file

Create `integrations/hostinger-mail/.env` (do **not** commit):

```bash
MAIL_IMAP_HOST=imap.hostinger.com
MAIL_IMAP_PORT=993
MAIL_SMTP_HOST=smtp.hostinger.com
MAIL_SMTP_PORT=465
MAIL_USERNAME=cohera@sciencecoherence.com
MAIL_PASSWORD=REPLACE_WITH_MAILBOX_PASSWORD
MAILBOX=INBOX
MAX_MESSAGES=25
STATE_FILE=integrations/hostinger-mail/state.json
OUT_DIR=integrations/hostinger-mail/out
MARK_SEEN=false
```

> Keep credentials local only. Never paste passwords in chat.

---

## 2) Configure routing keywords

Edit `integrations/hostinger-mail/rules.json` to tune classification.

---

## 3) Run once (manual test)

```bash
python3 integrations/hostinger-mail/poller.py --once
```

Outputs:
- `integrations/hostinger-mail/out/latest.json`
- `integrations/hostinger-mail/out/latest.md`

---

## 4) Run every 15 minutes (cron)

```bash
crontab -e
```

Add:

```cron
*/15 * * * * cd /home/xavier/.openclaw/workspace && /usr/bin/python3 integrations/hostinger-mail/poller.py --once >> integrations/hostinger-mail/out/poller.log 2>&1
```

---

## 5) Optional: draft replies (manual approval workflow)

Generate a reply draft from the last digest:

```bash
python3 integrations/hostinger-mail/reply_drafts.py
```

This writes markdown drafts in `integrations/hostinger-mail/out/drafts/`.

---

## 6) Safety defaults

- `MARK_SEEN=false` by default (non-destructive)
- No auto-send
- Credentials are loaded only from `.env`

If you later want auto-send, add a separate explicit approval step first.
