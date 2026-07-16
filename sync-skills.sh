#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  sync-skills.sh                 # list skills and prompt for selection
  sync-skills.sh <skill-dir>...   # sync one or more skills by directory name
  sync-skills.sh all              # sync all skills
  sync-skills.sh --dry-run        # preview selected sync without writing target

Environment:
  CODEX_HOME  Codex home directory. Defaults to "$HOME/.codex".

Notes:
  - Source skills are discovered from skill directories next to this script.
  - Installed skills are synced to "$CODEX_HOME/skills/<skill-dir>".
  - Existing installed skills are backed up before sync.
  - Known replaced skills are moved to the backup directory after their replacement syncs.
USAGE
}

DRY_RUN=false
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
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
DRY_RUN_STAGE=""

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
skill_names=()
while IFS= read -r skill_file; do
  dir="$(dirname "${skill_file}")"
  key="$(basename "${dir}")"
  name="$(awk '
    BEGIN { in_fm=0 }
    NR == 1 && $0 == "---" { in_fm=1; next }
    in_fm && $0 == "---" { exit }
    in_fm && /^name:[[:space:]]*/ {
      sub(/^name:[[:space:]]*/, "")
      print
      exit
    }
  ' "${skill_file}")"
  if [[ -z "${name}" ]]; then
    name="${key}"
  fi
  skill_dirs+=("${key}")
  skill_names+=("${name}")
done < <(find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | sort)

if [[ ${#skill_dirs[@]} -eq 0 ]]; then
  echo "No skills found under ${SKILLS_DIR}" >&2
  exit 1
fi

print_skills() {
  echo "Available skills:"
  local i
  for i in "${!skill_dirs[@]}"; do
    printf '  [%d] %s  (%s)\n' "$((i + 1))" "${skill_dirs[$i]}" "${skill_names[$i]}"
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
  local key
  for key in "${skill_dirs[@]}"; do
    add_selected "${key}"
  done
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

  rsync_args=(-av --delete --exclude '.DS_Store' --exclude '.idea' --exclude '__pycache__' --exclude '*.pyc')
  if [[ "${DRY_RUN}" == "true" ]]; then
    rsync_args+=(--dry-run)
    if [[ ! -d "${target_dir}" ]]; then
      rsync_target="${DRY_RUN_STAGE}"
    fi
  else
    mkdir -p "${target_dir}"
  fi

  rsync "${rsync_args[@]}" "${source_dir}/" "${rsync_target}/"

  if [[ "${DRY_RUN}" == "false" ]]; then
    test -f "${target_dir}/SKILL.md"
    test -d "${target_dir}/references" || true
    local source_count target_count
    source_count="$(find "${source_dir}" -type f ! -name '.DS_Store' ! -name '*.pyc' ! -path '*/.idea/*' ! -path '*/__pycache__/*' | wc -l | tr -d ' ')"
    target_count="$(find "${target_dir}" -type f ! -name '.DS_Store' ! -name '*.pyc' ! -path '*/.idea/*' ! -path '*/__pycache__/*' | wc -l | tr -d ' ')"
    echo "    files: source=${source_count}, target=${target_count}"
    if [[ "${source_count}" != "${target_count}" ]]; then
      echo "    warning: source and target file counts differ; inspect rsync output" >&2
    fi
  fi
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
  if [[ -e "${backup_dir}" ]]; then
    echo "Retirement backup already exists: ${backup_dir}" >&2
    exit 1
  fi
  mv "${target_dir}" "${backup_dir}"
  test ! -e "${target_dir}"
  test -f "${backup_dir}/SKILL.md"
  echo "    backup: ${backup_dir}"
}

for key in "${selected[@]}"; do
  sync_one "${key}"
  echo
done

retire_replaced_skill "wind-project-coding-conventions" "wind-coding-conventions"

echo "Done. Restart Codex or open a new session if skill metadata does not refresh immediately."
