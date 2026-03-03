#!/bin/sh
set -euo pipefail

PRIVATE_KEY="/github-app/private-key"
TOKEN_OUT="/github-token/token"

NOW=$(date +%s)
IAT=$((NOW - 60))
EXP=$((NOW + 540))

HEADER=$(printf '{"alg":"RS256","typ":"JWT"}' | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
PAYLOAD=$(printf '{"iss":"%s","iat":%d,"exp":%d}' "$GITHUB_APP_ID" "$IAT" "$EXP" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
SIGNATURE=$(printf '%s.%s' "$HEADER" "$PAYLOAD" | openssl dgst -sha256 -sign "$PRIVATE_KEY" -binary | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
JWT="${HEADER}.${PAYLOAD}.${SIGNATURE}"

RESPONSE=$(curl -sf -X POST \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/app/installations/${GITHUB_APP_INSTALLATION_ID}/access_tokens")

TOKEN=$(printf '%s' "$RESPONSE" | jq -r .token)

if [ -z "$TOKEN" ]; then
  echo "Failed to obtain installation token" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

printf '%s' "$TOKEN" > "$TOKEN_OUT"
