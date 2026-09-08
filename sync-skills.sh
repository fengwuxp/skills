#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  sync-skills.sh                 # list skills and prompt for selection
  sync-skills.sh <skill-dir>...   # sync one or more skills by directory name
  sync-skills.sh all              # sync all skills
  sync-skills.sh --overwrite all  # clear this project's installed skills, then sync all
  sync-skills.sh --dry-run        # preview selected sync without writing target
  sync-skills.sh --with-agents wise-agent  # also sync global implementer/batch_worker profiles

Environment:
  CODEX_HOME  Codex home directory. Defaults to "$HOME/.codex".

Notes:
  - Source skills are discovered from skill directories next to this script.
  - Installed skills are synced to "$CODEX_HOME/skills/<skill-dir>".
  - Named skills or all discovered skills are copied without admission or dependency checks.
  - Existing installed skills are backed up before sync.
  - Overwrite mode moves current project names and known retired names to backup first.
  - Other installed skills, .system, and existing backups are left untouched.
  - Symbolic-link roots, targets, and pre-existing backup paths are rejected.
  - Known replaced skills are moved to the backup directory after their replacement syncs.
USAGE
}

DRY_RUN=false
OVERWRITE=false
WITH_AGENTS=false
ARGS=()
for arg in "$@"; do
  case "${arg}" in
    -h|--help)
      usage
      exit 0
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --overwrite)
      OVERWRITE=true
      ;;
    --with-agents)
      WITH_AGENTS=true
      ;;
    *)
      ARGS+=("${arg}")
      ;;
  esac
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"
SKILLS_DIR="${REPO_ROOT}"

if find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | grep -q .; then
  :
elif [[ -d "${SCRIPT_DIR}/skills" ]] && find "${SCRIPT_DIR}/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | grep -q .; then
  SKILLS_DIR="${SCRIPT_DIR}/skills"
else
  echo "Cannot locate skills: no */SKILL.md found under ${SCRIPT_DIR} or ${SCRIPT_DIR}/skills" >&2
  exit 1
fi

CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"
TARGET_ROOT="${CODEX_HOME_DIR}/skills"
BACKUP_ROOT="${TARGET_ROOT}/.backups"
AGENT_SOURCE_DIR="${REPO_ROOT}/.codex/agents"
AGENT_TARGET_DIR="${CODEX_HOME_DIR}/agents"
AGENT_BACKUP_ROOT="${CODEX_HOME_DIR}/.agent-backups"
AGENT_PROFILE_FILES=("implementer.toml" "batch-worker.toml")
SKILL_REPLACEMENTS=(
  "wind-project-coding-conventions:wind-coding-conventions"
  "delivery-collab:wise-agent"
  "huaxia-wisdom:huaxia-practical-wisdom"
)
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
DRY_RUN_STAGE=""

refuse_symbolic_link() {
  local path="$1"
  local label="$2"
  if [[ -L "${path}" ]]; then
    echo "Refusing symbolic-link ${label}: ${path}" >&2
    exit 1
  fi
}

refuse_symbolic_link "${TARGET_ROOT}" "Skill root"
refuse_symbolic_link "${BACKUP_ROOT}" "Skill backup root"
if [[ "${WITH_AGENTS}" == "true" ]]; then
  refuse_symbolic_link "${AGENT_TARGET_DIR}" "Agent target"
  refuse_symbolic_link "${AGENT_BACKUP_ROOT}" "Agent backup root"
fi

cleanup_dry_run_stage() {
  if [[ -n "${DRY_RUN_STAGE}" ]]; then
    rmdir "${DRY_RUN_STAGE}" 2>/dev/null || true
  fi
}

if [[ "${DRY_RUN}" == "true" ]]; then
  DRY_RUN_STAGE="$(mktemp -d)"
  trap cleanup_dry_run_stage EXIT
fi

skill_dirs=()
while IFS= read -r skill_file; do
  dir="$(dirname "${skill_file}")"
  key="$(basename "${dir}")"
  skill_dirs+=("${key}")
done < <(find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | sort)

if [[ ${#skill_dirs[@]} -eq 0 ]]; then
  echo "No skills found under ${SKILLS_DIR}" >&2
  exit 1
fi

print_skills() {
  echo "Available skills:"
  local i
  for i in "${!skill_dirs[@]}"; do
    printf '  [%d] %s\n' "$((i + 1))" "${skill_dirs[$i]}"
  done
}

contains_skill() {
  local candidate="$1"
  local i
  for i in "${!skill_dirs[@]}"; do
    if [[ "${skill_dirs[$i]}" == "${candidate}" ]]; then
      return 0
    fi
  done
  return 1
}

selected=()
ALL_SELECTED=false
add_selected() {
  local key="$1"
  local existing
  for existing in "${selected[@]:-}"; do
    if [[ "${existing}" == "${key}" ]]; then
      return 0
    fi
  done
  selected+=("${key}")
}

select_all() {
  ALL_SELECTED=true
  local key
  for key in "${skill_dirs[@]}"; do
    add_selected "${key}"
  done
}

selected_index() {
  local candidate="$1"
  local i
  for i in "${!selected[@]}"; do
    if [[ "${selected[$i]}" == "${candidate}" ]]; then
      echo "${i}"
      return 0
    fi
  done
  return 1
}

if [[ ${#ARGS[@]} -gt 0 ]]; then
  for arg in "${ARGS[@]}"; do
    if [[ "${arg}" == "all" ]]; then
      select_all
      continue
    fi
    if contains_skill "${arg}"; then
      add_selected "${arg}"
    else
      echo "Unknown skill: ${arg}" >&2
      print_skills >&2
      exit 1
    fi
  done
else
  print_skills
  echo
  read -r -p "Select skill numbers/names to sync (comma or space separated, 'all', or 'q'): " reply
  if [[ "${reply}" == "q" || "${reply}" == "quit" ]]; then
    echo "Canceled."
    exit 0
  fi
  reply="${reply//,/ }"
  for token in ${reply}; do
    if [[ "${token}" == "all" ]]; then
      select_all
      continue
    fi
    if [[ "${token}" =~ ^[0-9]+$ ]]; then
      index=$((token - 1))
      if (( index < 0 || index >= ${#skill_dirs[@]} )); then
        echo "Invalid selection number: ${token}" >&2
        exit 1
      fi
      add_selected "${skill_dirs[$index]}"
    elif contains_skill "${token}"; then
      add_selected "${token}"
    else
      echo "Unknown selection: ${token}" >&2
      exit 1
    fi
  done
fi

if [[ ${#selected[@]} -eq 0 ]]; then
  echo "No skills selected."
  exit 0
fi

if [[ "${OVERWRITE}" == "true" ]]; then
  if [[ "${ALL_SELECTED}" != "true" ]]; then
    echo "--overwrite requires all" >&2
    exit 1
  fi
  if [[ "${TARGET_ROOT}" -ef "${SKILLS_DIR}" ]]; then
    echo "Refusing to clear the source Skill root: ${TARGET_ROOT}" >&2
    exit 1
  fi
fi

if [[ "${WITH_AGENTS}" == "true" ]] && ! selected_index "wise-agent" >/dev/null; then
  echo "--with-agents requires wise-agent to be selected" >&2
  exit 1
fi

echo "Repository root: ${REPO_ROOT}"
echo "Codex home:      ${CODEX_HOME_DIR}"
echo "Dry run:         ${DRY_RUN}"
echo

if [[ "${DRY_RUN}" == "false" ]]; then
  mkdir -p "${TARGET_ROOT}"
  mkdir -p "${BACKUP_ROOT}"
fi

sync_one() {
  local key="$1"
  local source_dir="${SKILLS_DIR}/${key}"
  local target_dir="${TARGET_ROOT}/${key}"
  local backup_dir="${BACKUP_ROOT}/${key}-${TIMESTAMP}"
  local rsync_target="${target_dir}"
  if [[ ! -f "${source_dir}/SKILL.md" ]]; then
    echo "Source skill is invalid, missing SKILL.md: ${source_dir}" >&2
    exit 1
  fi
  if [[ -L "${target_dir}" ]]; then
    echo "Refusing symbolic-link Skill target: ${target_dir}" >&2
    exit 1
  fi
  if [[ "${DRY_RUN}" == "false" && -e "${target_dir}" && ( -e "${backup_dir}" || -L "${backup_dir}" ) ]]; then
    echo "Refusing existing Skill backup path: ${backup_dir}" >&2
    exit 1
  fi

  echo "==> ${key}"
  echo "    from: ${source_dir}"
  echo "    to:   ${target_dir}"

  if [[ "${DRY_RUN}" == "false" && -d "${target_dir}" ]]; then
    echo "    backup: ${backup_dir}"
    mkdir -p "${backup_dir}"
    rsync -a "${target_dir}/" "${backup_dir}/"
  elif [[ "${DRY_RUN}" == "false" ]]; then
    echo "    target does not exist; it will be created"
  fi

  rsync_args=(-av --delete --exclude '.DS_Store' --exclude '.idea' --exclude '__pycache__' --exclude '*.[pP][yY][cC]')
  if [[ "${DRY_RUN}" == "true" ]]; then
    rsync_args+=(--dry-run)
    if [[ "${OVERWRITE}" == "true" || ! -d "${target_dir}" ]]; then
      rsync_target="${DRY_RUN_STAGE}"
    fi
  else
    mkdir -p "${target_dir}"
  fi

  rsync "${rsync_args[@]}" "${source_dir}/" "${rsync_target}/"
}

sync_agent_profiles() {
  local rsync_target="${AGENT_TARGET_DIR}"
  local backup_dir="${AGENT_BACKUP_ROOT}/agents-${TIMESTAMP}"
  local profile_file source_file target_file

  if [[ "${DRY_RUN}" == "false" && ( -e "${backup_dir}" || -L "${backup_dir}" ) ]]; then
    echo "Refusing existing Agent backup path: ${backup_dir}" >&2
    exit 1
  fi

  echo "==> Codex agent profiles"
  echo "    from: ${AGENT_SOURCE_DIR}"
  echo "    to:   ${AGENT_TARGET_DIR}"

  if [[ "${DRY_RUN}" == "true" ]]; then
    if [[ ! -d "${AGENT_TARGET_DIR}" ]]; then
      rsync_target="${DRY_RUN_STAGE}"
    fi
  else
    mkdir -p "${AGENT_TARGET_DIR}"
    for profile_file in "${AGENT_PROFILE_FILES[@]}"; do
      source_file="${AGENT_SOURCE_DIR}/${profile_file}"
      target_file="${AGENT_TARGET_DIR}/${profile_file}"
      if [[ -f "${target_file}" ]] && ! cmp -s "${source_file}" "${target_file}"; then
        mkdir -p "${backup_dir}"
        cp -p "${target_file}" "${backup_dir}/"
      fi
    done
  fi

  for profile_file in "${AGENT_PROFILE_FILES[@]}"; do
    source_file="${AGENT_SOURCE_DIR}/${profile_file}"
    if [[ "${DRY_RUN}" == "true" ]]; then
      rsync -av --dry-run "${source_file}" "${rsync_target}/"
    else
      rsync -av "${source_file}" "${rsync_target}/"
    fi
  done

  if [[ "${DRY_RUN}" == "false" ]]; then
    [[ ! -d "${backup_dir}" ]] || echo "    backup: ${backup_dir}"
  fi
}

clear_project_skills() {
  local project_skills=("${skill_dirs[@]}")
  local mapping key target_dir backup_dir
  for mapping in "${SKILL_REPLACEMENTS[@]}"; do
    project_skills+=("${mapping%%:*}")
  done

  for key in "${project_skills[@]}"; do
    target_dir="${TARGET_ROOT}/${key}"
    backup_dir="${BACKUP_ROOT}/${key}-${TIMESTAMP}"
    refuse_symbolic_link "${target_dir}" "Skill target"
    if [[ "${DRY_RUN}" == "false" && -e "${target_dir}" && ( -e "${backup_dir}" || -L "${backup_dir}" ) ]]; then
      echo "Refusing existing Skill backup path: ${backup_dir}" >&2
      exit 1
    fi
  done

  for key in "${project_skills[@]}"; do
    target_dir="${TARGET_ROOT}/${key}"
    backup_dir="${BACKUP_ROOT}/${key}-${TIMESTAMP}"
    [[ -e "${target_dir}" ]] || continue
    echo "==> clear ${key}"
    echo "    move to backup: ${backup_dir}"
    if [[ "${DRY_RUN}" == "false" ]]; then
      mv "${target_dir}" "${backup_dir}"
    fi
  done
}

retire_replaced_skill() {
  local retired="$1"
  local replacement="$2"
  local key replacement_selected=false
  for key in "${selected[@]}"; do
    if [[ "${key}" == "${replacement}" ]]; then
      replacement_selected=true
      break
    fi
  done
  if [[ "${replacement_selected}" == "false" ]]; then
    return 0
  fi

  local target_dir="${TARGET_ROOT}/${retired}"
  local backup_dir="${BACKUP_ROOT}/${retired}-${TIMESTAMP}"
  if [[ ! -d "${target_dir}" ]]; then
    return 0
  fi

  echo "==> retire ${retired}"
  if [[ "${DRY_RUN}" == "true" ]]; then
    echo "    would move: ${target_dir}"
    echo "    to backup: ${backup_dir}"
    return 0
  fi
  if [[ -e "${backup_dir}" || -L "${backup_dir}" ]]; then
    echo "Retirement backup already exists: ${backup_dir}" >&2
    exit 1
  fi
  mv "${target_dir}" "${backup_dir}"
  test ! -e "${target_dir}"
  test -f "${backup_dir}/SKILL.md"
  echo "    backup: ${backup_dir}"
}

if [[ "${OVERWRITE}" == "true" ]]; then
  clear_project_skills
fi

for key in "${selected[@]}"; do
  sync_one "${key}"
  echo
done

if [[ "${WITH_AGENTS}" == "true" ]]; then
  sync_agent_profiles
  echo
fi

if [[ "${OVERWRITE}" == "false" ]]; then
  for mapping in "${SKILL_REPLACEMENTS[@]}"; do
    retire_replaced_skill "${mapping%%:*}" "${mapping#*:}"
  done
fi

echo "Done. Restart Codex or open a new session if skill metadata does not refresh immediately."
