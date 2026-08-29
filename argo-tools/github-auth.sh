#!/bin/sh
set -euo pipefail

PRIVATE_KEY="/github-app/private-key"
TOKEN_OUT="/github-token/token"
API="https://api.github.com"

NOW=$(date +%s)
IAT=$((NOW - 60))
EXP=$((NOW + 540))

HEADER=$(printf '{"alg":"RS256","typ":"JWT"}' | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
PAYLOAD=$(printf '{"iss":"%s","iat":%d,"exp":%d}' "$GITHUB_APP_ID" "$IAT" "$EXP" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
SIGNATURE=$(printf '%s.%s' "$HEADER" "$PAYLOAD" | openssl dgst -sha256 -sign "$PRIVATE_KEY" -binary | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
JWT="${HEADER}.${PAYLOAD}.${SIGNATURE}"

# The installation is resolved from the target repository rather than pinned
# by id: the app is installed once per account (personal / organization), so
# moving a repository between accounts changes its installation. Passing the
# repository keeps the workflow definitions free of installation ids.
# GITHUB_APP_INSTALLATION_ID still works as an explicit override.
INSTALLATION_ID="${GITHUB_APP_INSTALLATION_ID:-}"
if [ -z "$INSTALLATION_ID" ]; then
  if [ -z "${GITHUB_REPO:-}" ]; then
    echo "Set GITHUB_REPO=owner/name or GITHUB_APP_INSTALLATION_ID" >&2
    exit 1
  fi
  RESPONSE=$(curl -sfL \
    -H "Authorization: Bearer ${JWT}" \
    -H "Accept: application/vnd.github+json" \
    "${API}/repos/${GITHUB_REPO}/installation") || {
    echo "Failed to resolve installation for ${GITHUB_REPO}" >&2
    exit 1
  }
  INSTALLATION_ID=$(printf '%s' "$RESPONSE" | jq -r .id)
  if [ -z "$INSTALLATION_ID" ] || [ "$INSTALLATION_ID" = "null" ]; then
    echo "No installation found for ${GITHUB_REPO}" >&2
    echo "$RESPONSE" >&2
    exit 1
  fi
fi

RESPONSE=$(curl -sf -X POST \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  "${API}/app/installations/${INSTALLATION_ID}/access_tokens")

TOKEN=$(printf '%s' "$RESPONSE" | jq -r .token)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "Failed to obtain installation token" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

printf '%s' "$TOKEN" > "$TOKEN_OUT"
