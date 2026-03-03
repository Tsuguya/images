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

TOKEN=$(wget -qO- \
  --header="Authorization: Bearer ${JWT}" \
  --header="Accept: application/vnd.github+json" \
  "https://api.github.com/app/installations/${GITHUB_APP_INSTALLATION_ID}/access_tokens" \
  --post-data="" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

printf '%s' "$TOKEN" > "$TOKEN_OUT"
