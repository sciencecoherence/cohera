# PIPELINE.md - The Autonomous Research Engine

Research is not an open-ended loop. It is a strict progression through discrete states.

## The 3-State Progression

### State 1: Autodraft (Ingestion & Hypothesis)
**Trigger:** A new paper, concept, or raw data dump is introduced.

**Action:**
- Extract core arguments.
- Identify mathematical models.
- Cross-reference with existing frameworks (e.g., Time-Crystalline Coherent Biology, Cosmos Emergent Geometry).

**Exit Criteria (move to Candidate):**
- Core thesis is defined.
- At least one novel connection or falsification hook is established.
- Append label: `[STATUS: READY FOR SYNTHESIS]`

---

### State 2: Candidate (Synthesis & Formalization)
**Trigger:** An Autodraft achieves `[STATUS: READY FOR SYNTHESIS]`.

**Action:**
- Transform bullets into academic prose.
- Formalize math.

**Strict Constraints:**
- All variables and equations must be in strict LaTeX.
- Remove all meta-text, planning notes, and website/navigation artifacts.

**Exit Criteria (move to Publication):**
- Document reads like an arXiv preprint.
- Typesetting/sanitization pass completed.
- Append label: `[STATUS: READY FOR COMPILATION]`

---

### State 3: Publication (Typesetting & Deployment)
**Trigger:** A Candidate achieves `[STATUS: READY FOR COMPILATION]`.

**Action:**
- Compile to clean PDF.
- Move item from Active Pipeline to Publications outputs.

**Exit Criteria:**
- PDF generated.
- Mathematics legible and consistent.
- No formatting errors.
- Loop complete.

## Anti-Stuck Protocol

### 3-Pass Limit
Do not revise the same section more than 3 times.

### Forced Advancement
If a math proof or structural issue is unresolved after 3 attempts:
- isolate that section with `[REQUIRES HUMAN REVIEW]`
- force the document to next state
- never freeze in draft state

A published paper with one flagged section is more valuable than a perfect draft that never compiles.
