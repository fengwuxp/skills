# Business Website Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Repository rules keep this execution inline; do not dispatch subagents unless the user separately authorizes them.

**Goal:** Create the candidate `business-website-planner` Skill, add deterministic contract checks and behavior fixtures, route it through `wise-agent`, and strengthen `ui-design-expert` with one authoritative Responsive Media Contract whose default website design carrier is Figma.

**Architecture:** The new Skill owns only the Business Website Contract. Business facts remain with product capabilities, detailed responsive/UI rules remain with `ui-design-expert`, Figma is the default design carrier after explicit write authorization, engineering remains with `senior-software-architect`, and acceptance remains independent. The package starts as `candidate` and stays explicit-only until behavior evidence and three business-type pilots close its blockers.

**Tech Stack:** Markdown Skill packages, YAML/JSON metadata, Python 3 standard library validators, repository behavior-evaluation scripts, Figma/UI reference contracts.

**Git boundary:** The user authorized source changes but not Git commit, sync, or publication. Commit steps are intentionally omitted.

---

## File Map

### Create

- `business-website-planner/SKILL.md`: concise trigger, responsibility, workflow, routing, output and red lines.
- `business-website-planner/admission.json`: explicit-only candidate blockers.
- `business-website-planner/agents/openai.yaml`: UI metadata and invocation policy.
- `business-website-planner/references/business-website-contract.md`: plan schema, suggested modules, simple metric suggestions and handoff contract.
- `business-website-planner/references/business-type-patterns.md`: twelve common business adapters.
- `business-website-planner/references/reference-research-and-distinctiveness.md`: public-reference reading and non-copying method.
- `business-website-planner/references/source-map.md`: verified public sources and absorption boundaries.
- `business-website-planner/fixtures/business-website-plan-valid.md`: positive structured contract.
- `business-website-planner/fixtures/business-website-plan-invalid-metric.md`: unconfirmed reference example published as fact.
- `business-website-planner/fixtures/business-website-plan-invalid-authority.md`: missing business authority.
- `business-website-planner/scripts/test_check_business_website_plan.py`: contract tests.
- `business-website-planner/scripts/check_business_website_plan.py`: offline validator.
- `fixtures/skill-eval/business-website-planner-behavior-cases.json`: candidate behavior contract.
- `fixtures/skill-eval/ui-design-responsive-media-behavior-cases.json`: UI responsive-media behavior contract.

### Modify

- `docs/superpowers/specs/2026-08-22-business-website-planner-design.md`: preserve Figma as the confirmed default design carrier.
- `ui-design-expert/SKILL.md`: route responsive media to its foundation reference.
- `ui-design-expert/references/design-foundations.md`: authoritative Responsive Media Contract.
- `ui-design-expert/references/source-map.md`: MDN, web.dev and Next.js source boundaries.
- `fixtures/skill-eval/evidence-gates.json`: add contract-only evidence gates.
- `fixtures/skill-eval/prompt-cases.json`: add realistic positive and hard-negative trigger cases.
- `scripts/audit-skill-eval-fixtures.py`: register Skill ID, display aliases and candidate explicit-only policy.
- `scripts/evaluate-skills.py`: register explicit-only candidate aliases.
- `scripts/validate.sh`: compile and run validator/tests and behavior contracts.
- `scripts/validate-trigger-paths.py`: add only durable ownership/routing checks.
- `wise-agent/references/capability-routing.md`: add the new professional route and collaboration boundary.
- `README.md`: add the candidate capability entry.

## Task 1: Contract Tests and Fixtures

**Files:**

- Create: `business-website-planner/fixtures/business-website-plan-valid.md`
- Create: `business-website-planner/fixtures/business-website-plan-invalid-metric.md`
- Create: `business-website-planner/fixtures/business-website-plan-invalid-authority.md`
- Create: `business-website-planner/scripts/test_check_business_website_plan.py`

- [x] **Step 1: Create the positive contract fixture**

Use six fenced blocks: `business-website-plan`, `website-modules`, `metric-suggestions`, `reference-dna`, `responsive-media`, and `website-handoff`.

The contract block must contain these exact fields:

```text
plan_id: BWP-DEMO-001
business_authority: owner-approved-business-brief-v1.md
business_type: advertising-services
company_subject: Example Advertising Services Limited
target_customers: B2B marketing teams
business_scope: campaign planning and coordination
non_goals: media budget custody, direct ad account operation, production release
organization_mode: core-plus-conditional
design_carrier: figma
design_carrier_override: none
owner: business-owner
status: ready-for-ui
```

The fixture must demonstrate that modules are suggestions rather than fixed pages, include three metrics with `reference_example_value` and `owner_confirmed_value`, include one actually read public reference with adopt/reject fields, and include responsive-media records for a decorative hero and a semantic business image.

- [x] **Step 2: Create the two negative fixtures**

`business-website-plan-invalid-authority.md` leaves `business_authority` empty.

`business-website-plan-invalid-metric.md` contains:

```text
[metric]
name: Advertising engagements
business_meaning: Shows operating experience
reference_example_value: 50+
owner_confirmed_value: none
publish: true
[/metric]
```

- [x] **Step 3: Write tests before the validator exists**

The test module imports `check_business_website_plan.py` with `importlib.util` and defines these tests:

```python
def test_valid_business_website_plan_passes(): ...
def test_missing_business_authority_is_rejected(): ...
def test_unconfirmed_reference_example_cannot_publish(): ...
def test_modules_are_suggestions_not_fixed_pages(): ...
def test_figma_is_default_without_explicit_override(): ...
def test_explicit_non_figma_override_is_allowed(): ...
def test_public_reference_requires_read_status_adopt_and_reject(): ...
def test_responsive_media_requires_mobile_and_large_screen_viewports(): ...
```

- [x] **Step 4: Run the tests and confirm RED**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 business-website-planner/scripts/test_check_business_website_plan.py
```

Expected: import failure because `check_business_website_plan.py` does not exist.

## Task 2: Minimal Offline Validator

**Files:**

- Create: `business-website-planner/scripts/check_business_website_plan.py`
- Test: `business-website-planner/scripts/test_check_business_website_plan.py`

- [x] **Step 1: Implement the parser with the Python standard library**

Use the established repository pattern:

```python
BLOCK_PATTERN = re.compile(
    r"```(?P<tag>business-website-plan|website-modules|metric-suggestions|reference-dna|responsive-media|website-handoff)\s*\n(?P<body>.*?)```",
    re.DOTALL,
)
RECORD_PATTERNS = {
    "module": re.compile(r"\[module\]\s*(?P<body>.*?)\s*\[/module\]", re.DOTALL),
    "metric": re.compile(r"\[metric\]\s*(?P<body>.*?)\s*\[/metric\]", re.DOTALL),
    "reference": re.compile(r"\[reference\]\s*(?P<body>.*?)\s*\[/reference\]", re.DOTALL),
    "media": re.compile(r"\[media\]\s*(?P<body>.*?)\s*\[/media\]", re.DOTALL),
}
```

Return a frozen dataclass with contract, module, metric, reference, media and handoff values.

- [x] **Step 2: Enforce only the approved contract invariants**

Implement these rules without a generalized schema framework:

```python
if not contract["business_authority"].strip():
    raise WebsitePlanError("business_authority is required")
if contract["design_carrier_override"].casefold() == "none" and contract["design_carrier"] != "figma":
    raise WebsitePlanError("figma is the default design_carrier")
if metric["publish"] == "true" and is_empty(metric["owner_confirmed_value"]):
    raise WebsitePlanError(f"metric[{metric['name']}] cannot publish a reference example")
```

Require at least one suggested module, but do not require Home, Business, About or Contact as four fixed pages. Require public references to contain `source`, `read_status`, `adopt`, `reject` and `limitations`. Require each media record to declare role, source, focal point, crop variants, target viewports and owner. The aggregate target viewports must include mobile plus at least one of 1920, 2560 or 3440.

- [x] **Step 3: Add the CLI**

Use:

```bash
python3 business-website-planner/scripts/check_business_website_plan.py --file plan.md
```

The CLI prints `VALID business website plan: <path>` on structural success and returns `2` on invalid input. Its module docstring must state that it is offline, read-only and does not judge business truth, visual quality, legal sufficiency or production readiness.

- [x] **Step 4: Run tests and confirm GREEN**

Run the Task 1 command.

Expected: all tests pass with no warnings.

## Task 3: Candidate Skill Package

**Files:**

- Create: `business-website-planner/SKILL.md`
- Create: `business-website-planner/admission.json`
- Create: `business-website-planner/agents/openai.yaml`
- Create: `business-website-planner/references/business-website-contract.md`
- Create: `business-website-planner/references/business-type-patterns.md`
- Create: `business-website-planner/references/reference-research-and-distinctiveness.md`
- Create: `business-website-planner/references/source-map.md`

- [x] **Step 1: Write concise metadata**

Use this frontmatter:

```yaml
---
name: business-website-planner
description: |
  用户要求从零规划或重构用于说明和辅助佐证公司真实业务的企业官网，并需要按广告、代采购、电商、SaaS、制造、物流等业务类型梳理定位、建议模块、内容、指标参考示例值、公开参考差异、图片多屏要求、联系方式或按需 Legal 页面时触发。单纯 UI/Figma、建站编码、商城交易、SEO 或法律文本不触发。
---
```

- [x] **Step 2: Write `SKILL.md` as a route, not a second coordinator**

Keep the body under 160 lines and include:

- candidate explicit-only status;
- business-authority gate;
- suggested module selection;
- business adapter selection;
- simple metric suggestions;
- public-reference and non-copying gate;
- Figma as the default design carrier unless explicitly overridden;
- responsive-media handoff to `ui-design-expert`;
- product, UI, engineering, acceptance, payment, security and document boundaries;
- output contract and stop conditions.

Link every reference at the point where it is needed. Do not copy detailed UI, payment, security or engineering rules into this Skill.

- [x] **Step 3: Write the three method references and source map**

`business-website-contract.md` owns the plan fields, suggested modules, simple metric table and handoff format.

`business-type-patterns.md` owns the twelve business adapters. Each adapter uses the same compact headings: business questions, proof material, metric suggestions, image focus, conditional modules and overclaim risks.

`reference-research-and-distinctiveness.md` owns actual-body reading, Content/Layout/Visual/Interaction DNA, adopt/reject rationale and non-copying boundaries.

`source-map.md` records the sources from the approved spec with read date `2026-08-22` and states what was not absorbed.

- [x] **Step 4: Add candidate admission and UI metadata**

Use blocker IDs:

```json
{
  "status": "candidate",
  "updated_at": "2026-08-22",
  "blockers": [
    {"id": "BWP-001", "summary": "baseline/candidate repeated responses and independent blind judgments are missing", "owner": "repository Owner / independent Checker"},
    {"id": "BWP-002", "summary": "advertising-services real-task pilot is missing", "owner": "business Owner / UI Owner"},
    {"id": "BWP-003", "summary": "sourcing or supply-chain real-task pilot is missing", "owner": "business Owner / product Owner"},
    {"id": "BWP-004", "summary": "ecommerce or marketplace real-task pilot is missing", "owner": "business Owner / product Owner"},
    {"id": "BWP-005", "summary": "responsive-media behavior and browser evidence are missing", "owner": "UI Owner / acceptance Checker"}
  ]
}
```

Set `allow_implicit_invocation: false`. The default prompt must explicitly invoke `$business-website-planner`.

- [x] **Step 5: Run package checks**

Run:

```bash
ruby scripts/validate-skill-frontmatter.rb business-website-planner
python3 scripts/check-skill-admission.py --status business-website-planner
python3 scripts/audit-skill-security.py --root business-website-planner --ignore-local-generated-pyc
```

Expected: frontmatter valid, status `candidate`, security scan passes.

## Task 4: Skill Behavior and Trigger Fixtures

**Files:**

- Create: `fixtures/skill-eval/business-website-planner-behavior-cases.json`
- Modify: `fixtures/skill-eval/prompt-cases.json`
- Modify: `fixtures/skill-eval/evidence-gates.json`
- Modify: `scripts/audit-skill-eval-fixtures.py`
- Modify: `scripts/evaluate-skills.py`

- [x] **Step 1: Create behavior cases before wiring the gate**

Create six cases:

```text
bwp-should-plan-advertising-business-website
bwp-should-plan-sourcing-business-website
bwp-should-plan-ecommerce-business-website
bwp-should-derive-other-business-type
bwp-should-block-unconfirmed-reference-metric
bwp-should-not-copy-reference-website
```

The candidate source profile paths are:

```json
[
  "business-website-planner/SKILL.md",
  "business-website-planner/admission.json",
  "business-website-planner/references/business-website-contract.md",
  "business-website-planner/references/business-type-patterns.md",
  "business-website-planner/references/reference-research-and-distinctiveness.md"
]
```

Compute the source hash with the repository source-set algorithm after all five files are stable. Static behavior cases are contract evidence only; do not add fabricated responses or scores.

- [x] **Step 2: Add four prompt cases**

Add two explicit positives:

- an advertising website with confirmed business facts and Figma-default handoff;
- a sourcing website needing suggested modules, metrics, proof media and public-reference differentiation.

Add two hard negatives:

- direct Figma drawing or Figma-to-code, preferred `ui-design-expert` or engineering/Figma capability;
- checkout, order, payment and refund product design, preferred `product-architecture-expert` plus `payment-expert`.

- [x] **Step 3: Register explicit-only fixture policy**

Add `business-website-planner` to the Skill sets and aliases in both evaluator scripts. All positive prompts must contain `$business-website-planner` or the exact Skill ID.

- [x] **Step 4: Add a contract-only evidence gate**

Append:

```json
"business-website-planner": [
  {"cases": "fixtures/skill-eval/business-website-planner-behavior-cases.json"}
]
```

- [x] **Step 5: Validate fixtures**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/business-website-planner-behavior-cases.json
env PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit-skill-eval-fixtures.py
env PYTHONDONTWRITEBYTECODE=1 python3 scripts/evaluate-skills.py --self-test
env PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-skill-evidence.py --skill business-website-planner
```

Expected: all commands pass; admission remains candidate because real behavior evidence and pilots are intentionally missing.

## Task 5: UI Responsive Media Authority

**Files:**

- Modify: `ui-design-expert/SKILL.md`
- Modify: `ui-design-expert/references/design-foundations.md`
- Modify: `ui-design-expert/references/source-map.md`
- Create: `fixtures/skill-eval/ui-design-responsive-media-behavior-cases.json`
- Modify: `fixtures/skill-eval/evidence-gates.json`

- [x] **Step 1: Write the behavior contract first**

Create cases for:

```text
ui-responsive-media-should-separate-art-direction-and-resolution
ui-responsive-media-should-protect-semantic-business-images
ui-responsive-media-should-handle-ultrawide-focal-safety
ui-responsive-media-should-use-container-context-for-reusable-media
ui-responsive-media-should-not-force-background-images
```

The expected behavior must cover browser clients only: desktop, ultrawide, mobile/H5, responsive Web and embedded WebView. Native app, mini-program and native desktop are routed out.

- [x] **Step 2: Add the single authoritative reference section**

Add `## Responsive Media Contract` to `design-foundations.md` with:

- semantic image versus decorative background decision;
- media query versus container query;
- Art Direction via `<picture>`;
- Resolution Switching via `srcset + sizes` and `image-set()`;
- aspect ratio, object-fit, object-position and focal-point tokens;
- background cover only when cropping cannot remove business meaning;
- target viewport matrix including 1280, 1440, 1920, 2560, 3440 and mobile;
- source resolution, 1x/2x, LCP and layout-shift checks;
- business-specific rules for advertising, sourcing, ecommerce, SaaS, manufacturing, logistics and maps/documents.

`SKILL.md` only routes to this section; it does not duplicate the rules.

- [x] **Step 3: Add official source entries**

Record MDN responsive images, `<picture>`, container queries, web.dev responsive images/aspect ratio and Next.js image optimization. Mark Next.js as a time-sensitive implementation example rather than stable UI authority.

- [x] **Step 4: Add the contract-only UI evidence gate and validate**

Run the behavior validator and `check-skill-evidence.py --skill ui-design-expert`. Do not create scored responses or claim live behavior improvement.

## Task 6: Repository Routing and Validation

**Files:**

- Modify: `wise-agent/references/capability-routing.md`
- Modify: `README.md`
- Modify: `scripts/validate-trigger-paths.py`
- Modify: `scripts/validate.sh`

- [x] **Step 1: Add the capability route**

The route must state:

```text
Signal: planning or redesigning a business website to explain and support evidence of real company activity across common business types
Owner: candidate business-website-planner, explicit-only until admission passes
Consumes: product-architecture-expert for unconfirmed business facts
Hands off: ui-design-expert, Figma by default, senior-software-architect, requirement-acceptance-testing
Evidence: business authority, suggested modules, confirmed metrics, reference DNA, responsive media brief and Owner review
```

- [x] **Step 2: Add the README candidate entry**

Name the Skill, link the directory, state the candidate blockers, summarize minimum input and state that Figma is the default design carrier unless explicitly overridden.

- [x] **Step 3: Add only durable trigger checks**

`validate-trigger-paths.py` should verify existence, ownership terms, Figma-default wording, suggested-module wording, reference-example-value wording and UI responsive-media routing. Do not reintroduce exact behavior artifact fingerprints into this legacy routing checker; those belong to `check-skill-evidence.py`.

- [x] **Step 4: Wire unified validation**

Add Python compilation, validator tests, valid fixture check and both new behavior-contract validations to `scripts/validate.sh` through `run_gate` where deferred evidence failures must not stop later checks.

## Task 7: Verification and Review

**Files:** all files above.

- [x] **Step 1: Run targeted validation**

Run the validator tests, valid fixture, both behavior fixtures, prompt fixture audit, Skill evaluation self-test, frontmatter, admission, security scan and `git diff --check`.

- [x] **Step 2: Run the full repository validator**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 scripts/validate.sh
```

Report new-scope failures separately from pre-existing deferred evidence failures. Do not modify unrelated novelist, product, UI Ant Design or other user changes.

- [x] **Step 3: Confirm candidate sync guard**

Run:

```bash
./sync-skills.sh --dry-run all
```

Expected: `business-website-planner` is skipped because admission status is candidate. No installation writes occur.

- [x] **Step 4: Review the scoped diff**

Check every changed line maps to the approved spec. Confirm no generated `__pycache__`, private thread text, customer data, copied external content, Figma mutation, Git staging, commit, sync or publication occurred.

## Execution Result

- Business Website Contract tests: 18 passed, including the four post-CR contract fixes.
- Positive contract CLI, frontmatter, admission, security, source-map, prompt fixture, Skill evaluation and BWP evidence gates: passed.
- Business website behavior cases: 6 passed contract validation.
- UI Responsive Media behavior cases: 5 passed contract validation.
- Trigger-path validation: passed.
- Candidate sync dry-run: `business-website-planner` skipped as designed; no installation write occurred.
- Full repository validation reached the end but returned deferred failures from pre-existing novelist source drift and the existing UI Ant Design scored evidence gate. The new BWP and Responsive Media checks passed.
- Git stage, commit, push, Figma mutation, installation and publication were not performed.
- Post-CR fixes: non-Figma override now requires `user-specified-*`; `reference_mode` supports legitimate no-reference tasks; reference example values and handoff owners reject unresolved placeholders.
