#!/usr/bin/env python3
import subprocess, sys

res = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True)
print(res.stdout.strip())
if res.stderr.strip():
    print(res.stderr.strip())
