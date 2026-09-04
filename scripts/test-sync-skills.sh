#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
cleanup() {
  rm -r -- "${tmp_dir}"
}
trap cleanup EXIT

codex_home="${tmp_dir}/codex"
outside_target="${tmp_dir}/outside-target"
mkdir -p "${codex_home}/skills" "${outside_target}"
printf '%s\n' sentinel > "${outside_target}/keep.txt"
ln -s "${outside_target}" "${codex_home}/skills/hanzi-philology"

output_file="${tmp_dir}/sync-output.txt"
if CODEX_HOME="${codex_home}" "${ROOT_DIR}/sync-skills.sh" hanzi-philology >"${output_file}" 2>&1; then
  echo "FAIL sync accepted a symbolic-link Skill target" >&2
  exit 1
fi

if [[ ! -f "${outside_target}/keep.txt" ]]; then
  echo "FAIL sync deleted data through a symbolic-link Skill target" >&2
  exit 1
fi
if [[ -f "${outside_target}/SKILL.md" ]]; then
  echo "FAIL sync wrote data through a symbolic-link Skill target" >&2
  exit 1
fi
if ! grep -Fq "Refusing symbolic-link Skill target" "${output_file}"; then
  echo "FAIL sync did not explain the symbolic-link rejection" >&2
  exit 1
fi

root_link_home="${tmp_dir}/root-link-home"
root_link_target="${tmp_dir}/root-link-target"
mkdir -p "${root_link_home}" "${root_link_target}"
printf '%s\n' sentinel > "${root_link_target}/keep.txt"
ln -s "${root_link_target}" "${root_link_home}/skills"
if CODEX_HOME="${root_link_home}" "${ROOT_DIR}/sync-skills.sh" hanzi-philology >"${output_file}" 2>&1; then
  echo "FAIL sync accepted a symbolic-link Skill root" >&2
  exit 1
fi
if [[ ! -f "${root_link_target}/keep.txt" || -e "${root_link_target}/hanzi-philology" ]]; then
  echo "FAIL sync changed data through a symbolic-link Skill root" >&2
  exit 1
fi
if ! grep -Fq "Refusing symbolic-link Skill root" "${output_file}"; then
  echo "FAIL sync did not explain the symbolic-link Skill root rejection" >&2
  exit 1
fi

backup_link_home="${tmp_dir}/backup-link-home"
backup_link_target="${tmp_dir}/backup-link-target"
mkdir -p "${backup_link_home}/skills/hanzi-philology" "${backup_link_target}"
printf '%s\n' installed > "${backup_link_home}/skills/hanzi-philology/SKILL.md"
printf '%s\n' sentinel > "${backup_link_target}/keep.txt"
ln -s "${backup_link_target}" "${backup_link_home}/skills/.backups"
if CODEX_HOME="${backup_link_home}" "${ROOT_DIR}/sync-skills.sh" hanzi-philology >"${output_file}" 2>&1; then
  echo "FAIL sync accepted a symbolic-link Skill backup root" >&2
  exit 1
fi
if [[ ! -f "${backup_link_target}/keep.txt" ]] || find "${backup_link_target}" -mindepth 1 ! -name keep.txt | grep -q .; then
  echo "FAIL sync wrote through a symbolic-link Skill backup root" >&2
  exit 1
fi
if ! grep -Fq "Refusing symbolic-link Skill backup root" "${output_file}"; then
  echo "FAIL sync did not explain the symbolic-link backup rejection" >&2
  exit 1
fi

backup_entry_home="${tmp_dir}/backup-entry-home"
backup_entry_target="${tmp_dir}/backup-entry-target"
fake_bin="${tmp_dir}/fake-bin"
mkdir -p "${backup_entry_home}/skills/hanzi-philology" \
  "${backup_entry_home}/skills/.backups" "${backup_entry_target}" "${fake_bin}"
printf '%s\n' installed > "${backup_entry_home}/skills/hanzi-philology/SKILL.md"
printf '%s\n' sentinel > "${backup_entry_target}/keep.txt"
printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" 20260904-000000' > "${fake_bin}/date"
chmod 755 "${fake_bin}/date"
ln -s "${backup_entry_target}" \
  "${backup_entry_home}/skills/.backups/hanzi-philology-20260904-000000"
if PATH="${fake_bin}:${PATH}" CODEX_HOME="${backup_entry_home}" \
  "${ROOT_DIR}/sync-skills.sh" hanzi-philology >"${output_file}" 2>&1; then
  echo "FAIL sync accepted a symbolic-link Skill backup entry" >&2
  exit 1
fi
if [[ ! -f "${backup_entry_target}/keep.txt" ]] \
  || find "${backup_entry_target}" -mindepth 1 ! -name keep.txt | grep -q .; then
  echo "FAIL sync wrote through a symbolic-link Skill backup entry" >&2
  exit 1
fi
if ! grep -Fq "Refusing existing Skill backup path" "${output_file}"; then
  echo "FAIL sync did not explain the existing backup path rejection" >&2
  exit 1
fi

agent_link_home="${tmp_dir}/agent-link-home"
agent_link_target="${tmp_dir}/agent-link-target"
mkdir -p "${agent_link_home}/skills" "${agent_link_target}"
printf '%s\n' sentinel > "${agent_link_target}/keep.txt"
ln -s "${agent_link_target}" "${agent_link_home}/agents"
if CODEX_HOME="${agent_link_home}" "${ROOT_DIR}/sync-skills.sh" --with-agents wise-agent >"${output_file}" 2>&1; then
  echo "FAIL sync accepted a symbolic-link Agent target" >&2
  exit 1
fi
if [[ ! -f "${agent_link_target}/keep.txt" || -e "${agent_link_target}/implementer.toml" ]]; then
  echo "FAIL sync wrote through a symbolic-link Agent target" >&2
  exit 1
fi
if ! grep -Fq "Refusing symbolic-link Agent target" "${output_file}"; then
  echo "FAIL sync did not explain the symbolic-link Agent target rejection" >&2
  exit 1
fi

echo "OK sync target safety"
