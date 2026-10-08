# Deploying chrisgraham.com

## How it works

The VM deploys itself. A systemd timer on `pete` (GCP project
`pete-new-albany`, zone `us-east5-a`) runs `deploy/autodeploy.sh` every
minute. If GitHub `main` has a new commit, it pulls, rebuilds the
`chrisgraham` Docker image, restarts the `chrisgraham` service, and checks
`/health`. Log: `/var/log/chrisgraham-autodeploy.log` on the VM.

So: merge to `main`, wait about a minute, hard refresh. No GitHub Actions,
no secrets stored in GitHub, no Mac.

## One-time install (from the Mac, once)

```
gcloud compute ssh pete --project pete-new-albany --zone us-east5-a
sudo -i
# first run prints a deploy key
bash <(curl -fsSL https://raw.githubusercontent.com/fugioconsulting/chrisgraham.com/main/deploy/install.sh)
```

The repo is private, so the first run will fail to fetch the script unless
you copy it over instead:

```
gcloud compute scp deploy/install.sh pete:/tmp/install.sh --project pete-new-albany --zone us-east5-a
gcloud compute ssh pete --project pete-new-albany --zone us-east5-a -- sudo bash /tmp/install.sh
```

1. First run prints an ed25519 public key. Add it as a **read-only deploy
   key** at https://github.com/fugioconsulting/chrisgraham.com/settings/keys
2. Run the script again. It clones to `/opt/chrisgraham`, installs the
   timer, and deploys once.

If the existing checkout on the VM is somewhere other than
`/opt/chrisgraham`, or the systemd unit is not named `chrisgraham`, edit
the three constants at the top of `deploy/autodeploy.sh` and the
`ExecStart` path in the service file before installing. Check
`bin/chrisgraham-deploy` in the Bonnie ops repo for the truth.

## Manual fallback

From the Mac: `bin/chrisgraham-deploy` in the Bonnie ops repo. Or on the
VM: `sudo /opt/chrisgraham/deploy/autodeploy.sh`.

## Verify

```
curl -s https://chrisgraham.com/health
curl -s https://chrisgraham.com/ | grep -c fugio-framework
```
