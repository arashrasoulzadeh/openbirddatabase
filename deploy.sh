#!/usr/bin/env bash
# Update the stack on the server.
#   ./deploy.sh           pull the code, download the images CI built for this commit, restart (no compiling)
#   ./deploy.sh --build   build the images on this server instead, then trim Docker's build cache
#
# Environment: WAIT_MINUTES (default 15) how long to wait for CI to publish the images,
#              BUILD_CACHE_LIMIT (default 1GB) build cache kept after --build
set -euo pipefail
cd "$(dirname "$0")"

WAIT_MINUTES="${WAIT_MINUTES:-15}"
LIMIT="${BUILD_CACHE_LIMIT:-1GB}"

git pull --ff-only
HEAD_SHA="$(git rev-parse HEAD)"

if [ "${1:-}" = "--build" ]; then
  docker compose up -d --build
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
for attempt in $(seq 1 $((WAIT_MINUTES * 2))); do
  if docker compose pull web api >/dev/null 2>&1; then
    revision="$(docker image inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' "$(web_image)" 2>/dev/null || true)"
    if [ "$revision" = "$HEAD_SHA" ]; then
      ready=1
      break
    fi
    echo "Published images are for ${revision:0:8}; waiting for CI to publish ${HEAD_SHA:0:8} ($attempt)..."
  else
    echo "Could not pull the images yet (not published, or the package is private and this server is not logged in) ($attempt)..."
  fi
  sleep 30
done

if [ "$ready" -ne 1 ]; then
  echo "The images for ${HEAD_SHA:0:8} were not available after $WAIT_MINUTES minutes." >&2
  echo "Check the 'Publish Images' run in GitHub Actions, or build here with: ./deploy.sh --build" >&2
  exit 1
fi

docker compose up -d
docker image prune -f >/dev/null
echo "Deployed ${HEAD_SHA:0:8} from prebuilt images."
