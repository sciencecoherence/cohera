#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
REPO_ROOT = Path('/home/xavier/cohera-repo')
INPUT_FILE = REPO_ROOT / 'chatgpt/latex/cosmos.tex'
OUTPUT_DIR = REPO_ROOT / 'research/drafts'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_gemini(prompt):
    """Call the Gemini CLI with a prompt."""
    try:
        # Assuming 'gemini' is in the PATH and configured
        result = subprocess.run(
            ['gemini', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error calling Gemini: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: 'gemini' command not found. Please ensure the gemini skill is installed and in PATH.")
        return None

def analyze_and_propose():
    """Read the source file and generate a proposal for a missing section."""
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    content = INPUT_FILE.read_text()
    
    # Define the specific research task
    task_prompt = f"""
    You are a theoretical physicist working on the "Science of Coherence" model.
    Read the following LaTeX document which outlines the model:
    
    === START DOCUMENT ===
    {content[:10000]} # Truncate if too large, but cosmos.tex is small enough
    === END DOCUMENT ===
    
    Your task is to solve the problem posed in "Section 8.2 Derive the compatibility condition cleanly".
    
    The document states:
    "Turn the schematic $\\Proj\\,\\Floquet \\approx \\Floquet_{{\\mathrm{{loc}}}}\\,\\Proj$ into a precise condition (norm bound, channel distance, commutator constraint, etc.) that yields a sharp stability criterion."
    
    Output a LaTeX subsection (Section 8.2.1) that:
    1. Proposes a specific norm-based inequality (e.g., using the Frobenius norm or operator norm).
    2. Defines the "Stability Error" $\\epsilon$.
    3. Interprets what happens when $\\epsilon$ crosses a threshold.
    
    Keep the style rigorous but consistent with the existing text.
    """
    
    print("Thinking... (Querying Gemini)")
    proposal = run_gemini(task_prompt)
    
    if proposal:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f'cosmos_8.2_proposal_{timestamp}.tex'
        output_file.write_text(proposal)
        print(f"Proposal written to: {output_file}")
    else:
        print("Failed to generate proposal.")

if __name__ == '__main__':
    analyze_and_propose()
