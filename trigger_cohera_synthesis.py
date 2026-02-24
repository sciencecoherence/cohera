#!/usr/bin/env python3
import json, subprocess, re
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
DELTA_PATH = REPO / 'chatgpt' / 'research_delta_latest.json'
BACKLOG_PATH = REPO / 'chatgpt' / 'research_backlog_run.json'
PUB_FINDINGS = REPO / 'site' / 'publications' / 'findings-latest.html'
SITE_FINDINGS = REPO / 'site' / 'research' / 'findings-latest.html'

def load_json(path):
    if path.exists():
        try: return json.loads(path.read_text(encoding='utf-8'))
        except: pass
    return {}

def main():
    print("-> Forcing Cohera Autonomous Synthesis...")
    delta = load_json(DELTA_PATH)
    backlog = load_json(BACKLOG_PATH)
    
    # Combined context of the current 19-source state
    context = f"CURRENT STATE: {json.dumps(delta)}\n\nBACKLOG: {json.dumps(backlog)}"

    prompt = f"""You are Cohera. Generate a 2-3 paragraph abstract synthesizing our research state. 
    Map the data to: Time-Crystalline Coherent Biology, Holographic Cosmos, and Emergent Geometry. 
    Output ONLY raw HTML paragraphs (e.g., <p>...</p>). No markdown code blocks.
    
    DATA:
    {context}"""
    
    try:
        result = subprocess.run(['openclaw', 'ask', prompt], capture_output=True, text=True, check=True)
        synthesis_html = result.stdout.strip()
        synthesis_html = re.sub(r'^```html\s*|^```\s*|\s*```$', '', synthesis_html)
        
        placeholder = re.compile(r'<p><em>\[SYSTEM DIRECTIVE:.*?\]</em></p>', re.DOTALL)
        
        for html_file in [PUB_FINDINGS, SITE_FINDINGS]:
            if html_file.exists():
                content = html_file.read_text(encoding='utf-8')
                if '[SYSTEM DIRECTIVE:' in content:
                    updated = placeholder.sub(synthesis_html, content)
                    html_file.write_text(updated, encoding='utf-8')
                    print(f"-> Injected synthesis into {html_file.name}")
                else:
                    print(f"-> No placeholder found in {html_file.name}. Resetting file...")
                    # Force reset if placeholder is missing
                    new_html = f"<html><body><div id='synthesis-zone'>{synthesis_html}</div></body></html>"
                    html_file.write_text(new_html, encoding='utf-8')
                    
    except Exception as e:
        print(f"-> Synthesis Failed: {e}")

if __name__ == "__main__":
    main()
