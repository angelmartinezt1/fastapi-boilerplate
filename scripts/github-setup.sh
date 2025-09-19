#!/usr/bin/env bash
set -euo pipefail

# ==============================================
# Uso:
#   ./scripts/github-setup.sh OWNER/REPO
# Requiere:
#   - gh CLI instalado (dnf install gh  o  ver instrucciones oficiales)
#   - gh auth login   (ya autenticado)
#   - jq
#   - Variables de entorno para los secrets (ej. DB_PASSWORD, DB_PASSWORD_DEV...)
# ==============================================

REPO_SLUG="${1:-}"
CONFIG_PATH="$(dirname "$0")/github-env.json"

if [[ -z "${REPO_SLUG}" ]]; then
  echo "Uso: $0 OWNER/REPO"
  exit 1
fi

need() { command -v "$1" >/dev/null 2>&1 || { echo "❌ Falta '$1'"; exit 1; }; }
need gh
need jq
gh auth status -h github.com >/dev/null || { echo "❌ Ejecuta 'gh auth login' primero"; exit 1; }

# Helpers
expand_env_ref() {
  local v="$1"
  if [[ "$v" =~ ^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$ ]]; then
    printf '%s' "${!BASH_REMATCH[1]-}"
  else
    printf '%s' "$v"
  fi
}

create_env() {
  local env="$1"
  echo "🛠️  Creando/actualizando environment: $env"
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/${REPO_SLUG}/environments/${env}" >/dev/null
}

set_repo_var() {
  local k="$1" v="$2"
  echo "🔧 Repo Var: ${k}=${v}"
  gh variable set "$k" --body "$v" -R "$REPO_SLUG" >/dev/null
}

set_repo_secret() {
  local k="$1" v="$2"
  [[ -z "$v" || "$v" == "null" ]] && { echo "⚠️  Repo Secret $k sin valor. Saltando."; return; }
  echo "🔐 Repo Secret: ${k}=***"
  printf "%s" "$v" | gh secret set "$k" -R "$REPO_SLUG" --body - >/dev/null
}

set_env_var() {
  local env="$1" k="$2" v="$3"
  echo "🔧 Env Var [$env]: ${k}=${v}"
  gh variable set "$k" --body "$v" -R "$REPO_SLUG" -e "$env" >/dev/null
}

set_env_secret() {
  local env="$1" k="$2" v="$3"
  [[ -z "$v" || "$v" == "null" ]] && { echo "⚠️  Env Secret $k ($env) sin valor. Saltando."; return; }
  echo "🔐 Env Secret [$env]: ${k}=***"
  printf "%s" "$v" | gh secret set "$k" -R "$REPO_SLUG" -e "$env" --body - >/dev/null
}

# =========================
# Procesar repo variables/secrets
# =========================
echo "📦 Repo-level..."
jq -r '.repo.variables | to_entries[]? | "\(.key)=\(.value)"' "$CONFIG_PATH" |
while IFS='=' read -r k v; do
  v2="$(expand_env_ref "$v")"
  set_repo_var "$k" "$v2"
done

jq -r '.repo.secrets | to_entries[]? | "\(.key)=\(.value)"' "$CONFIG_PATH" |
while IFS='=' read -r k v; do
  v2="$(expand_env_ref "$v")"
  set_repo_secret "$k" "$v2"
done

# =========================
# Procesar environments
# =========================
len=$(jq '.environments | length' "$CONFIG_PATH")
for i in $(seq 0 $((len-1))); do
  ENV_NAME=$(jq -r ".environments[$i].name" "$CONFIG_PATH")
  create_env "$ENV_NAME"

  jq -r ".environments[$i].variables | to_entries[]? | \"\(.key)=\(.value)\"" "$CONFIG_PATH" |
  while IFS='=' read -r k v; do
    v2="$(expand_env_ref "$v")"
    set_env_var "$ENV_NAME" "$k" "$v2"
  done

  jq -r ".environments[$i].secrets | to_entries[]? | \"\(.key)=\(.value)\"" "$CONFIG_PATH" |
  while IFS='=' read -r k v; do
    v2="$(expand_env_ref "$v")"
    set_env_secret "$ENV_NAME" "$k" "$v2"
  done
done

echo "✅ Configuración sincronizada en ${REPO_SLUG}"
