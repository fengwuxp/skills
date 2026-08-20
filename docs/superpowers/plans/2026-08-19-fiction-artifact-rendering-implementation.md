# Fiction Artifact Rendering Implementation Plan

> **Execution:** Implement in the current worktree with `superpowers:executing-plans`; keep unrelated dirty-worktree changes intact. No Git checkpoint, sync, install, network request, or paid image generation is authorized.

**Goal:** Extend the candidate `fiction-visual-designer` Skill so a confirmed artifact design can be rendered through `imagegen` as four consistent views and composed into one deterministic PNG design sheet.

**Architecture:** `fiction-visual-designer` owns the artifact rendering contract, view planning, continuity review, and stop conditions. System `imagegen` remains the only image-generation executor. A local Pillow script only validates, scales, labels, and composes four existing images; it never generates or edits visual content.

**Authority:** `docs/superpowers/specs/2026-08-19-fiction-artifact-rendering-design.md`. The base visual-design contract remains `docs/superpowers/specs/2026-08-19-fiction-visual-designer-design.md`.

---

## File Map

**Create:**

- `fiction-visual-designer/references/artifact-rendering.md`: input gate, four-view loop, `imagegen` handoff, review, retry, and stop contract.
- `fiction-visual-designer/scripts/compose-design-sheet.py`: deterministic 2x2 PNG composition with one embedded self-test.

**Modify:**

- `fiction-visual-designer/SKILL.md`: route confirmed artifact rendering without taking over model execution.
- `fiction-visual-designer/agents/openai.yaml`: expose the confirmed-artifact rendering trigger.
- `fiction-visual-designer/assets/visual-design-sheet-template.md`: add the minimum render-mode fields.
- `fiction-visual-designer/references/source-map.md`: record four reviewed sources and rejected runtime dependencies.
- `fixtures/skill-eval/fiction-visual-designer-behavior-cases.json`: add generation gate, confirmed render, and precision-limit cases; bind the new sources.
- `README.md`: describe the revised `fiction-visual-designer -> imagegen` responsibility boundary.
- `scripts/validate.sh`: compile the composer and validate the behavior fixture without requiring Pillow.

**Do not modify:** `novelist/**`, `imagegen`, provider configuration, install/sync scripts, admission status, Git state, or external runtime configuration.

---

### Task 1: Capture Behavior And Script RED

- [ ] Replace three narrower object-specialty cases with three rendering cases before changing production Skill files, keeping the repository validator's 5-8 case contract:
  - confirmed artifact design requests front/side/three-quarter/detail images and a design sheet;
  - visual candidate requests immediate rendering;
  - exact CAD/manufacturing/true-orthographic output is requested.
- [ ] Validate the fixture schema with:

```bash
scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json
```

- [ ] In an isolated fresh run, answer the new prompts without reading candidate sources. Record whether the baseline fails the explicit render-loop criteria; never fabricate a RED result.
- [ ] Run the absent composer with the bundled Python runtime:

```bash
"$CODEX_BUNDLED_PYTHON" fiction-visual-designer/scripts/compose-design-sheet.py --self-test
```

Expected: missing-file failure before implementation.

### Task 2: Implement And Test Deterministic Composition

- [ ] Create `compose-design-sheet.py` using only `argparse`, `pathlib`, `tempfile`, and installed Pillow.
- [ ] Accept `--front`, `--side`, `--three-quarter`, `--detail`, `--output`, and `--self-test`.
- [ ] Fail closed for missing/non-file inputs, non-PNG output, absent output parent, input/output collision, existing output, unreadable/non-image input, and missing Pillow.
- [ ] Produce a fixed 1600x1600 2x2 PNG with preserved aspect ratio, neutral background, borders, and ASCII labels.
- [ ] Run the embedded self-test using the bundled Python runtime; then run system-Python `py_compile` so repository validation does not depend on Desktop's Pillow installation.

### Task 3: Add The Artifact Rendering Contract

- [ ] Create `references/artifact-rendering.md` with the repository's five mandatory reference headings.
- [ ] Require `状态：已确认设计`; stop at `视觉候选` and reject CAD/manufacturing claims.
- [ ] Specify anchor-first generation, shared invariants, one targeted revision per failed view, deterministic composition, and optional beauty image.
- [ ] Update `SKILL.md`, `openai.yaml`, and the design-sheet template without copying the full reference into Level 2.

### Task 4: Record Sources And Public Routing

- [ ] Add source entries for `inference-sh/character-design-sheet`, Krea Skills issue 30, 80.lv's concept-art delivery article, and OpenAI's official image-generation guide.
- [ ] Record only the abstract methods; reject external CLIs, unsupported frontmatter, provider MCP dependencies, copied prompts, and vendor quality claims.
- [ ] Update `README.md` to say the Skill orchestrates confirmed artifact multi-view rendering while `imagegen` still executes generation.

### Task 5: Bind Evidence And Verify

- [ ] Add the new reference and script to the candidate source profile and recompute its repository-defined SHA-256 digest.
- [ ] Re-run the new prompts with only candidate sources loaded and compare against the baseline without changing criteria to force success.
- [ ] Run:

```bash
"$CODEX_BUNDLED_PYTHON" fiction-visual-designer/scripts/compose-design-sheet.py --self-test
python3 -m py_compile fiction-visual-designer/scripts/compose-design-sheet.py
scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json
ruby scripts/validate-skill-frontmatter.rb .
python3 scripts/audit-reference-indexes.py
scripts/audit-source-map.py
python3 scripts/validate-trigger-paths.py
./sync-skills.sh --dry-run fiction-visual-designer
scripts/validate.sh
git diff --check
```

Report targeted checks separately from full validation. Keep `FVD-001` open until real image generation, repeated baseline/candidate execution, blind review, and independent acceptance exist.
