# Deploying chrisgraham.com

## How it works

GitHub Pages serves the `docs/` folder of `main`. Merge to `main`, wait
about a minute, hard refresh. That is the whole deploy.

## One-time setup (done once, in the browser)

1. **Repo visibility.** Pages on a private repo needs GitHub Pro. Either
   upgrade, or make the repo public at
   https://github.com/fugioconsulting/chrisgraham.com/settings
   (Danger Zone, Change visibility). The site is public anyway.
2. **Enable Pages.** https://github.com/fugioconsulting/chrisgraham.com/settings/pages
   Source: Deploy from a branch. Branch: `main`, folder `/docs`. Save.
3. **Custom domain.** Same page, Custom domain: `chrisgraham.com`. Save.
   Tick Enforce HTTPS once the DNS check passes.
4. **DNS** at the registrar for chrisgraham.com:

   | Type  | Host | Value                       |
   |-------|------|-----------------------------|
   | A     | @    | 185.199.108.153             |
   | A     | @    | 185.199.109.153             |
   | A     | @    | 185.199.110.153             |
   | A     | @    | 185.199.111.153             |
   | CNAME | www  | fugioconsulting.github.io   |

   Remove the old A record that points at the `pete` VM.

5. **Retire the VM service.** On `pete`: `sudo systemctl disable --now chrisgraham`.
   Delete `bin/chrisgraham-deploy` from the Bonnie ops repo or mark it dead.

## Verify

```
curl -sI https://chrisgraham.com/ | head -1
curl -s https://chrisgraham.com/ | grep -c fugio-framework
curl -sI https://chrisgraham.com/coaching | head -1
```

## Local preview

`npm start`, then http://localhost:3000. Serves the same `docs/` folder.
