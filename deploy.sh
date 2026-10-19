#!/usr/bin/env bash
# Update the stack on the server.
#   ./deploy.sh               pull the code, download the images CI built for this commit, restart (no compiling)
#   ./deploy.sh --if-changed  do nothing unless a newer commit exists (for cron, see docs/DEPLOYMENT.md)
#   ./deploy.sh --build       build the images on this server instead, then trim Docker's build cache
#
# Cache warm-up and other background jobs run in the `worker` Compose service (not here).
#
# Environment: WAIT_MINUTES (default 15) how long to wait for CI to publish the images,
#              BUILD_CACHE_LIMIT (default 1GB) build cache kept after --build
set -euo pipefail
cd "$(dirname "$0")"

WAIT_MINUTES="${WAIT_MINUTES:-15}"
LIMIT="${BUILD_CACHE_LIMIT:-1GB}"
MODE=prebuilt
IF_CHANGED=0
for arg in "$@"; do
  case "$arg" in
    --build) MODE=build ;;
    --if-changed) IF_CHANGED=1 ;;
    --no-warm)
      echo "note: --no-warm is obsolete; cache warm-up is handled by the worker service" >&2
      ;;
    *) echo "Usage: ./deploy.sh [--if-changed] [--build]" >&2; exit 2 ;;
  esac
done

# One deploy at a time (cron runs can overlap while waiting for CI)
if command -v flock >/dev/null 2>&1; then
  exec 9>.deploy.lock
  flock -n 9 || { echo "Another deploy is already running."; exit 0; }
fi

# The commit the running website container was built from (empty if it was built locally)
running_revision() {
  local id
  id="$(docker compose ps -q web 2>/dev/null | head -1)"
  [ -n "$id" ] || return 0
  docker inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' "$id" 2>/dev/null || true
}

if [ "$IF_CHANGED" -eq 1 ]; then
  git fetch -q
  if [ "$(running_revision)" = "$(git rev-parse '@{u}')" ]; then
    exit 0  # already running the newest commit
  fi
fi

PREVIOUS="$(running_revision)"
git pull --ff-only
HEAD_SHA="$(git rev-parse HEAD)"

healthy() {
  docker compose exec -T api python -c \
    "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health', timeout=3).status == 200 else 1)" \
    >/dev/null 2>&1
}

verify() {
  echo "Waiting for the API to answer..."
  for _ in $(seq 1 45); do
    if healthy; then
      echo "API is healthy."
      return 0
    fi
    sleep 2
  done
  echo "The API did not become healthy within 90 seconds. Last log lines:" >&2
  docker compose logs --tail 30 api >&2 || true
  if [ -n "$PREVIOUS" ]; then
    echo "Roll back to the previous version with:" >&2
    echo "  IMAGE_TAG=sha-${PREVIOUS:0:7} docker compose up -d" >&2
  fi
  exit 1
}

if [ "$MODE" = "build" ]; then
  docker compose up -d --build --remove-orphans
  docker compose up -d --force-recreate --no-deps api worker
  verify
  # The build cache holds node_modules, npm's and pip's download caches and Next.js's compile cache.
  # Least recently used entries go first, so the next build is still fast. Docker 27+ renamed the flag.
  docker builder prune -f --reserved-space "$LIMIT" 2>/dev/null \
    || docker builder prune -f --keep-storage "$LIMIT"
  echo "Built locally. Build cache is capped at about $LIMIT."
  exit 0
fi

# CI publishes the images a few minutes after a push; wait until they match the commit we just pulled.
web_image() { docker compose config --images | grep 'openbird-web' | head -1; }
ready=0
shown_login_hint=0
for attempt in $(seq 1 $((WAIT_MINUTES * 2))); do
  echo "Downloading the images (attempt $attempt)..."
  pull_log="$(mktemp)"
  # show the download as it happens (it used to be hidden, which made a slow download look like a hang)
  if ( set -o pipefail; docker compose pull web api 2>&1 | tee "$pull_log" ); then
    output="$(cat "$pull_log")"; rm -f "$pull_log"
    revision="$(docker image inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' "$(web_image)" 2>/dev/null || true)"
    if [ "$revision" = "$HEAD_SHA" ]; then
      ready=1
      break
    fi
    echo "Published images are for ${revision:0:8}; waiting for CI to publish ${HEAD_SHA:0:8} ($attempt)..."
  else
    output="$(cat "$pull_log")"; rm -f "$pull_log"
    echo "Could not pull the images yet ($attempt)..."
    if [ "$shown_login_hint" -eq 0 ] && echo "$output" | grep -qiE 'denied|unauthorized|authentication required'; then
      shown_login_hint=1
      echo "  The registry refused access. If the packages are private, log this server in once with a GitHub token" >&2
      echo "  that has the read:packages scope:  echo <TOKEN> | docker login ghcr.io -u <github-user> --password-stdin" >&2
    fi
  fi
  sleep 30
done

if [ "$ready" -ne 1 ]; then
  echo "The images for ${HEAD_SHA:0:8} were not available after $WAIT_MINUTES minutes." >&2
  echo "Check the 'Publish Images' run in GitHub Actions, or build here with: ./deploy.sh --build" >&2
  exit 1
fi

docker compose up -d --remove-orphans
# Recreate api/worker so in-memory indexes pick up bind-mounted birds/_index from this git pull
docker compose up -d --force-recreate --no-deps api worker
verify
docker image prune -f >/dev/null
echo "Deployed ${HEAD_SHA:0:8} from prebuilt images (worker handles cache warm-up and other jobs)."
