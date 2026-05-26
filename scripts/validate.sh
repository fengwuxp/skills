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
  agent = File.join(File.dirname(skill_md), "agents", "openai.yaml")
  YAML.load_file(agent) if File.exist?(agent)
  puts "OK #{skill_md}"
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

echo "==> python compile"
python3 -m py_compile java-service-code-generator/scripts/generate_scaffold.py
python3 -m py_compile product-architecture-expert/scripts/check_external_rules.py
python3 -m py_compile product-architecture-expert/scripts/check_product_deliverable.py
python3 -m py_compile senior-software-architect/scripts/check_architecture_deliverable.py
python3 -m py_compile scripts/audit-reference-indexes.py
python3 -m py_compile scripts/archive-source-evidence.py
python3 -m py_compile scripts/audit-source-map.py
python3 -m py_compile scripts/skillx_export_adapter.py
python3 -m py_compile scripts/validate-trigger-paths.py

echo "==> java-service-code-generator fixtures"
java-service-code-generator/scripts/verify_fixtures.py

echo "==> product external rule checker"
product-architecture-expert/scripts/check_external_rules.py --self-test

echo "==> product deliverable checker"
product-architecture-expert/scripts/check_product_deliverable.py --self-test

echo "==> architecture deliverable checker"
senior-software-architect/scripts/check_architecture_deliverable.py --self-test

echo "==> reference index audit"
scripts/audit-reference-indexes.py

echo "==> source map audit"
scripts/audit-source-map.py
scripts/audit-source-map.py --self-test

echo "==> source evidence archive"
scripts/archive-source-evidence.py --self-test

echo "==> SkillX export adapter"
python3 scripts/skillx_export_adapter.py --self-test

echo "==> sync dry-run"
CODEX_HOME="${tmp_dir}/codex-home" ./sync-skills.sh --dry-run all

echo "==> diff whitespace"
git diff --check

echo "All validations passed."
