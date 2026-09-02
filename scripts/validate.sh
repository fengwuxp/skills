#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

validation_failed=0
run_gate() {
  if ! "$@"; then
    validation_failed=1
  fi
}

echo "==> bash syntax"
bash -n sync-skills.sh
bash -n scripts/audit-skills.sh
bash -n scripts/validate-installed-skills.sh
bash -n scripts/smoke-wise-agent-behavior.sh
bash -n scripts/validate-superpowers-install.sh
bash -n wise-agent/scripts/check_dirty_worktree_commit.sh

echo "==> Codex agent TOML"
python3 scripts/validate-codex-agent-profiles.py --self-test
python3 scripts/validate-codex-agent-profiles.py --source-dir .codex/agents

echo "==> skill audit"
scripts/audit-skills.sh

echo "==> internal project keyword guard"
internal_project_pattern='no''be|cap''te|fin''cone|wind-inte''gration|wind-fu''nds|blue-pow''der'
if rg -n -i --hidden \
  --glob '!.git/**' \
  --glob '!.idea/**' \
  --glob '!.serena/**' \
  --glob '!**/__pycache__/**' \
  "${internal_project_pattern}" .; then
  echo "FAIL internal project keyword found in Skill repository" >&2
  exit 1
fi
if rg --files --hidden \
  --glob '!.git/**' \
  --glob '!.idea/**' \
  --glob '!.serena/**' \
  --glob '!**/__pycache__/**' | rg -n -i "${internal_project_pattern}"; then
  echo "FAIL internal project keyword found in Skill repository path" >&2
  exit 1
fi

echo "==> skill frontmatter and agent yaml"
ruby scripts/test-validate-skill-frontmatter.rb
ruby scripts/validate-skill-frontmatter.rb .
ruby <<'RB'
require "yaml"

Dir.glob("*/SKILL.md").sort.each do |skill_md|
  text = File.read(skill_md, encoding: "UTF-8")
  match = text.match(/\A---\n(.*?)\n---\n/m)
  abort("#{skill_md}: missing YAML frontmatter") unless match
  data = YAML.safe_load(match[1], aliases: true) || {}
  %w[name description].each do |key|
    abort("#{skill_md}: missing #{key}") if data[key].to_s.strip.empty?
  end
  skill_dir = File.basename(File.dirname(skill_md))
  skill_name = data["name"].to_s.strip
  unless skill_name.match?(/\A[a-z0-9]+(?:-[a-z0-9]+)*\z/)
    abort("#{skill_md}: invalid skill id #{skill_name.inspect}; use lowercase letters, digits, and hyphens")
  end
  abort("#{skill_md}: name #{skill_name.inspect} must match directory #{skill_dir.inspect}") unless skill_name == skill_dir
  agent = File.join(File.dirname(skill_md), "agents", "openai.yaml")
  if File.exist?(agent)
    agent_data = YAML.load_file(agent) || {}
    default_prompt = agent_data.dig("interface", "default_prompt").to_s
    abort("#{agent}: default_prompt must invoke $#{skill_name}") unless default_prompt.include?("$#{skill_name}")
  end
  puts "OK #{skill_md}"
end

route_files = Dir.glob("*/SKILL.md") + ["wise-agent/references/capability-routing.md"]
forbidden_display_ids = ["`产品架构专家`", "`资深架构师`", "$产品架构专家", "$资深架构师"]
route_files.uniq.each do |path|
  text = File.read(path, encoding: "UTF-8")
  forbidden_display_ids.each do |term|
    abort("#{path}: use stable Skill ID instead of display name #{term.inspect}") if text.include?(term)
  end
end
RB

echo "==> reference links"
python3 - <<'PY'
from pathlib import Path
import re

root = Path(".")
missing = []
for skill_md in sorted(root.glob("*/SKILL.md")):
    skill_dir = skill_md.parent
    text = skill_md.read_text(encoding="utf-8")
    refs = sorted(set(re.findall(r"`(references/[^`]+)`", text)))
    for ref in refs:
        if not (skill_dir / ref).exists():
            missing.append(f"{skill_md}: {ref}")
    print(f"OK {skill_md} references={len(refs)}")
if missing:
    raise SystemExit("Missing references:\n" + "\n".join(missing))
PY

echo "==> trigger paths"
run_gate python3 scripts/validate-trigger-paths.py

echo "==> grill-me install validator"
python3 scripts/validate-grill-me-install.py --self-test
python3 scripts/test-grill-me-process-assets.py
run_gate scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/grill-me-resolution-and-intent-behavior-cases.json
if [[ "${VALIDATE_GRILL_ME_INSTALL:-}" == "1" ]]; then
  python3 scripts/validate-grill-me-install.py
fi

echo "==> Superpowers install validator"
scripts/validate-superpowers-install.sh --self-test
if [[ "${VALIDATE_SUPERPOWERS_INSTALL:-}" == "1" ]]; then
  scripts/validate-superpowers-install.sh
fi

echo "==> wise-agent behavior smoke parser"
scripts/smoke-wise-agent-behavior.sh --self-test

echo "==> agent output actionability behavior cases"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/agent-output-actionability-behavior-cases.json"

echo "==> wise-agent state contract"
python3 wise-agent/scripts/check_state_contract.py --self-test

echo "==> wise-agent dirty-worktree commit fixture"
wise-agent/scripts/check_dirty_worktree_commit.sh --self-test

echo "==> wise-agent skill learning ledger"
python3 wise-agent/scripts/skill-learning-ledger.py --self-test

echo "==> wise-agent user collaboration profile"
python3 wise-agent/scripts/user-context-ledger.py --self-test

echo "==> wise-agent reference section reader"
python3 wise-agent/scripts/read-reference-sections.py --self-test
python3 scripts/test-read-reference-sections-integration.py

echo "==> wise-agent skill usage observability"
python3 wise-agent/scripts/skill-usage-observability.py --self-test
python3 wise-agent/scripts/test_skill_usage_observability.py

echo "==> python compile"
python3 -m py_compile business-website-planner/scripts/check_business_website_plan.py
python3 -m py_compile business-website-planner/scripts/test_check_business_website_plan.py
python3 -m py_compile document-authoring/scripts/check_document_deliverable.py
python3 -m py_compile document-authoring/scripts/check_document_style.py
python3 -m py_compile fiction-visual-designer/scripts/compose-design-sheet.py
python3 -m py_compile hanzi-philology/scripts/check_philology_evidence.py
python3 -m py_compile java-service-code-generator/scripts/generate_scaffold.py
python3 -m py_compile payment-expert/scripts/check_external_rules.py
python3 -m py_compile payment-expert/scripts/test_verify_behavior_cases.py
python3 -m py_compile payment-expert/scripts/verify_behavior_cases.py
python3 -m py_compile payment-expert/scripts/verify_fixtures.py
python3 -m py_compile product-architecture-expert/scripts/check_product_deliverable.py
python3 -m py_compile product-architecture-expert/scripts/check_product_qualification.py
python3 -m py_compile product-architecture-expert/scripts/check_prd_readability_evaluation.py
python3 -m py_compile product-architecture-expert/scripts/test_check_prd_readability_evaluation.py
python3 -m py_compile product-architecture-expert/scripts/test_check_product_qualification.py
python3 -m py_compile product-architecture-expert/scripts/verify_fixtures.py
python3 -m py_compile requirement-acceptance-testing/scripts/check_requirement_acceptance.py
python3 -m py_compile requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
python3 -m py_compile resource-capability-distiller/scripts/check_capability_candidate.py
python3 -m py_compile security-engineering-expert/scripts/check_security_deliverable.py
python3 -m py_compile senior-software-architect/scripts/check_architecture_deliverable.py
python3 -m py_compile senior-software-architect/scripts/check_harness_plan.py
python3 -m py_compile senior-software-architect/scripts/check_system_intervention_card.py
python3 -m py_compile senior-software-architect/scripts/test_check_system_intervention_card.py
python3 -m py_compile senior-software-architect/scripts/verify_fixtures.py
python3 -m py_compile ui-design-expert/scripts/check_ui_design_deliverable.py
python3 -m py_compile ui-design-expert/scripts/check_design_draft_review.py
python3 -m py_compile ui-design-expert/scripts/test_check_design_draft_review.py
python3 -m py_compile ui-design-expert/scripts/check_figma_design_plan.py
python3 -m py_compile ui-design-expert/scripts/test_check_figma_design_plan.py
python3 -m py_compile ui-design-expert/scripts/check_ui_source.py
python3 -m py_compile ui-design-expert/scripts/verify_fixtures.py
python3 -m py_compile wind-coding-conventions/scripts/check_wind_conventions.py
python3 -m py_compile wise-agent/scripts/check_state_contract.py
python3 -m py_compile wise-agent/scripts/read-reference-sections.py
python3 -m py_compile scripts/test-read-reference-sections-integration.py
python3 -m py_compile wise-agent/scripts/skill-learning-ledger.py
python3 -m py_compile wise-agent/scripts/skill-usage-observability.py
python3 -m py_compile wise-agent/scripts/test_skill_usage_observability.py
python3 -m py_compile wise-agent/scripts/user-context-ledger.py
python3 -m py_compile scripts/audit-reference-indexes.py
python3 -m py_compile scripts/check-skill-admission.py
python3 -m py_compile scripts/test-check-skill-admission.py
python3 -m py_compile scripts/check-skill-evidence.py
python3 -m py_compile scripts/test-check-skill-evidence.py
python3 -m py_compile scripts/audit-skill-security.py
python3 -m py_compile scripts/test-audit-skill-security.py
python3 -m py_compile scripts/audit-skill-quality.py
python3 -m py_compile scripts/test-audit-skill-quality.py
python3 -m py_compile scripts/audit-skill-eval-fixtures.py
python3 -m py_compile scripts/archive-source-evidence.py
python3 -m py_compile scripts/audit-source-map.py
python3 -m py_compile scripts/evaluate-skill-behavior.py
python3 -m py_compile scripts/test-evaluate-skill-behavior.py
python3 -m py_compile novelist/scripts/check-novelist-continuity-ledger.py
python3 -m py_compile novelist/scripts/check-novelist-timeline.py
python3 -m py_compile scripts/evaluate-skills.py
python3 -m py_compile scripts/test-evaluate-skills.py
python3 -m py_compile scripts/skillx_export_adapter.py
python3 -m py_compile scripts/validate-trigger-paths.py
python3 -m py_compile scripts/test-validate-trigger-paths-structure.py
python3 -m py_compile scripts/validate-grill-me-install.py

echo "==> java-service-code-generator fixtures"
java-service-code-generator/scripts/verify_fixtures.py

echo "==> payment expert"
payment-expert/scripts/check_external_rules.py --self-test
python3 payment-expert/scripts/verify_behavior_cases.py
python3 payment-expert/scripts/test_verify_behavior_cases.py
public_core_eval_dir="${tmp_dir}/payment-public-core-eval"
python3 payment-expert/scripts/verify_behavior_cases.py --prepare-eval-batches "${public_core_eval_dir}"
python3 scripts/evaluate-skill-behavior.py validate --cases "${public_core_eval_dir}/candidate-comparison.json"
python3 scripts/evaluate-skill-behavior.py validate --cases "${public_core_eval_dir}/post-merge-forward.json"
python3 scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/payment-domain-foundations-behavior-cases.json"
python3 scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/payment-channel-routing-behavior-cases.json"
python3 payment-expert/scripts/verify_fixtures.py

echo "==> product deliverable checker"
product-architecture-expert/scripts/check_product_deliverable.py --self-test
python3 product-architecture-expert/scripts/test_check_prd_readability_evaluation.py
python3 product-architecture-expert/scripts/check_prd_readability_evaluation.py validate --contract product-architecture-expert/fixtures/prd-readability-evaluation.json
python3 product-architecture-expert/scripts/check_prd_readability_evaluation.py validate-report --contract product-architecture-expert/fixtures/prd-readability-evaluation.json --responses fixtures/skill-eval/product-prd-readability-r1-reader-evidence.jsonl --report fixtures/skill-eval/product-prd-readability-r1-report.json
python3 product-architecture-expert/scripts/test_check_product_qualification.py
python3 product-architecture-expert/scripts/verify_fixtures.py
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-client-interaction-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-business-expression-requirements-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-qualification-and-concepts-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-business-architecture-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-simple-design-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-reference-fast-gate-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-builder-series-increment-behavior-cases.json"
echo "==> document deliverable checker"
document-authoring/scripts/check_document_deliverable.py --self-test
document-authoring/scripts/check_document_style.py --self-test
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/document-authoring-humanization-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/document-authoring-visual-explanation-behavior-cases.json"

echo "==> resource capability candidate checker"
resource-capability-distiller/scripts/check_capability_candidate.py --self-test
scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/resource-capability-distiller-behavior-cases.json"

echo "==> fiction visual designer behavior cases"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/fiction-visual-designer-behavior-cases.json"

echo "==> novelist behavior cases"
python3 novelist/scripts/test-check-novelist-continuity-ledger.py
python3 novelist/scripts/test-check-novelist-timeline.py
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-logical-timeline-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-imagination-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-diversified-imagination-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-creative-inertia-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-local-material-use-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-planning-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-creative-technique-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-narrative-expression-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-character-life-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-historical-closure-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-civilization-responsibility-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-r6-foundation-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-r6-craft-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-scene-construction-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-draft-continuation-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-plot-progression-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-plot-inheritance-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-r8-practice-backflow-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/novelist-public-fiction-learning-behavior-cases.json"

echo "==> wise-agent module deliberation behavior cases"
scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/wise-agent-module-deliberation-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/wise-agent-external-capability-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/wise-agent-jit-loading-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/codex-harness-runtime-behavior-cases.json"

echo "==> hanzi philology evidence checker"
hanzi-philology/scripts/check_philology_evidence.py --self-test

echo "==> llm coding hygiene behavior cases"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/llm-coding-hygiene-behavior-cases.json"

echo "==> architecture deliverable checker"
senior-software-architect/scripts/check_architecture_deliverable.py --self-test
senior-software-architect/scripts/check_harness_plan.py --self-test
python3 senior-software-architect/scripts/test_check_system_intervention_card.py
senior-software-architect/scripts/verify_fixtures.py
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/senior-system-design-principles-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/senior-system-intervention-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/senior-public-contract-migration-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/senior-adr-governance-behavior-cases.json"
echo "==> business website planner"
run_gate python3 business-website-planner/scripts/test_check_business_website_plan.py
run_gate python3 business-website-planner/scripts/check_business_website_plan.py --file business-website-planner/fixtures/business-website-plan-valid.md
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/business-website-planner-behavior-cases.json"

echo "==> requirement acceptance testing"
run_gate python3 requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/requirement-acceptance-testing-behavior-cases.json"

echo "==> UI design deliverable checker"
python3 ui-design-expert/scripts/check_ui_design_deliverable.py --self-test
python3 ui-design-expert/scripts/test_check_design_draft_review.py
python3 ui-design-expert/scripts/test_check_figma_design_plan.py
python3 ui-design-expert/scripts/check_ui_source.py --self-test
python3 ui-design-expert/scripts/test_style_gallery.py
python3 ui-design-expert/scripts/style_gallery.py check
python3 ui-design-expert/scripts/verify_fixtures.py
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-design-visual-reproduction-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-design-prototype-evolution-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-design-responsive-media-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-design-ant-adoption-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-simple-design-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-quick-readonly-audit-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-style-gallery-behavior-cases.json"
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/ui-motion-craft-behavior-cases.json"

echo "==> security engineering deliverable checker"
python3 security-engineering-expert/scripts/check_security_deliverable.py --self-test
scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/security-engineering-behavior-cases.json"

echo "==> wind convention guard"
wind-coding-conventions/scripts/check_wind_conventions.py --self-test

echo "==> reference index audit"
scripts/audit-reference-indexes.py

echo "==> source map audit"
scripts/audit-source-map.py
scripts/audit-source-map.py --self-test

echo "==> skill admission"
python3 scripts/check-skill-admission.py --self-test
python3 scripts/test-check-skill-admission.py
python3 scripts/check-skill-admission.py

echo "==> skill evidence"
python3 scripts/test-check-skill-evidence.py
run_gate python3 scripts/check-skill-evidence.py

echo "==> source evidence archive"
scripts/archive-source-evidence.py --self-test

echo "==> Skill Eval prompt fixtures"
scripts/audit-skill-eval-fixtures.py --self-test

echo "==> Skill behavior evaluation"
python3 scripts/evaluate-skill-behavior.py --self-test
python3 scripts/test-evaluate-skill-behavior.py

echo "==> skill quality advisory"
python3 scripts/test-audit-skill-security.py
scripts/audit-skill-quality.py
scripts/audit-skill-quality.py --self-test
python3 scripts/test-audit-skill-quality.py
python3 scripts/test-validate-trigger-paths-structure.py

echo "==> skill evaluation"
scripts/evaluate-skills.py --self-test
python3 scripts/test-evaluate-skills.py

echo "==> SkillX export adapter"
python3 scripts/skillx_export_adapter.py --self-test

echo "==> sync dry-run"
dry_run_home="${tmp_dir}/dry-run-home"
CODEX_HOME="${dry_run_home}" ./sync-skills.sh --dry-run all
if [[ -e "${dry_run_home}" ]]; then
  echo "FAIL sync dry-run wrote to CODEX_HOME" >&2
  exit 1
fi

echo "==> candidate skill sync guard"
candidate_home="${tmp_dir}/candidate-home"
if CODEX_HOME="${candidate_home}" ./sync-skills.sh --dry-run payment-funds-review >/dev/null 2>&1; then
  echo "FAIL candidate payment-funds-review was syncable" >&2
  exit 1
fi

echo "==> optional payment routing sync guard"
dependency_home="${tmp_dir}/dependency-home"
if ! CODEX_HOME="${dependency_home}" ./sync-skills.sh --dry-run product-architecture-expert >/dev/null 2>&1; then
  echo "FAIL product-architecture-expert was blocked by optional payment routing" >&2
  exit 1
fi

echo "==> installed skill parity self-test"
parity_home="${tmp_dir}/parity-home"
CODEX_HOME="${parity_home}" ./sync-skills.sh all >/dev/null
CODEX_HOME="${parity_home}" scripts/validate-installed-skills.sh
mode_probe="${parity_home}/skills/product-architecture-expert/scripts/check_product_deliverable.py"
chmod -x "${mode_probe}"
if CODEX_HOME="${parity_home}" scripts/validate-installed-skills.sh >/dev/null 2>&1; then
  echo "FAIL installed skill parity ignored executable-bit drift" >&2
  exit 1
fi
CODEX_HOME="${parity_home}" ./sync-skills.sh product-architecture-expert >/dev/null
CODEX_HOME="${parity_home}" scripts/validate-installed-skills.sh
if [[ "${VALIDATE_INSTALLED_SKILLS:-}" == "1" ]]; then
  scripts/validate-installed-skills.sh
fi

echo "==> retired skill sync"
retirement_home="${tmp_dir}/retirement-home"
mkdir -p "${retirement_home}/skills/wind-project-coding-conventions"
printf '%s\n' 'legacy skill' > "${retirement_home}/skills/wind-project-coding-conventions/SKILL.md"
CODEX_HOME="${retirement_home}" ./sync-skills.sh wind-coding-conventions >/dev/null
if [[ -e "${retirement_home}/skills/wind-project-coding-conventions" ]]; then
  echo "FAIL retired Wind skill remains installed" >&2
  exit 1
fi
if ! find "${retirement_home}/skills/.backups" -path '*/wind-project-coding-conventions-*/SKILL.md' -type f | grep -q .; then
  echo "FAIL retired Wind skill backup missing" >&2
  exit 1
fi

mkdir -p "${retirement_home}/skills/delivery-collab"
printf '%s\n' 'legacy skill' > "${retirement_home}/skills/delivery-collab/SKILL.md"
CODEX_HOME="${retirement_home}" ./sync-skills.sh wise-agent >/dev/null
if [[ -e "${retirement_home}/skills/delivery-collab" ]]; then
  echo "FAIL retired delivery-collab skill remains installed" >&2
  exit 1
fi
if ! find "${retirement_home}/skills/.backups" -path '*/delivery-collab-*/SKILL.md' -type f | grep -q .; then
  echo "FAIL retired delivery-collab skill backup missing" >&2
  exit 1
fi

mkdir -p "${retirement_home}/skills/huaxia-wisdom"
printf '%s\n' 'legacy skill' > "${retirement_home}/skills/huaxia-wisdom/SKILL.md"
CODEX_HOME="${retirement_home}" ./sync-skills.sh huaxia-practical-wisdom >/dev/null
if [[ -e "${retirement_home}/skills/huaxia-wisdom" ]]; then
  echo "FAIL retired huaxia-wisdom skill remains installed" >&2
  exit 1
fi
if ! find "${retirement_home}/skills/.backups" -path '*/huaxia-wisdom-*/SKILL.md' -type f | grep -q .; then
  echo "FAIL retired huaxia-wisdom skill backup missing" >&2
  exit 1
fi

echo "==> diff whitespace"
git diff --check

if (( validation_failed != 0 )); then
  echo "Validation completed with deferred gate failures." >&2
  exit 1
fi

echo "All validations passed."
