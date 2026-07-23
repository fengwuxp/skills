#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

echo "==> bash syntax"
bash -n sync-skills.sh
bash -n scripts/audit-skills.sh
bash -n scripts/validate-installed-skills.sh
bash -n scripts/smoke-wise-agent-behavior.sh
bash -n scripts/validate-superpowers-install.sh

echo "==> skill audit"
scripts/audit-skills.sh

echo "==> skill frontmatter and agent yaml"
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
python3 scripts/validate-trigger-paths.py

echo "==> grill-me install validator"
python3 scripts/validate-grill-me-install.py --self-test
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

echo "==> wise-agent state contract"
python3 wise-agent/scripts/check_state_contract.py --self-test

echo "==> wise-agent skill learning ledger"
python3 wise-agent/scripts/skill-learning-ledger.py --self-test

echo "==> python compile"
python3 -m py_compile document-authoring/scripts/check_document_deliverable.py
python3 -m py_compile document-authoring/scripts/check_document_style.py
python3 -m py_compile hanzi-philology/scripts/check_philology_evidence.py
python3 -m py_compile java-service-code-generator/scripts/generate_scaffold.py
python3 -m py_compile product-architecture-expert/scripts/check_external_rules.py
python3 -m py_compile product-architecture-expert/scripts/check_product_deliverable.py
python3 -m py_compile resource-capability-distiller/scripts/check_capability_candidate.py
python3 -m py_compile senior-software-architect/scripts/check_architecture_deliverable.py
python3 -m py_compile senior-software-architect/scripts/check_harness_plan.py
python3 -m py_compile senior-software-architect/scripts/verify_fixtures.py
python3 -m py_compile wind-coding-conventions/scripts/check_wind_conventions.py
python3 -m py_compile wise-agent/scripts/check_state_contract.py
python3 -m py_compile wise-agent/scripts/skill-learning-ledger.py
python3 -m py_compile scripts/audit-reference-indexes.py
python3 -m py_compile scripts/audit-skill-quality.py
python3 -m py_compile scripts/audit-skill-eval-fixtures.py
python3 -m py_compile scripts/archive-source-evidence.py
python3 -m py_compile scripts/audit-source-map.py
python3 -m py_compile scripts/evaluate-skills.py
python3 -m py_compile scripts/skillx_export_adapter.py
python3 -m py_compile scripts/validate-trigger-paths.py
python3 -m py_compile scripts/validate-grill-me-install.py

echo "==> java-service-code-generator fixtures"
java-service-code-generator/scripts/verify_fixtures.py

echo "==> product external rule checker"
product-architecture-expert/scripts/check_external_rules.py --self-test

echo "==> product deliverable checker"
product-architecture-expert/scripts/check_product_deliverable.py --self-test

echo "==> document deliverable checker"
document-authoring/scripts/check_document_deliverable.py --self-test
document-authoring/scripts/check_document_style.py --self-test

echo "==> resource capability candidate checker"
resource-capability-distiller/scripts/check_capability_candidate.py --self-test

echo "==> hanzi philology evidence checker"
hanzi-philology/scripts/check_philology_evidence.py --self-test

echo "==> architecture deliverable checker"
senior-software-architect/scripts/check_architecture_deliverable.py --self-test
senior-software-architect/scripts/check_harness_plan.py --self-test
senior-software-architect/scripts/verify_fixtures.py

echo "==> wind convention guard"
wind-coding-conventions/scripts/check_wind_conventions.py --self-test

echo "==> reference index audit"
scripts/audit-reference-indexes.py

echo "==> source map audit"
scripts/audit-source-map.py
scripts/audit-source-map.py --self-test

echo "==> source evidence archive"
scripts/archive-source-evidence.py --self-test

echo "==> Skill Eval prompt fixtures"
scripts/audit-skill-eval-fixtures.py --self-test

echo "==> skill quality advisory"
scripts/audit-skill-quality.py
scripts/audit-skill-quality.py --self-test

echo "==> skill evaluation"
scripts/evaluate-skills.py --self-test

echo "==> SkillX export adapter"
python3 scripts/skillx_export_adapter.py --self-test

echo "==> sync dry-run"
dry_run_home="${tmp_dir}/dry-run-home"
CODEX_HOME="${dry_run_home}" ./sync-skills.sh --dry-run all
if [[ -e "${dry_run_home}" ]]; then
  echo "FAIL sync dry-run wrote to CODEX_HOME" >&2
  exit 1
fi

echo "==> installed skill parity self-test"
parity_home="${tmp_dir}/parity-home"
CODEX_HOME="${parity_home}" ./sync-skills.sh all >/dev/null
CODEX_HOME="${parity_home}" scripts/validate-installed-skills.sh
mode_probe="${parity_home}/skills/document-authoring/scripts/check_document_deliverable.py"
chmod -x "${mode_probe}"
if CODEX_HOME="${parity_home}" scripts/validate-installed-skills.sh >/dev/null 2>&1; then
  echo "FAIL installed skill parity ignored executable-bit drift" >&2
  exit 1
fi
CODEX_HOME="${parity_home}" ./sync-skills.sh document-authoring >/dev/null
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

echo "All validations passed."
