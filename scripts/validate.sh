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

echo "==> python compile"
python3 -m py_compile java-service-code-generator/scripts/generate_scaffold.py

echo "==> java-service-code-generator fixtures"
java-service-code-generator/scripts/verify_fixtures.py

echo "==> sync dry-run"
CODEX_HOME="${tmp_dir}/codex-home" ./sync-skills.sh --dry-run all

echo "==> diff whitespace"
git diff --check

echo "All validations passed."
