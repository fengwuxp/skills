#!/usr/bin/env bash
set -euo pipefail

# Input: `codex plugin list`, the listed plugin directory, and this repository.
# Output: plugin status, version, required Skill files, and retired snapshot checks.
# Writes: temporary files only during --self-test. Network: `codex plugin list` may refresh its catalog.
# Failure: exits non-zero when the official plugin is unavailable, incomplete, or the vendored snapshot returns.

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
REQUIRED_SKILLS=(
  brainstorming
  dispatching-parallel-agents
  executing-plans
  finishing-a-development-branch
  receiving-code-review
  requesting-code-review
  subagent-driven-development
  systematic-debugging
  test-driven-development
  using-git-worktrees
  using-superpowers
  verification-before-completion
  writing-plans
  writing-skills
)

validate_listing() {
  local listing="$1" repo_root="$2" row version plugin_root skill status=0
  row="$(printf '%s\n' "${listing}" | awk '$1 == "superpowers@openai-api-curated" && $2 == "installed," && $3 == "enabled" { print; exit }')"
  if [[ -z "${row}" ]]; then
    echo "ERROR superpowers@openai-api-curated is not installed and enabled" >&2
    return 1
  fi

  version="$(printf '%s\n' "${row}" | awk '{ print $4 }')"
  plugin_root="$(printf '%s\n' "${row}" | awk '{ print $5 }')"
  if [[ -z "${version}" || ! -d "${plugin_root}" ]]; then
    echo "ERROR invalid Superpowers plugin version or path: ${row}" >&2
    return 1
  fi
  if [[ ! -f "${plugin_root}/.codex-plugin/plugin.json" ]] \
    || ! grep -Eq '"name"[[:space:]]*:[[:space:]]*"superpowers"' "${plugin_root}/.codex-plugin/plugin.json"; then
    echo "ERROR invalid Superpowers plugin manifest: ${plugin_root}" >&2
    status=1
  fi
  for skill in "${REQUIRED_SKILLS[@]}"; do
    if [[ ! -f "${plugin_root}/skills/${skill}/SKILL.md" ]]; then
      echo "ERROR missing Superpowers Skill: ${skill}" >&2
      status=1
    fi
  done
  if [[ -e "${repo_root}/wise-agent/references/external-superpowers" ]]; then
    echo "ERROR retired external-superpowers snapshot exists" >&2
    status=1
  fi
  if [[ ${status} -eq 0 ]]; then
    echo "OK Superpowers plugin: version=${version} path=${plugin_root}"
  fi
  return "${status}"
}

create_fake_plugin() {
  local plugin_root="$1" skill
  mkdir -p "${plugin_root}/.codex-plugin"
  printf '%s\n' '{"name":"superpowers","version":"test"}' > "${plugin_root}/.codex-plugin/plugin.json"
  for skill in "${REQUIRED_SKILLS[@]}"; do
    mkdir -p "${plugin_root}/skills/${skill}"
    printf '%s\n' '---' "name: ${skill}" '---' > "${plugin_root}/skills/${skill}/SKILL.md"
  done
}

self_test() {
  local tmp plugin_root repo_root listing
  tmp="$(mktemp -d)"
  plugin_root="${tmp}/superpowers"
  repo_root="${tmp}/repo"
  trap 'rm -rf "${tmp}"' RETURN
  mkdir -p "${repo_root}/wise-agent/references"
  create_fake_plugin "${plugin_root}"
  listing="superpowers@openai-api-curated installed, enabled test-version ${plugin_root}"
  validate_listing "${listing}" "${repo_root}" >/dev/null

  rm -f "${plugin_root}/skills/systematic-debugging/SKILL.md"
  if validate_listing "${listing}" "${repo_root}" >/dev/null 2>&1; then
    echo "FAIL validator accepted a missing required Skill" >&2
    return 1
  fi
  create_fake_plugin "${plugin_root}"
  mkdir -p "${repo_root}/wise-agent/references/external-superpowers"
  if validate_listing "${listing}" "${repo_root}" >/dev/null 2>&1; then
    echo "FAIL validator accepted the retired snapshot" >&2
    return 1
  fi
  if validate_listing "superpowers@openai-api-curated not installed" "${repo_root}" >/dev/null 2>&1; then
    echo "FAIL validator accepted a disabled plugin" >&2
    return 1
  fi
}

case "${1:-}" in
  --self-test)
    self_test
    echo "OK validate-superpowers-install self-test"
    ;;
  "")
    validate_listing "$(codex plugin list)" "${ROOT_DIR}"
    ;;
  *)
    echo "usage: validate-superpowers-install.sh [--self-test]" >&2
    exit 2
    ;;
esac
