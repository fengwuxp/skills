# Skills Top-Down CR Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bind Skill synchronization and delivery readiness to current behavior evidence, wire the missing novelist suite, reduce central-validator responsibility, and restore Level-1 metadata boundaries.

**Architecture:** `admission.json` remains the declared installability authority. Repository-relative evidence gates live outside hashed Skill source profiles in `fixtures/skill-eval/evidence-gates.json`, avoiding a self-referential digest. A dedicated evidence checker reuses `evaluate-skill-behavior.py` for source, response, blind, score, and release-gate verification; sync and static delivery reporting consume that checker. `validate-trigger-paths.py` keeps legacy trigger invariants but no longer owns behavior evidence freshness.

**Tech Stack:** Python standard library, Bash, JSON, YAML text, repository behavior fixtures and validators.

**Authority:** Current root `AGENTS.md` plus the accepted top-down CR findings. Preserve unrelated dirty-worktree changes. No Git, installation, synchronization, evidence relabeling, or response regeneration is authorized.

---

### Task 1: Evidence-Bound Sync Gate

**Files:**

- Create: `scripts/check-skill-evidence.py`
- Create: `scripts/test-check-skill-evidence.py`
- Create: `fixtures/skill-eval/evidence-gates.json`
- Modify: `sync-skills.sh`
- Modify: `scripts/evaluate-skills.py`
- Modify: `scripts/test-evaluate-skills.py`

- [ ] Write tests proving malformed evidence declarations fail, current source/response drift blocks, passing scored evidence succeeds, and a Skill with no evidence gates remains valid.
- [ ] Run the new tests and confirm RED because no evidence checker or sync integration exists.
- [ ] Implement a read-only evidence checker using the evaluator's existing validation, blinding, scoring, and `report.passed` result.
- [ ] Make sync call the checker before rsync and make `evaluate-skills.py` expose `evidence_readiness` in delivery gates.
- [ ] Bind document humanization, product business architecture, UI Ant adoption, and the six scored novelist suites through the external manifest without changing response, score, case, or source hashes.

### Task 2: Historical Closure Wiring

**Files:**

- Modify: `scripts/test-evaluate-skill-behavior.py`
- Modify: `scripts/validate.sh`

- [ ] Write a failing test that requires every `*-behavior-cases.json` suite to appear in `validate.sh`.
- [ ] Confirm RED for `novelist-historical-closure-behavior-cases.json`.
- [ ] Add its explicit `evaluate-skill-behavior.py validate` gate and rerun the test.

### Task 3: Separate Behavior Evidence From Trigger Contracts

**Files:**

- Modify: `scripts/validate-trigger-paths.py`
- Modify: `scripts/validate.sh`

- [ ] Remove behavior source/response/score freshness ownership from the central trigger validator where the new evidence checker is authoritative.
- [ ] Keep trigger ownership, routing, reference discovery, and high-value cross-Skill boundary assertions.
- [ ] Add the evidence checker to unified validation and verify existing trigger assertions still pass except independently stale evidence.

### Task 4: Level-1 Metadata Guard

**Files:**

- Create: `scripts/test-audit-skill-quality.py`
- Modify: `scripts/audit-skill-quality.py`
- Modify: `product-architecture-expert/agents/openai.yaml`
- Modify: `senior-software-architect/agents/openai.yaml`
- Modify: `scripts/validate-trigger-paths.py`

- [ ] Write tests that flag oversized or workflow-heavy `default_prompt` values while accepting short invocation prompts.
- [ ] Confirm RED because the quality audit only scans `SKILL.md`.
- [ ] Extend the audit to `agents/openai.yaml` without adding a YAML dependency.
- [ ] Shorten product and senior default prompts; keep detailed workflow and output structure in their Skill bodies/references.
- [ ] Update central metadata assertions to check identity and scope, not duplicated workflow terms.

### Task 5: Verification

- [ ] Run focused unit tests, evidence checks, all behavior contract validation, trigger validation, quality/security/source/reference audits, sync dry-runs, installed parity report, and `git diff --check`.
- [ ] Run `bash scripts/validate.sh`; stale real evidence may remain a deliberate blocker, but no structural or wiring failure may remain.
- [ ] Review the exact diff and report remaining evidence collection work separately from implemented code fixes.
