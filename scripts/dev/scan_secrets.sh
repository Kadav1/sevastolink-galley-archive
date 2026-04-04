#!/usr/bin/env bash
# Scan the repo for high-confidence hardcoded secret patterns.
# Intended for local use and pre-commit enforcement.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCAN_ROOT="${GALLEY_SECRET_SCAN_ROOT:-$REPO_ROOT}"

if ! command -v rg >/dev/null 2>&1; then
    echo "ripgrep (rg) is required for secret scanning." >&2
    exit 2
fi

FILE_LIST="$(mktemp)"
MATCH_FILE="$(mktemp)"
trap 'rm -f "$FILE_LIST" "$MATCH_FILE"' EXIT

collect_repo_files() {
    if git -C "$SCAN_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        git -C "$SCAN_ROOT" ls-files -z -c -o --exclude-standard
    else
        (
            cd "$SCAN_ROOT"
            find . \
                \( -path './.git' -o -path './node_modules' -o -path './dist' -o -path './coverage' -o -path './.venv' -o -path './data' \) -prune \
                -o -type f -print0
        )
    fi
}

filter_repo_files() {
    while IFS= read -r -d '' path; do
        path="${path#./}"
        case "$path" in
            .git/*|node_modules/*|dist/*|coverage/*|.venv/*|data/*)
                continue
                ;;
        esac
        if [ ! -f "$SCAN_ROOT/$path" ]; then
            continue
        fi
        printf '%s\0' "$path"
    done
}

run_scan() {
    local label="$1"
    shift

    local tmp_output
    local rc
    local matched
    tmp_output="$(mktemp)"
    matched=0
    while IFS= read -r -d '' path; do
        set +e
        (
            cd "$SCAN_ROOT"
            rg -nHI --with-filename --color never "$@" -- "$path"
        ) >>"$tmp_output"
        rc=$?
        set -e
        if [ "$rc" -eq 0 ]; then
            matched=1
            continue
        fi
        if [ "$rc" -ne 1 ]; then
            rm -f "$tmp_output"
            echo "Secret scan failed while evaluating $label." >&2
            exit "$rc"
        fi
    done <"$FILE_LIST"

    if [ "$matched" -eq 1 ]; then
        {
            echo "[$label]"
            cat "$tmp_output"
            echo ""
        } >>"$MATCH_FILE"
        rm -f "$tmp_output"
        return 0
    fi
    rm -f "$tmp_output"
    return 1
}

collect_repo_files | filter_repo_files >"$FILE_LIST"

echo "Scanning for hardcoded secrets under $SCAN_ROOT"

run_scan "Private keys and high-confidence tokens" \
    -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' \
    -e 'AKIA[0-9A-Z]{16}' \
    -e 'AIza[0-9A-Za-z_-]{35}' \
    -e 'ghp_[A-Za-z0-9]{36,}' \
    -e 'github_pat_[A-Za-z0-9_]{20,}' \
    -e 'sk-[A-Za-z0-9]{20,}' \
    -e 'xox[baprs]-[A-Za-z0-9-]{10,}' || true

run_scan "Credential URLs and assignment-style secrets" \
    -e 'https?://[^/@[:space:]]+:[^/@[:space:]]+@' \
    -e '(postgres(ql)?|mysql)://[^/@[:space:]]+:[^/@[:space:]]+@' \
    -e '[A-Za-z0-9_]*(API_KEY|CLIENT_SECRET|ACCESS_TOKEN|REFRESH_TOKEN|AUTH_TOKEN|PASSWORD|PASSWD|PRIVATE_KEY|SECRET)[A-Za-z0-9_]*[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_./:+@=-]{12,}' || true

if [ -s "$MATCH_FILE" ]; then
    echo ""
    echo "Potential secrets detected."
    echo ""
    cat "$MATCH_FILE"
    exit 1
fi

echo "No high-confidence secret patterns found."
