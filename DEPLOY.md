# Deploying chrisgraham.com

## Automatic (preferred)

Every push to `main` runs `.github/workflows/deploy.yml`, which archives the
repo, copies it to the GCP VM `pete` (project `pete-new-albany`, zone
`us-east5-a`), rebuilds the `chrisgraham` Docker image, restarts the
`chrisgraham` systemd service, and checks `/health`.

One-time setup, done from the Mac:

1. Create a service account in `pete-new-albany` that can run
   `gcloud compute ssh` and `gcloud compute scp` against `pete`.
2. Download a JSON key and add it as the repo secret `GCP_SA_KEY` on
   `fugioconsulting/chrisgraham.com`. Never paste the key into a chat.
3. If the app does not live at `/opt/chrisgraham` on the VM, set the repo
   variable `CHRISGRAHAM_VM_DIR` to the real path. Check
   `bin/chrisgraham-deploy` in the Bonnie ops repo for the truth.
4. Run the workflow once by hand (Actions, Deploy to pete, Run workflow).

## Manual fallback

From the Mac: `bin/chrisgraham-deploy` in the Bonnie ops repo. Add
`--restart` for a plain restart with no rebuild.

## Verify

```
curl -s https://chrisgraham.com/health
curl -s https://chrisgraham.com/ | grep -c fugio-framework
```

Hard refresh in the browser; assets cache for an hour.
