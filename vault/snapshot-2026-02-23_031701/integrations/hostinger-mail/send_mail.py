#!/usr/bin/env python3
import smtplib
import os
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

def send_mail(to_addr, subject, body_md):
    base = Path(__file__).resolve().parent
    load_env(base / ".env")

    smtp_host = os.getenv("MAIL_SMTP_HOST", "smtp.hostinger.com")
    smtp_port = int(os.getenv("MAIL_SMTP_PORT", "465"))
    username = os.getenv("MAIL_USERNAME", "")
    password = os.getenv("MAIL_PASSWORD", "")

    if not username or not password:
        raise SystemExit("Missing MAIL_USERNAME/MAIL_PASSWORD in .env")

    msg = MIMEMultipart()
    msg["From"] = f"Cohera <{username}>"
    msg["To"] = to_addr
    msg["Subject"] = subject

    # Attach HTML body
    msg.attach(MIMEText(body_md, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(username, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending mail: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: reply.py <to> <subject> <body>")
        sys.exit(1)
    
    to = sys.argv[1]
    subj = sys.argv[2]
    # Interpret explicit \n as actual newlines if passed from shell
    body = sys.argv[3].replace("\\n", "\n")
    
    if send_mail(to, subj, body):
        print(f"Sent email to {to}")
    else:
        sys.exit(1)
