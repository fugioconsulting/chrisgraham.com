#!/usr/bin/env bash
# One-time install on the VM. Run as root on pete:
#   curl -fsSL <raw url of this file> | bash      (or scp it over and run it)
#
# What it does:
# 1. Makes a read-only deploy key for GitHub if none exists and prints it.
#    Add it at https://github.com/fugioconsulting/chrisgraham.com/settings/keys
#    (read-only). Rerun this script after adding it.
# 2. Clones the repo to /opt/chrisgraham if not already there.
# 3. Installs the autodeploy service + timer and starts the timer.
set -euo pipefail

APP_DIR=/opt/chrisgraham
REPO=git@github.com:fugioconsulting/chrisgraham.com.git
KEY=/root/.ssh/chrisgraham_deploy

mkdir -p /root/.ssh && chmod 700 /root/.ssh
if [ ! -f "$KEY" ]; then
  ssh-keygen -t ed25519 -N '' -C 'pete chrisgraham autodeploy' -f "$KEY" >/dev/null
  echo
  echo "Add this READ-ONLY deploy key to the GitHub repo, then rerun this script:"
  echo
  cat "$KEY.pub"
  echo
  exit 0
fi

grep -q 'Host github.com' /root/.ssh/config 2>/dev/null || cat >>/root/.ssh/config <<EOF
Host github.com
  IdentityFile $KEY
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
EOF

if [ ! -d "$APP_DIR/.git" ]; then
  git clone -q "$REPO" "$APP_DIR"
fi
chmod +x "$APP_DIR/deploy/autodeploy.sh"

cp "$APP_DIR/deploy/chrisgraham-autodeploy.service" /etc/systemd/system/
cp "$APP_DIR/deploy/chrisgraham-autodeploy.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now chrisgraham-autodeploy.timer

echo "Installed. Timer status:"
systemctl list-timers chrisgraham-autodeploy.timer --no-pager
echo "Forcing a first deploy now:"
"$APP_DIR/deploy/autodeploy.sh" || true
