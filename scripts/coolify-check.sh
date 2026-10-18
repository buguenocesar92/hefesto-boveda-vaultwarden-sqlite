#!/usr/bin/env bash
# Verifica que un compose cumple el contrato Coolify para los kits del MVP Hefesto.
#   - Render del compose con variables de prueba (no secretos) → debe validar.
#   - Servicios sin profiles: nada que salte Traefik ni dé poder sobre el host.
#   - Nivel raíz y volúmenes: no usar `name:` fijo (Coolify pone el nombre).
#   - supabase-pg: la base del kit debe ser `mvp_prueba` y el sslmode `disable`.
#
# Uso: bash scripts/coolify-check.sh [BASE_DIR] [COMPOSE_FILE] [KIND]
#   BASE_DIR por defecto "."
#   COMPOSE_FILE por defecto "compose.yaml"
#   KIND: sqlite | supabase-pg | supabase-rest (por defecto sqlite)
#         también puede venir por env KIND=...
#
# Sale con código:
#   0 — cumple el contrato.
#   1 — argumentos inválidos o archivos ausentes.
#   2 — el render del compose falló.
#   3 — el compose tiene campos prohibidos (nombre o poderes sobre el host).
#   5 — el contrato de supabase-pg no se cumple.

set -euo pipefail

BASE_DIR=${1:-.}
COMPOSE_FILE=${2:-compose.yaml}
KIND=${3:-${KIND:-sqlite}}

# Argumentos no pueden empezar con '-' para no ser interpretados como flags
# por `docker compose` o el propio script.
if [[ "$BASE_DIR" == -* || "$COMPOSE_FILE" == -* ]]; then
  echo "ERROR: BASE_DIR y COMPOSE_FILE no pueden empezar con '-'" >&2
  exit 1
fi

if [[ "$KIND" != "sqlite" && "$KIND" != "supabase-pg" && "$KIND" != "supabase-rest" ]]; then
  echo "ERROR: KIND debe ser sqlite, supabase-pg o supabase-rest (recibido: '$KIND')" >&2
  exit 1
fi

if [[ ! -d "$BASE_DIR" ]]; then
  echo "ERROR: BASE_DIR '$BASE_DIR' no existe" >&2
  exit 1
fi

cd "$BASE_DIR"
COMPOSE_PATH="$COMPOSE_FILE"

if [[ ! -f "$COMPOSE_PATH" ]]; then
  echo "ERROR: $COMPOSE_PATH no existe" >&2
  exit 1
fi

# 1) Detección de variables referenciadas en el compose.
mapfile -t VARS < <(grep -oP '\$\{[A-Z_][A-Z0-9_]*' "$COMPOSE_PATH" \
  | sed -E 's/^\$\{//' \
  | sort -u)

# 2) Genera un .env temporal con valores ficticios no secretos.
TMP_ENV=$(mktemp -t coolify-check-env.XXXXXX)
TMP_OUT=$(mktemp -t coolify-check-out.XXXXXX)
TMP_ERR=$(mktemp -t coolify-check-err.XXXXXX)
cleanup() { rm -f "$TMP_ENV" "$TMP_OUT" "$TMP_ERR"; }
trap cleanup EXIT

for var in "${VARS[@]:-}"; do
  [[ -z "$var" ]] && continue
  case "$var" in
    *_HOST|*_URL|*_DOMAIN)
      echo "${var}=https://ejemplo.invalid" >> "$TMP_ENV"
      ;;
    OWNER_EMAIL)
      echo "${var}=owner@example.invalid" >> "$TMP_ENV"
      ;;
    DB_SSLMODE)
      echo "${var}=disable" >> "$TMP_ENV"
      ;;
    DB_NAME)
      echo "${var}=mvp_prueba" >> "$TMP_ENV"
      ;;
    *)
      echo "${var}=x123-test-no-secret" >> "$TMP_ENV"
      ;;
  esac
done

# 3) Render del compose con `docker compose config`.
#    Los argumentos ya fueron validados arriba (no pueden empezar con '-').
if ! docker compose --project-directory "$BASE_DIR" -f "$COMPOSE_FILE" \
     --env-file "$TMP_ENV" config --format json > "$TMP_OUT" 2> "$TMP_ERR"; then
  cat "$TMP_ERR" "$TMP_OUT" >&2
  echo "ERROR: docker compose config falló para $COMPOSE_FILE" >&2
  exit 2
fi

# 4) Chequeos del contrato. Se usan DOS fuentes para evitar bypass por caso
#    o comillas en el YAML:
#    a) `name:` fijo se busca en el YAML ORIGINAL con PyYAML (el render siempre
#       agrega `name` calculado por compose).
#    b) Los campos booleanos/de host de cada servicio se leen del JSON
#       normalizado por `docker compose config`.
set +e
CHECK_OUT=$(COMPOSE_PATH="$COMPOSE_PATH" TMP_OUT="$TMP_OUT" python3 <<'PY'
import json, os, re, sys

path = os.environ["COMPOSE_PATH"]
render_path = os.environ["TMP_OUT"]

errors = []

# (a) name fijo en raíz y dentro de volumes/networks sobre el YAML ORIGINAL.
try:
    import yaml  # PyYAML está disponible en los repos del ecosistema.
except ImportError:
    yaml = None

def fixed_name_in_subtree(node):
    """Devuelve (path, line) si algún sub-nodo tiene 'name' como CLAVE
    y cuyo valor sea un string no vacío. Consideramos 'name' como campo
    declarado cuando su clave aparece explícitamente en el mapeo.
    """
    hits = []
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(k, str) and k == "name":
                if v is not None and v != "":
                    hits.append((list(node.keys()), v))
            if isinstance(v, (dict, list)):
                hits.extend(fixed_name_in_subtree(v))
    elif isinstance(node, list):
        for item in node:
            hits.extend(fixed_name_in_subtree(item))
    return hits

if yaml is not None:
    with open(path) as f:
        raw_doc = f.read()

    class LineLoader(yaml.SafeLoader):
        pass

    def _construct_mapping(loader, node):
        loader.flatten_mapping(node)
        pairs = loader.construct_pairs(node)
        pairs.insert(0, ("__line__", node.start_mark.line + 1))
        return dict(pairs)

    LineLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        _construct_mapping,
    )
    try:
        docs = list(yaml.load_all(raw_doc, Loader=LineLoader))
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML inválido: {exc}")
        sys.exit(2)

    for doc in docs:
        if doc is None:
            continue
        line = doc.pop("__line__", 1) if isinstance(doc, dict) else 1

        # 'name' a nivel raíz
        if isinstance(doc, dict) and "name" in doc and doc["name"]:
            errors.append(f"'name:' fijo a nivel raíz (línea {line})")

        # 'name' en entries de volumes/networks
        for sect in ("volumes", "networks"):
            sub = doc.get(sect) if isinstance(doc, dict) else None
            if not isinstance(sub, dict):
                continue
            for entry_name, body in sub.items():
                if isinstance(body, dict) and "name" in body and body["name"]:
                    entry_line = body.pop("__line__", 0) if isinstance(body, dict) else 0
                    errors.append(
                        f"{sect}.{entry_name}: 'name:' fijo (línea {entry_line})"
                    )
else:
    # Fallback sin PyYAML — chequeo regex básico.
    for i, line in enumerate(open(path)):
        if re.match(r"^name:\s*\S", line):
            errors.append(f"'name:' fijo a nivel raíz (línea {i+1})")
            break

# (b) Campos de poder sobre el host y Traefik, sobre el render JSON.
with open(render_path) as f:
    render = json.load(f)

services = render.get("services") or {}

def has_profile(svc):
    pf = svc.get("profiles")
    return bool(pf)

def coerce_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "yes", "on", "1")
    if isinstance(v, (int, float)):
        return bool(v)
    return False

def coerce_str(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return ""
    return str(v).strip().strip("'\"").lower()

for svc_name, svc in services.items():
    if has_profile(svc):
        continue
    label = f"'{svc_name}' (sin profiles)"

    if svc.get("ports"):
        errors.append(f"{label}: tiene 'ports:' que evade Traefik")
    if svc.get("container_name"):
        errors.append(f"{label}: tiene 'container_name:' fijo")
    if coerce_bool(svc.get("privileged")):
        errors.append(f"{label}: tiene 'privileged: true'")
    if svc.get("cap_add"):
        errors.append(f"{label}: tiene 'cap_add:'")
    if svc.get("devices"):
        errors.append(f"{label}: tiene 'devices:'")
    if coerce_str(svc.get("network_mode")) == "host":
        errors.append(f"{label}: tiene 'network_mode: host'")
    if coerce_str(svc.get("pid")) == "host":
        errors.append(f"{label}: tiene 'pid: host'")
    if coerce_str(svc.get("ipc")) == "host":
        errors.append(f"{label}: tiene 'ipc: host'")
    sec_opts = svc.get("security_opt") or []
    if any("unconfined" in str(o).lower() for o in sec_opts):
        errors.append(f"{label}: tiene 'security_opt: unconfined'")

    raw = json.dumps(svc)
    if "docker.sock" in raw or "/var/run/docker.sock" in raw:
        errors.append(f"{label}: monta docker.sock")

if errors:
    print("FAIL")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)

print("OK")
PY
)
CHECK_STATUS=$?
set -e

if [[ "$CHECK_STATUS" -ne 0 ]]; then
  echo "$CHECK_OUT" >&2
  echo "FAIL: $COMPOSE_FILE no cumple el contrato Coolify" >&2
  exit 3
fi

# 5) supabase-pg: DB_NAME y DB_SSLMODE deben llegar al render del servicio web.
if [[ "$KIND" == "supabase-pg" ]]; then
  if ! grep -q "^DB_NAME=mvp_prueba" "$TMP_ENV"; then
    echo "FAIL: KIND=supabase-pg exige DB_NAME=mvp_prueba" >&2
    exit 5
  fi
  if ! grep -q "^DB_SSLMODE=disable" "$TMP_ENV"; then
    echo "FAIL: KIND=supabase-pg exige DB_SSLMODE=disable" >&2
    exit 5
  fi
  RENDER_ENVS=$(jq -r '.services | to_entries[]
                           | (.value.environment // {}) as $e
                           | $e | to_entries[]? | .value' "$TMP_OUT")
  if ! printf '%s\n' "$RENDER_ENVS" | grep -q "mvp_prueba"; then
    echo "FAIL: 'mvp_prueba' (DB_NAME) no aparece en el render del servicio web" >&2
    exit 5
  fi
  if ! printf '%s\n' "$RENDER_ENVS" | grep -q "disable"; then
    echo "FAIL: 'disable' (DB_SSLMODE) no aparece en el render del servicio web" >&2
    exit 5
  fi
fi

echo "$CHECK_OUT"
echo "OK: $COMPOSE_FILE cumple el contrato Coolify"
exit 0
