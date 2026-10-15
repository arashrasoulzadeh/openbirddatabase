#!/usr/bin/env bash
# Update and rebuild the stack on the server, then trim Docker's build cache.
#   ./deploy.sh            pull, rebuild, restart, keep at most BUILD_CACHE_LIMIT of build cache (default 1GB)
#   BUILD_CACHE_LIMIT=2GB ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

LIMIT="${BUILD_CACHE_LIMIT:-1GB}"

git pull --ff-only
docker compose up -d --build

# The build cache holds node_modules, npm's and pip's download caches and Next.js's compile cache.
# Least recently used entries are removed first, so the next build is still fast. Docker 27+ renamed the flag.
docker builder prune -f --reserved-space "$LIMIT" 2>/dev/null \
  || docker builder prune -f --keep-storage "$LIMIT"

echo "Build cache is capped at about $LIMIT."
docker system df | sed -n '1p;/Build Cache/p'
