#!/usr/bin/env bash
# One-shot installer for the CC Config shared customizations (non-plugin path).
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Lxcardoza993/claude-code-config/main/install.sh | bash
#   # or clone and run: ./install.sh
#
# For the richer path (auto health-check hook + /cc-config commands + updates),
# install as a Claude Code plugin instead — see README.md.
set -euo pipefail

REPO="Lxcardoza993/claude-code-config"
BRANCH="main"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "==> Cloning $REPO..."
if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Install git, or use the plugin path (see README)." >&2
  exit 1
fi
git clone --depth 1 -b "$BRANCH" "https://github.com/$REPO.git" "$TMP/repo" 2>/dev/null \
  || git clone --depth 1 "https://github.com/$REPO.git" "$TMP/repo"

echo "==> Running installer (copies statusline.py + wires settings.json)..."
python3 "$TMP/repo/cc-config/scripts/install.py"

echo
echo "==> Done. Restart Claude Code for the env vars to take effect."
echo "    Tip: for an auto health-check hook and /cc-config commands, install as a plugin:"
echo "      /plugin marketplace add Lxcardoza993/claude-code-config"
echo "      /plugin install cc-config@cc-config-market"
