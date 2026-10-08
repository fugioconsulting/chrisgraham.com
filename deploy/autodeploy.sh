#!/usr/bin/env bash
# Runs on the VM every minute (systemd timer). If GitHub main has moved,
# pull it, rebuild the chrisgraham image, restart the service, check health.
# No GitHub Actions, no secrets in GitHub. Needs a read-only deploy key on
# the VM (see deploy/install.sh).
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/chrisgraham}"
BRANCH="${BRANCH:-main}"
IMAGE="${IMAGE:-chrisgraham}"
SERVICE="${SERVICE:-chrisgraham}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"
LOG="${LOG:-/var/log/chrisgraham-autodeploy.log}"

log() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }

cd "$APP_DIR"
git fetch -q origin "$BRANCH"
local_sha=$(git rev-parse HEAD)
remote_sha=$(git rev-parse "origin/$BRANCH")

if [ "$local_sha" = "$remote_sha" ]; then
  exit 0
fi

log "deploying $BRANCH ${local_sha:0:7} -> ${remote_sha:0:7}"
git reset -q --hard "origin/$BRANCH"
docker build -q -t "$IMAGE" . >>"$LOG" 2>&1
systemctl restart "$SERVICE"

for i in $(seq 1 15); do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    log "healthy at ${remote_sha:0:7}"
    exit 0
  fi
  sleep 2
done

log "WARNING: health check failed after deploy of ${remote_sha:0:7}"
exit 1
