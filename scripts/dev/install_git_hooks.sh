#!/usr/bin/env bash
# Install an opt-in pre-commit hook that runs the repo secret scan.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK_DIR="$REPO_ROOT/.git/hooks"
HOOK_PATH="$HOOK_DIR/pre-commit"
MARKER="# galley-managed-secret-scan-hook"

if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "This installer must be run from inside the Galley git repository." >&2
    exit 1
fi

mkdir -p "$HOOK_DIR"

if [ -f "$HOOK_PATH" ] && ! grep -q "$MARKER" "$HOOK_PATH"; then
    echo "Refusing to overwrite existing unmanaged pre-commit hook at $HOOK_PATH" >&2
    echo "Move it aside manually or merge the commands you need." >&2
    exit 1
fi

cat >"$HOOK_PATH" <<'EOF'
#!/usr/bin/env bash
# galley-managed-secret-scan-hook
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
bash "$REPO_ROOT/scripts/dev/scan_secrets.sh"
EOF

chmod +x "$HOOK_PATH"

echo "Installed pre-commit hook at $HOOK_PATH"
echo "The hook runs scripts/dev/scan_secrets.sh before each commit."
