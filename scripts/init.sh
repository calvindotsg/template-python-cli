#!/usr/bin/env bash
# init.sh — initialize a repo created from template-python-cli
#
# Usage: bash scripts/init.sh <tool-name> "<description>" [author]
#
# Prerequisites: gh, uv, git
#
# This script is self-deleting: the entire scripts/ directory is removed as the
# final step. Safe because execution is trampolined into a /tmp copy first.

set -euo pipefail

# --- Step 1: Trampoline re-exec into /tmp so we can delete scripts/ safely ---
if [ -z "${CONSUMER_INIT_TRAMPOLINE:-}" ]; then
    TMP=$(mktemp)
    cp "$0" "$TMP"
    chmod +x "$TMP"
    export CONSUMER_INIT_TRAMPOLINE=1
    exec bash "$TMP" "$@"
else
    trap 'rm -f "$0"' EXIT
fi

# --- Step 2: Parse args (fall back to interactive prompts) ---
TOOL_NAME="${1:-}"
DESCRIPTION="${2:-}"
AUTHOR_ARG="${3:-}"

if [ -z "$TOOL_NAME" ]; then
    read -rp "Tool name (e.g. my-tool): " TOOL_NAME
fi
if [ -z "$DESCRIPTION" ]; then
    read -rp "Description: " DESCRIPTION
fi

# --- Step 3: Validate tool name ---
if ! echo "$TOOL_NAME" | grep -qE '^[a-z][a-z0-9-]*$'; then
    echo "Error: tool name must match ^[a-z][a-z0-9-]*$ (lowercase letters, digits, hyphens)" >&2
    exit 1
fi

# --- Step 4: Compute derived values ---
TOOL_SLUG="${TOOL_NAME//-/_}"
ENV_PREFIX=$(echo "$TOOL_SLUG" | tr '[:lower:]' '[:upper:]')
YEAR=$(date +%Y)
PYPI_HOMEPAGE="https://pypi.org/project/$TOOL_NAME/"

if [ -n "$AUTHOR_ARG" ]; then
    AUTHOR="$AUTHOR_ARG"
elif command -v gh &>/dev/null; then
    AUTHOR=$(gh api user --jq '.name // .login' 2>/dev/null || git config user.name 2>/dev/null || echo "")
else
    AUTHOR=$(git config user.name 2>/dev/null || echo "")
fi
if [ -z "$AUTHOR" ]; then
    read -rp "Author name: " AUTHOR
fi

echo "==> Initializing: $TOOL_NAME"
echo "    slug:        $TOOL_SLUG"
echo "    env prefix:  ${ENV_PREFIX}_"
echo "    author:      $AUTHOR"
echo "    year:        $YEAR"
echo ""

# --- Step 5: In-place substitution ---
# Exclusions: .git/, .venv/, dist/, __pycache__/, .ruff_cache/, .pytest_cache/, scripts/, uv.lock
_sed_inplace() {
    local from="$1" to="$2"
    find . \
        -not -path './.git/*' \
        -not -path './.venv/*' \
        -not -path './dist/*' \
        -not -path './__pycache__/*' \
        -not -path './.ruff_cache/*' \
        -not -path './.pytest_cache/*' \
        -not -path './scripts/*' \
        -not -name 'uv.lock' \
        -type f \
        -exec env LC_ALL=C sed -i.bak "s|$from|$to|g" {} +
    find . -name '*.bak' -delete
}

# Sentinel strings first (strictly-parsed files)
_sed_inplace "template-python-cli" "$TOOL_NAME"
_sed_inplace "template_python_cli" "$TOOL_SLUG"
_sed_inplace "TEMPLATE_PYTHON_CLI" "$ENV_PREFIX"

# Markdown tokens (free-form values)
_sed_inplace "{{TOOL_NAME}}" "$TOOL_NAME"
_sed_inplace "{{TOOL_DESCRIPTION}}" "$DESCRIPTION"
_sed_inplace "{{AUTHOR}}" "$AUTHOR"
_sed_inplace "{{YEAR}}" "$YEAR"
_sed_inplace "{{PYPI_HOMEPAGE}}" "$PYPI_HOMEPAGE"

echo "==> Substitutions applied."

# --- Step 6: Rename package directory ---
if git rev-parse --git-dir &>/dev/null 2>&1; then
    git mv "src/template_python_cli" "src/$TOOL_SLUG" 2>/dev/null || mv "src/template_python_cli" "src/$TOOL_SLUG"
else
    mv "src/template_python_cli" "src/$TOOL_SLUG"
fi
echo "==> Renamed src/template_python_cli -> src/$TOOL_SLUG"

# --- Step 7: Strip release.yml CI guard ---
sed -i.bak '/if: github\.repository != .*/d' .github/workflows/release.yml
find . -name '*.bak' -delete
echo "==> Stripped release.yml CI guard."

# --- Step 8: Strip template-usage block from README ---
sed -i.bak '/<!-- template-usage-block-start -->/,/<!-- template-usage-block-end -->/d' README.md
find . -name '*.bak' -delete
echo "==> Stripped README template block."

# --- Step 9: Remove TEMPLATE.md ---
rm -f TEMPLATE.md
echo "==> Removed TEMPLATE.md."

# --- Step 10: Regenerate lockfile ---
if command -v uv &>/dev/null; then
    uv sync
    echo "==> Regenerated uv.lock."
else
    echo "WARNING: uv not found, skipping uv sync. Run 'uv sync' manually." >&2
fi

# --- Step 11: Remove scripts/ directory ---
if git rev-parse --git-dir &>/dev/null 2>&1; then
    git rm -rf scripts 2>/dev/null || rm -rf scripts
else
    rm -rf scripts
fi
echo "==> Removed scripts/."

# --- Step 12: Commit ---
if git rev-parse --git-dir &>/dev/null 2>&1; then
    if [ -n "$(git status --porcelain)" ]; then
        git add -A
        git commit -m "chore(repo): initialize from template-python-cli"
        echo "==> Committed initialization."
    fi
fi

# --- Step 13: Next steps ---
echo ""
echo "==> Done! Next steps:"
echo "    1. bash /path/to/.github/scripts/setup-repo.sh calvindotsg/$TOOL_NAME"
echo "    2. gh repo edit calvindotsg/$TOOL_NAME --homepage '$PYPI_HOMEPAGE' --add-topic python --add-topic cli"
echo "    3. Configure PyPI trusted publisher at pypi.org (environment: pypi)"
echo "    4. Set RELEASE_PLEASE_APP_ID (var) + RELEASE_PLEASE_PRIVATE_KEY (secret) in repo settings"
echo "    5. Push a feat: commit to trigger the first release-please PR"
