#!/usr/bin/env bash
# Runs once when the dev container is created. Safe to run again.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "› Installing pnpm (version from package.json) and website dependencies"
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0
corepack enable
pnpm install

echo "› Installing pipenv and API dependencies"
pip install --user --quiet pipenv
(cd apps/api && pipenv install --dev)

if [ ! -f .env ]; then
  echo "› Creating .env from .env.example"
  cp .env.example .env
fi

# In Codespaces the browser can't reach the container's 127.0.0.1, so point
# the website at the API's forwarded URL instead. Make port 8000 public in the
# Ports panel (or with `gh codespace ports visibility 8000:public`) so the
# browser can load thumbnails from it.
if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  api_url="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  sed -i "s#^VITE_API_BASE_URL=.*#VITE_API_BASE_URL=\"${api_url}\"#" .env
  echo "› Codespaces: VITE_API_BASE_URL set to ${api_url}"
fi

echo "✓ Ready. Run \`pnpm dev\` to start the website (port 5173) and the API (port 8000)."
