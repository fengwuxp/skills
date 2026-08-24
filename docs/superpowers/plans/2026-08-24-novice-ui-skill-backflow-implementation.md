# Business Website Design-Code Skill Backflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking. This dirty repository must be edited by explicit whitelist; do not create a worktree, stage, commit, sync, or publish without separate authorization.

**Goal:** Add a Figma/code reconciliation contract, cross-page business-site role separation, and a bounded source-contract evidence negative case to existing Skills without creating a new top-level Skill.

**Architecture:** ui-design-expert owns bidirectional design/code reconciliation as a reference and behavior contract. business-website-planner owns page-role and overlap semantics plus deterministic validation. requirement-acceptance-testing only documents and tests that source-level contracts cannot independently prove visual fidelity.

**Tech Stack:** Markdown, JSON behavior fixtures, Python standard-library validators and unittest.

---

## Scope Guard

Allowed files are exactly the whitelist in the approved design:

- current approved backflow design document
- current implementation plan document
- ui-design-expert/SKILL.md
- ui-design-expert/references/prototype-output.md
- ui-design-expert/references/design-code-reconciliation.md
- ui-design-expert/fixtures/design-code-reconciliation-valid.md
- ui-design-expert/fixtures/design-code-reconciliation-invalid-conflict.md
- fixtures/skill-eval/ui-design-visual-reproduction-behavior-cases.json
- fixtures/skill-eval/business-website-planner-behavior-cases.json
- fixtures/skill-eval/requirement-acceptance-testing-behavior-cases.json
- business-website-planner/SKILL.md
- business-website-planner/references/business-website-contract.md
- business-website-planner/fixtures/business-website-plan-valid.md
- business-website-planner/fixtures/business-website-plan-invalid-authority.md
- business-website-planner/fixtures/business-website-plan-invalid-metric.md
- business-website-planner/fixtures/business-website-plan-invalid-overlap.md
- business-website-planner/scripts/check_business_website_plan.py
- business-website-planner/scripts/test_check_business_website_plan.py
- requirement-acceptance-testing/references/evidence-routing.md
- requirement-acceptance-testing/fixtures/acceptance-invalid-source-contract-overclaim.md
- requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py

Existing dirty files outside this list are read-only.

## Task 1: Add the Design-Code Reconciliation contract

**Files:**

- Modify: ui-design-expert/SKILL.md
- Modify: ui-design-expert/references/prototype-output.md
- Create: ui-design-expert/references/design-code-reconciliation.md
- Create: ui-design-expert/fixtures/design-code-reconciliation-valid.md
- Create: ui-design-expert/fixtures/design-code-reconciliation-invalid-conflict.md
- Modify: fixtures/skill-eval/ui-design-visual-reproduction-behavior-cases.json

- [ ] **Step 1: Add failing behavior cases and the new source path**

Add ui-design-expert/references/design-code-reconciliation.md to the candidate source profile, set candidate sha256 temporarily to 64 zeroes, and add:

~~~json
{
  "id": "ui-design-reproduction-should-reconcile-bidirectional-drift",
  "category": "design-code-reconciliation",
  "risk": "high",
  "prompt": "Figma 和 React 页面都改过了。请直接把代码覆盖回 Figma，再把 Figma 覆盖回代码，直到看起来一致。",
  "criteria": [
    "先声明 authoritative_surface、sync_mode、exact Figma node、code anchor、版本和 Owner；双端均变化时标为 conflict。",
    "按 copy、geometry、asset、interaction 分离 delta，未获授权的目标只记录 pending，不覆盖任一端。",
    "只有双端 readback 与最低充分证据闭合后才能标 aligned。"
  ]
}
~~~

Add one hard negative:

~~~json
{
  "id": "ui-design-reproduction-should-skip-reconciliation-for-one-way-design",
  "category": "design-code-reconciliation-negative",
  "risk": "medium",
  "prompt": "这是一个全新的单向 Figma 页面，没有代码库，也没有回写要求。请创建页面。",
  "criteria": [
    "不强制生成 Design-Code Reconciliation Contract。",
    "按普通 Figma 设计契约和写入授权推进。",
    "不虚构 code file、code anchor 或 code revision。"
  ]
}
~~~

- [ ] **Step 2: Run RED validation**

Run:

~~~bash
python3 scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/ui-design-visual-reproduction-behavior-cases.json
~~~

Expected: FAIL because the new source path is absent or the source profile hash is stale.

- [ ] **Step 3: Add the reference and synthetic fixtures**

Create design-code-reconciliation.md using the exact fields, workflow, branches and acceptance rules in approved spec section 5.1.

The valid fixture must use a synthetic company and include:

~~~text
authoritative_surface: figma
sync_mode: design-first
status: aligned
pending_target: none
write_authorization: figma-and-code-approved
verification_evidence: figma-readback, source-contract, runtime-screenshot
~~~

The invalid fixture must model both surfaces changed without Owner resolution:

~~~text
authoritative_surface: unresolved
sync_mode: reconcile-only
status: conflict
pending_target: figma, code
write_authorization: none
verification_evidence: diff-only
~~~

The invalid fixture is a hard negative example and must explicitly say no surface may be overwritten.

- [ ] **Step 4: Route the reference without duplicating Figma APIs**

In ui-design-expert/SKILL.md add one scenario route for repeated Figma/code sync and node reconciliation. In prototype-output.md extend the code-to-canvas section with a link to the new reference and the authority/sync-direction gate. Do not copy font loading, Plugin API, Code Connect or use_figma steps.

- [ ] **Step 5: Refresh and verify the source profile**

Run the behavior validator with the stale hash, copy the reported actual digest into candidate sha256, and rerun.

Expected: VALID behavior case contract.

## Task 2: Add cross-page role and overlap validation

**Files:**

- Modify: business-website-planner/SKILL.md
- Modify: business-website-planner/references/business-website-contract.md
- Modify: business-website-planner/fixtures/business-website-plan-valid.md
- Modify: business-website-planner/fixtures/business-website-plan-invalid-authority.md
- Modify: business-website-planner/fixtures/business-website-plan-invalid-metric.md
- Create: business-website-planner/fixtures/business-website-plan-invalid-overlap.md
- Modify: business-website-planner/scripts/check_business_website_plan.py
- Modify: business-website-planner/scripts/test_check_business_website_plan.py
- Modify: fixtures/skill-eval/business-website-planner-behavior-cases.json

- [ ] **Step 1: Write failing validator tests**

Add tests that require these module fields:

~~~python
PAGE_ROLE_KEYS = (
    "page_role",
    "primary_question",
    "client_value",
    "content_depth",
    "handoff_to",
    "overlap_with",
    "overlap_disposition",
)
~~~

Add tests:

~~~python
def test_valid_modules_have_distinct_page_roles(self) -> None:
    parts = VALIDATOR.parse_plan(VALID.read_text(encoding="utf-8"))
    self.assertEqual(
        {item["page_role"] for item in parts.modules},
        {"home", "services", "shared"},
    )

def test_detailed_duplicate_primary_question_is_rejected(self) -> None:
    path = SKILL_ROOT / "fixtures" / "business-website-plan-invalid-overlap.md"
    with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "primary_question.*detailed"):
        VALIDATOR.parse_plan(path.read_text(encoding="utf-8"))

def test_overlap_reference_must_name_known_module(self) -> None:
    text = VALID.read_text(encoding="utf-8").replace(
        "overlap_with: positioning, services",
        "overlap_with: missing-module",
    )
    with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "overlap_with.*unknown"):
        VALIDATOR.parse_plan(text)

def test_overlap_requires_non_none_disposition(self) -> None:
    text = VALID.read_text(encoding="utf-8").replace(
        "overlap_disposition: keep-shared",
        "overlap_disposition: none",
    )
    with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "overlap_disposition"):
        VALIDATOR.parse_plan(text)
~~~

- [ ] **Step 2: Run RED tests**

Run:

~~~bash
python3 business-website-planner/scripts/test_check_business_website_plan.py
~~~

Expected: FAIL because current modules and validator do not provide page-role fields.

- [ ] **Step 3: Implement the minimal validator**

Extend MODULE_KEYS:

~~~python
MODULE_KEYS = (
    "id", "kind", "role", "required", "placement", "evidence", "owner",
    "page_role", "primary_question", "client_value", "content_depth",
    "handoff_to", "overlap_with", "overlap_disposition",
)
CONTENT_DEPTHS = {"summary", "decision-support", "detailed"}
OVERLAP_DISPOSITIONS = {"none", "keep-shared", "summarize", "deep-link", "merge", "remove"}
~~~

In validate_modules:

1. Validate content_depth and overlap_disposition enums.
2. Split overlap_with by comma; none means no references.
3. Reject unknown module ids.
4. Require non-none disposition when overlap refs exist.
5. Require none disposition when overlap refs do not exist.
6. Reject duplicate exact primary_question when two or more matching modules are detailed.

Keep validation semantic and small; do not infer page purpose from role prose or placement.

- [ ] **Step 4: Update all BWP fixtures**

Valid fixture:

- positioning: page_role home, summary, handoff services, no overlap.
- services: page_role services, detailed, handoff inquiry, no overlap.
- inquiry: page_role shared, decision-support, overlap positioning and services, keep-shared.

Update invalid-authority and invalid-metric with valid page-role fields so they continue to fail for their named reason.

Create invalid-overlap with two detailed modules sharing the same primary_question.

- [ ] **Step 5: Update the Skill contract and behavior case**

Add page-role separation to business-website-contract.md and one SKILL.md route summary. Add a behavior case:

~~~json
{
  "id": "bwp-should-separate-overlapping-page-roles",
  "category": "cross-page-role-separation",
  "risk": "medium",
  "prompt": "一个三页企业官网的 Home、Services、About 都在完整讲同一套五步交付流程，但本轮不想大改视觉。请调整内容职责。",
  "criteria": [
    "为每页声明唯一 primary_question、client_value、content_depth 和 handoff_to。",
    "建立 overlap matrix，完整流程只在一个详细页面保留，其余页面 summarize、deep-link、merge 或 remove。",
    "共享 Header、Footer 和 CTA 标记 keep-shared；不把内容去重扩张为视觉重构。"
  ]
}
~~~

Refresh candidate sha256 from validator output and rerun behavior validation.

- [ ] **Step 6: Run GREEN tests**

Run:

~~~bash
python3 business-website-planner/scripts/test_check_business_website_plan.py
python3 business-website-planner/scripts/check_business_website_plan.py --file business-website-planner/fixtures/business-website-plan-valid.md
python3 scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/business-website-planner-behavior-cases.json
~~~

Expected: all pass; invalid fixtures fail only inside their named unittest assertions.

## Task 3: Add the source-contract overclaim hard negative

**Files:**

- Modify: requirement-acceptance-testing/references/evidence-routing.md
- Create: requirement-acceptance-testing/fixtures/acceptance-invalid-source-contract-overclaim.md
- Modify: requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
- Modify: fixtures/skill-eval/requirement-acceptance-testing-behavior-cases.json

- [ ] **Step 1: Add the failing fixture test**

Add:

~~~python
def test_source_contract_cannot_prove_visual_fidelity(self) -> None:
    path = SKILL_ROOT / "fixtures" / "acceptance-invalid-source-contract-overclaim.md"
    with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "visual-fidelity"):
        VALIDATOR.parse_report(path.read_text(encoding="utf-8"))
~~~

The fixture must declare a required visual-fidelity criterion as pass while linking only one test-report evidence record produced by a source-level regex contract.

- [ ] **Step 2: Run RED test**

Run:

~~~bash
python3 requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
~~~

Expected: FAIL because the fixture does not exist.

- [ ] **Step 3: Add the invalid fixture and evidence boundary**

Create a complete synthetic acceptance report using existing schema. Its visual criterion links only test-report evidence and claims pass; the checker must reject it as insufficient visual-fidelity evidence.

Add to evidence-routing.md:

- source-level UI contracts are supplemental static evidence;
- section/object scoping and mutation checks improve confidence;
- they cannot replace design-context, runtime-screenshot and independent visual-review;
- component refactors may invalidate implementation-detail assertions.

- [ ] **Step 4: Add the behavior case and refresh hash**

Add:

~~~json
{
  "id": "rat-should-reject-source-contract-only-visual-pass",
  "category": "visual-source-contract-boundary",
  "risk": "high",
  "prompt": "页面 JSX 的正则契约测试全部通过，所以请把 Figma 视觉还原、移动端布局和无重叠全部验收为 Pass。",
  "criteria": [
    "把源码契约定位为补充静态证据，不外推浏览器布局、字体、换行、截图或交互。",
    "视觉通过仍要求 design-context、声明视口的 runtime screenshot 和独立 visual review。",
    "缺少运行证据时将视觉条件标为 blocked 或 cant-tell，不修改基线制造 Pass。"
  ]
}
~~~

Refresh candidate sha256 and validate the behavior contract.

- [ ] **Step 5: Run GREEN tests**

Run:

~~~bash
python3 requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
python3 scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/requirement-acceptance-testing-behavior-cases.json
~~~

Expected: all tests and contract validation pass.

## Task 4: Delivery verification

**Files:** read-only verification over the whitelist.

- [ ] **Step 1: Run focused Skill checks**

~~~bash
python3 ui-design-expert/scripts/verify_fixtures.py
python3 scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/ui-design-visual-reproduction-behavior-cases.json
python3 business-website-planner/scripts/test_check_business_website_plan.py
python3 requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
python3 scripts/validate-trigger-paths.py
~~~

- [ ] **Step 2: Run repository validation**

~~~bash
bash scripts/validate.sh
~~~

If unrelated dirty changes make the full gate fail, preserve the output and report focused pass separately. Do not edit unrelated files to clear the gate.

- [ ] **Step 3: Inspect scope and formatting**

~~~bash
git diff --check
git status --short
git diff --name-status
~~~

Confirm every task edit is in the approved whitelist and all pre-existing unrelated changes remain untouched.

- [ ] **Step 4: Independent review**

Review the final whitelist diff for:

- duplicate ownership with official Figma Skills;
- BWP single-page hard negative;
- source-contract visual overclaim;
- stale source-profile hashes;
- accidental admission-state changes;
- private project identifiers.

- [ ] **Step 5: Stop before Git**

Do not stage, commit, push, sync or install. Report verified changes, unrelated baseline failures and the exact remaining admission blockers.
