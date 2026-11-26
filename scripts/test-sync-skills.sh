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

fixture_repo="${tmp_dir}/repository"
mkdir -p "${fixture_repo}/candidate" "${fixture_repo}/caller" "${fixture_repo}/unchecked"
cp "${ROOT_DIR}/sync-skills.sh" "${fixture_repo}/sync-skills.sh"
for key in candidate caller unchecked; do
  printf '%s\n' '---' "name: ${key}" '---' "# ${key}" > "${fixture_repo}/${key}/SKILL.md"
done
printf '%s\n' '{"status":"candidate"}' > "${fixture_repo}/candidate/admission.json"
printf '%s\n' '{"status":"installable","requires":["missing-dependency"]}' > "${fixture_repo}/caller/admission.json"
printf '%s\n' 'not valid JSON' > "${fixture_repo}/unchecked/admission.json"

direct_home="${tmp_dir}/direct-home"
mkdir -p "${direct_home}/skills/candidate" "${direct_home}/skills/unrelated"
printf '%s\n' old > "${direct_home}/skills/candidate/SKILL.md"
printf '%s\n' stale > "${direct_home}/skills/candidate/stale.txt"
printf '%s\n' keep > "${direct_home}/skills/unrelated/keep.txt"
if ! CODEX_HOME="${direct_home}" "${fixture_repo}/sync-skills.sh" candidate candidate >"${output_file}" 2>&1; then
  cat "${output_file}" >&2
  echo "FAIL named sync requires admission validators instead of copying the selected Skill" >&2
  exit 1
fi
cmp "${fixture_repo}/candidate/SKILL.md" "${direct_home}/skills/candidate/SKILL.md"
test ! -e "${direct_home}/skills/candidate/stale.txt"
test -f "${direct_home}/skills/unrelated/keep.txt"
test ! -e "${direct_home}/skills/caller"
backup_file="$(find "${direct_home}/skills/.backups" -name stale.txt -type f)"
test -n "${backup_file}"
test "$(cat "${backup_file}")" = stale

claude_home="${tmp_dir}/claude-home"
CLAUDE_HOME="${claude_home}" "${fixture_repo}/sync-skills.sh" --target claude candidate >"${output_file}" 2>&1
diff -qr "${fixture_repo}/candidate" "${claude_home}/skills/candidate"
test -d "${claude_home}/skills/.backups"

printf '%s\n' changed > "${claude_home}/skills/candidate/SKILL.md"
CLAUDE_HOME="${claude_home}" "${fixture_repo}/sync-skills.sh" --target claude candidate >"${output_file}" 2>&1
diff -qr "${fixture_repo}/candidate" "${claude_home}/skills/candidate"
claude_backup_file="$(find "${claude_home}/skills/.backups" -name SKILL.md -type f)"
test -n "${claude_backup_file}"
test "$(cat "${claude_backup_file}")" = changed

claude_preview_home="${tmp_dir}/claude-preview-home"
CLAUDE_HOME="${claude_preview_home}" "${fixture_repo}/sync-skills.sh" --target claude --dry-run all >"${output_file}" 2>&1
test ! -e "${claude_preview_home}"

if CLAUDE_HOME="${tmp_dir}/claude-agent-home" \
  "${fixture_repo}/sync-skills.sh" --target claude --with-agents wise-agent >"${output_file}" 2>&1; then
  echo "FAIL Claude target accepted Codex agent profiles" >&2
  exit 1
fi
grep -Fq -- '--with-agents is only supported with --target codex' "${output_file}"

all_home="${tmp_dir}/all-home"
CODEX_HOME="${all_home}" "${fixture_repo}/sync-skills.sh" all >"${output_file}" 2>&1
for key in candidate caller unchecked; do
  diff -qr "${fixture_repo}/${key}" "${all_home}/skills/${key}"
done
test ! -e "${all_home}/skills/missing-dependency"

caller_home="${tmp_dir}/caller-home"
CODEX_HOME="${caller_home}" "${fixture_repo}/sync-skills.sh" caller >"${output_file}" 2>&1
diff -qr "${fixture_repo}/caller" "${caller_home}/skills/caller"
test ! -e "${caller_home}/skills/candidate"

interactive_home="${tmp_dir}/interactive-home"
printf '%s\n' '2,1' | CODEX_HOME="${interactive_home}" "${fixture_repo}/sync-skills.sh" >"${output_file}" 2>&1
for key in candidate caller; do
  diff -qr "${fixture_repo}/${key}" "${interactive_home}/skills/${key}"
done

menu_script="${fixture_repo}/menu-sync.sh"
menu_home="${tmp_dir}/menu-home"
menu_log="${tmp_dir}/menu.log"
cp "${ROOT_DIR}/sync-skills.sh" "${menu_script}"
: > "${menu_log}"
save_during_menu() {
  local deadline=$((SECONDS + 10))
  until grep -Fq 'Available skills:' "${menu_log}"; do
    if (( SECONDS >= deadline )); then
      echo "FAIL sync did not display the selection menu" >&2
      return 1
    fi
    sleep 0.05
  done
  # 原地保存另一份有效脚本，保留字节范围，以便发现仍然读取新版本尾部的进程。
  LC_ALL=C tr -c '\n' ' ' < "${ROOT_DIR}/sync-skills.sh" > "${menu_script}" || return 1
  printf '\nexit 73\n' >> "${menu_script}" || return 1
  printf 'all\n'
}
if ! save_during_menu | CODEX_HOME="${menu_home}" "${menu_script}" >"${menu_log}" 2>&1; then
  cat "${menu_log}" >&2
  echo "FAIL interactive sync read the script saved during selection" >&2
  exit 1
fi
grep -q '^Done\.' "${menu_log}"
for key in candidate caller unchecked; do
  grep -Fxq "==> ${key}" "${menu_log}"
  diff -qr "${fixture_repo}/${key}" "${menu_home}/skills/${key}"
done

preview_home="${tmp_dir}/preview-home"
CODEX_HOME="${preview_home}" "${fixture_repo}/sync-skills.sh" --dry-run all >"${output_file}" 2>&1
test ! -e "${preview_home}"
printf '%s\n' unchanged > "${direct_home}/skills/candidate/SKILL.md"
CODEX_HOME="${direct_home}" "${fixture_repo}/sync-skills.sh" --dry-run candidate >"${output_file}" 2>&1
test "$(cat "${direct_home}/skills/candidate/SKILL.md")" = unchanged

large_repo="${tmp_dir}/large-repository"
large_preview_home="${tmp_dir}/large-preview-home"
mkdir -p "${large_repo}"
cp "${ROOT_DIR}/sync-skills.sh" "${large_repo}/sync-skills.sh"
for ((index = 0; index < 600; index++)); do
  key="$(printf 'skill-%04d' "${index}")"
  mkdir -p "${large_repo}/${key}"
  printf '%s\n' '---' "name: ${key}" '---' "# ${key}" > "${large_repo}/${key}/SKILL.md"
done
if ! CODEX_HOME="${large_preview_home}" "${large_repo}/sync-skills.sh" --dry-run skill-0000 >"${output_file}" 2>&1; then
  cat "${output_file}" >&2
  echo "FAIL sync could not discover a Skill in a large repository" >&2
  exit 1
fi
grep -Fxq '==> skill-0000' "${output_file}"
test "$(grep -c '^==> ' "${output_file}")" = 1
test ! -e "${large_preview_home}"

unknown_home="${tmp_dir}/unknown-home"
if CODEX_HOME="${unknown_home}" "${fixture_repo}/sync-skills.sh" candidate missing >"${output_file}" 2>&1; then
  echo "FAIL sync accepted an unknown Skill" >&2
  exit 1
fi
test ! -e "${unknown_home}"

overwrite_home="${tmp_dir}/overwrite-home"
mkdir -p "${overwrite_home}/skills/candidate/.idea" \
  "${overwrite_home}/skills/delivery-collab" \
  "${overwrite_home}/skills/candidate-extra" "${overwrite_home}/skills/.system" \
  "${overwrite_home}/skills/.backups/previous"
printf '%s\n' old > "${overwrite_home}/skills/candidate/SKILL.md"
printf '%s\n' old-cache > "${overwrite_home}/skills/candidate/.idea/stale.txt"
printf '%s\n' retired > "${overwrite_home}/skills/delivery-collab/SKILL.md"
for key in candidate-extra .system .backups/previous; do
  printf '%s\n' keep > "${overwrite_home}/skills/${key}/keep.txt"
done
ln -s "${outside_target}" "${overwrite_home}/skills/external-link"
cp -R "${overwrite_home}" "${tmp_dir}/overwrite-before"
if ! CODEX_HOME="${overwrite_home}" "${fixture_repo}/sync-skills.sh" --dry-run --overwrite all >"${output_file}" 2>&1; then
  cat "${output_file}" >&2
  echo "FAIL overwrite-all preview is not supported" >&2
  exit 1
fi
diff -qr "${tmp_dir}/overwrite-before" "${overwrite_home}"

CODEX_HOME="${overwrite_home}" "${fixture_repo}/sync-skills.sh" --overwrite all >"${output_file}" 2>&1
for key in candidate caller unchecked; do
  diff -qr "${fixture_repo}/${key}" "${overwrite_home}/skills/${key}"
done
test ! -e "${overwrite_home}/skills/candidate/.idea"
test ! -e "${overwrite_home}/skills/delivery-collab"
for key in candidate-extra .system .backups/previous; do
  test "$(cat "${overwrite_home}/skills/${key}/keep.txt")" = keep
done
test -L "${overwrite_home}/skills/external-link"
test "$(cat "${outside_target}/keep.txt")" = sentinel
test -n "$(find "${overwrite_home}/skills/.backups" -path '*/candidate-*/.idea/stale.txt' -type f)"
test -n "$(find "${overwrite_home}/skills/.backups" -path '*/delivery-collab-*/SKILL.md' -type f)"

overwrite_empty_home="${tmp_dir}/overwrite-empty-home"
CODEX_HOME="${overwrite_empty_home}" "${fixture_repo}/sync-skills.sh" --dry-run --overwrite all >"${output_file}" 2>&1
test ! -e "${overwrite_empty_home}"
if CODEX_HOME="${overwrite_empty_home}" "${fixture_repo}/sync-skills.sh" --overwrite candidate >"${output_file}" 2>&1; then
  echo "FAIL overwrite accepted a partial selection" >&2
  exit 1
fi
test ! -e "${overwrite_empty_home}"
grep -Fq -- '--overwrite requires all' "${output_file}"

overwrite_link_home="${tmp_dir}/overwrite-link-home"
mkdir -p "${overwrite_link_home}/skills/candidate"
printf '%s\n' untouched > "${overwrite_link_home}/skills/candidate/SKILL.md"
ln -s "${outside_target}" "${overwrite_link_home}/skills/unchecked"
if CODEX_HOME="${overwrite_link_home}" "${fixture_repo}/sync-skills.sh" --overwrite all >"${output_file}" 2>&1; then
  echo "FAIL overwrite accepted a symbolic-link project Skill" >&2
  exit 1
fi
test "$(cat "${overwrite_link_home}/skills/candidate/SKILL.md")" = untouched
test "$(cat "${outside_target}/keep.txt")" = sentinel
grep -Fq 'Refusing symbolic-link Skill target' "${output_file}"

self_home="${tmp_dir}/self-home"
mkdir -p "${self_home}/skills/candidate"
cp "${ROOT_DIR}/sync-skills.sh" "${self_home}/sync-skills.sh"
cp "${fixture_repo}/candidate/SKILL.md" "${self_home}/skills/candidate/SKILL.md"
if CODEX_HOME="${self_home}" "${self_home}/sync-skills.sh" --overwrite all >"${output_file}" 2>&1; then
  echo "FAIL overwrite accepted its own source directory as the installation" >&2
  exit 1
fi
cmp "${fixture_repo}/candidate/SKILL.md" "${self_home}/skills/candidate/SKILL.md"
grep -Fq 'Refusing to clear the source Skill root' "${output_file}"

expect_overlap_rejected() {
  local install_home="$1" source_script="$2"
  shift 2
  if CODEX_HOME="${install_home}" "${source_script}" --dry-run "$@" >"${output_file}" 2>&1; then
    echo "FAIL preview accepted overlapping source and target paths" >&2
    exit 1
  fi
  grep -Fq 'Refusing overlapping source and target paths' "${output_file}"
  if CODEX_HOME="${install_home}" "${source_script}" "$@" >"${output_file}" 2>&1; then
    echo "FAIL sync accepted overlapping source and target paths" >&2
    exit 1
  fi
  grep -Fq 'Refusing overlapping source and target paths' "${output_file}"
}

# 实际清理目标可以包含整个源码仓；预演和同步都必须在移动前拒绝。
ancestor_home="${tmp_dir}/ancestor-home"
ancestor_repo="${ancestor_home}/skills/candidate"
mkdir -p "${ancestor_repo}/candidate"
cp "${ROOT_DIR}/sync-skills.sh" "${ancestor_repo}/sync-skills.sh"
cp "${fixture_repo}/candidate/SKILL.md" "${ancestor_repo}/candidate/SKILL.md"
expect_overlap_rejected "${ancestor_home}" "${ancestor_repo}/sync-skills.sh" --overwrite all
expect_overlap_rejected "${ancestor_home}" "${ancestor_repo}/sync-skills.sh" candidate
cmp "${fixture_repo}/candidate/SKILL.md" "${ancestor_repo}/candidate/SKILL.md"
test ! -e "${ancestor_home}/skills/.backups"

# 尚不存在的后代目标、相对路径及父目录链接都应解析到同一个源目录。
expect_overlap_rejected "${fixture_repo}/candidate/new-home" "${fixture_repo}/sync-skills.sh" candidate
test ! -e "${fixture_repo}/candidate/new-home"
(
  cd "${fixture_repo}"
  expect_overlap_rejected "candidate/../candidate/new-home" "./sync-skills.sh" --overwrite all
)
test ! -e "${fixture_repo}/candidate/new-home"
ln -s "${fixture_repo}/candidate" "${tmp_dir}/source-alias"
expect_overlap_rejected "${tmp_dir}/source-alias/new-home" "${fixture_repo}/sync-skills.sh" candidate
test ! -e "${fixture_repo}/candidate/new-home"

# 文件系统可能把大小写不同的路径解析为同一目录，不能仅按字符串判断包含。
case_home="${tmp_dir}/case-home"
case_alias="${tmp_dir}/CASE-HOME"
case_repo="${case_home}/skills/candidate"
mkdir -p "${case_repo}/candidate"
cp "${ROOT_DIR}/sync-skills.sh" "${case_repo}/sync-skills.sh"
cp "${fixture_repo}/candidate/SKILL.md" "${case_repo}/candidate/SKILL.md"
if [[ "${case_home}" -ef "${case_alias}" ]]; then
  expect_overlap_rejected "${case_alias}" "${case_repo}/sync-skills.sh" --overwrite all
  expect_overlap_rejected "${fixture_repo}/CANDIDATE/new-home" "${fixture_repo}/sync-skills.sh" candidate
  test ! -e "${case_home}/skills/.backups"
  test ! -e "${fixture_repo}/candidate/new-home"
else
  # 大小写敏感文件系统上的同名异大小写目录是合法独立目标。
  CODEX_HOME="${case_alias}" "${case_repo}/sync-skills.sh" --dry-run candidate >"${output_file}" 2>&1
  test ! -e "${case_alias}"
  CODEX_HOME="${case_alias}" "${case_repo}/sync-skills.sh" candidate >"${output_file}" 2>&1
  diff -qr "${case_repo}/candidate" "${case_alias}/skills/candidate"
fi
cmp "${fixture_repo}/candidate/SKILL.md" "${case_repo}/candidate/SKILL.md"

# 普通同步也拒绝相同源目标，退役旧名称的移动同样不能吞入源码仓。
expect_overlap_rejected "${self_home}" "${self_home}/sync-skills.sh" candidate
retired_home="${tmp_dir}/retired-source-home"
retired_repo="${retired_home}/skills/delivery-collab"
mkdir -p "${retired_repo}/wise-agent"
cp "${ROOT_DIR}/sync-skills.sh" "${retired_repo}/sync-skills.sh"
cp "${fixture_repo}/candidate/SKILL.md" "${retired_repo}/wise-agent/SKILL.md"
expect_overlap_rejected "${retired_home}" "${retired_repo}/sync-skills.sh" wise-agent
test -f "${retired_repo}/wise-agent/SKILL.md"
test ! -e "${retired_home}/skills/wise-agent"
test ! -e "${retired_home}/skills/.backups"

# 备份路径落在源码仓时，在创建安装目录前拒绝。
backup_source_home="${tmp_dir}/backup-source-home"
backup_source_repo="${backup_source_home}/skills/.backups/candidate-20260904-000000"
mkdir -p "${backup_source_repo}/candidate"
cp "${ROOT_DIR}/sync-skills.sh" "${backup_source_repo}/sync-skills.sh"
cp "${fixture_repo}/candidate/SKILL.md" "${backup_source_repo}/candidate/SKILL.md"
PATH="${fake_bin}:${PATH}" expect_overlap_rejected "${backup_source_home}" "${backup_source_repo}/sync-skills.sh" candidate
cmp "${fixture_repo}/candidate/SKILL.md" "${backup_source_repo}/candidate/SKILL.md"
test ! -e "${backup_source_home}/skills/candidate"

# --with-agents 共用写入前检查，独立的 Skill 目标不能掩盖 Agent 源目标重叠。
agent_source_repo="${tmp_dir}/agent-source-repository"
mkdir -p "${agent_source_repo}/wise-agent" "${agent_source_repo}/.codex/agents"
cp "${ROOT_DIR}/sync-skills.sh" "${agent_source_repo}/sync-skills.sh"
cp "${fixture_repo}/candidate/SKILL.md" "${agent_source_repo}/wise-agent/SKILL.md"
printf '%s\n' source-profile > "${agent_source_repo}/.codex/agents/implementer.toml"
expect_overlap_rejected "${agent_source_repo}/.codex" "${agent_source_repo}/sync-skills.sh" --with-agents wise-agent
test "$(cat "${agent_source_repo}/.codex/agents/implementer.toml")" = source-profile
test ! -e "${agent_source_repo}/.codex/skills"
test ! -e "${agent_source_repo}/.codex/.agent-backups"

# 仓内独立安装目录及路径同前缀的兄弟目录仍可使用。
for safe_home in "${fixture_repo}/.codex" "${fixture_repo}/candidate-other"; do
  CODEX_HOME="${safe_home}" "${fixture_repo}/sync-skills.sh" --dry-run candidate >"${output_file}" 2>&1
  test ! -e "${safe_home}"
  CODEX_HOME="${safe_home}" "${fixture_repo}/sync-skills.sh" candidate >"${output_file}" 2>&1
  diff -qr "${fixture_repo}/candidate" "${safe_home}/skills/candidate"
done

echo "OK direct sync, overwrite-all, selection, dry-run and target safety"
