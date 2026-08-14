---
name: "A → Z Launch checklist (A to Z)"
about: "Full launch & activation checklist: repo structure, docs, Stripe compliance, deployment, and activation steps. Use this to track activation tasks."
labels: ["launch", "checklist"]
assignees: []
---

# A → Z Launch checklist — Helios Empire

Use this issue to track the complete repository activation, deployment, and compliance tasks. Check items as you complete them.

## Repository and docs
- [ ] Drop repo structure into GitHub (confirm files/folders present)
- [ ] Verify README.md and mkdocs.yml are present and correct
- [ ] Build and preview docs locally: `mkdocs build` / `mkdocs serve`
- [ ] Confirm docs nav and legal pages (privacy, TOS, refund)

## MkDocs configuration
- [ ] Verify `mkdocs.yml` site_name, site_url, theme, nav
- [ ] Install Python dependencies: `pip install -r requirements.txt`
- [ ] Confirm docs deploy workflow (.github/workflows/docs-deploy.yml)

## Backend skeleton (Flask + Stripe)
- [ ] Review `app/server.py` and confirm health route works
- [ ] Review `app/webhook_handler.py` for correct Stripe webhook signing
- [ ] Ensure `app/stripe_config.md` documents required env vars
- [ ] Add secrets to deployment environment (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET)

## Stripe compliance & onboarding
- [ ] Paste business description and public info into Stripe onboarding
- [ ] Complete Stripe onboarding checklist and required legal pages
- [ ] Confirm refund policy and TOS are published on the website

## GitHub Actions & CI/CD
- [ ] Confirm `.github/workflows/docs-deploy.yml` exists
- [ ] Test workflow by pushing a docs change to the default branch
- [ ] Add any required secrets to repo settings (if workflows use them)

## Deployment & runtime
- [ ] Prepare host or container environment (Docker, VM, etc.)
- [ ] Configure environment variables and secrets on host
- [ ] Run application smoke test: `/health` returns 200 JSON
- [ ] Verify Stripe webhook endpoint is reachable and responds to Stripe

## Security, monitoring & operations
- [ ] Review key rotation, backups, and restore docs
- [ ] Configure monitoring and alerting (dashboards, runbooks)
- [ ] Document incident response and verification workflows

## Final activation
- [ ] Perform final verification checklist (DNS, TLS, secrets, health checks)
- [ ] Announce launch and monitor first 24–72 hours

---

## Paste-ready reference (short)

Repository layout (example):
```
helios-empire/
├─ README.md
├─ mkdocs.yml
├─ requirements.txt
├─ docs/
├─ app/
│  ├─ server.py
│  ├─ webhook_handler.py
│  ├─ stripe_config.md
└─ .github/workflows/docs-deploy.yml
```

MkDocs deps (requirements.txt):
```
mkdocs==1.5.*
mkdocs-material==9.5.*
```

Flask server example (app/server.py):
```
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return "Helios Empire – Ledger Integrity Platform"

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

Stripe webhook handler notes (app/webhook_handler.py):
- Env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- Use `stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)` and handle exceptions

GitHub Actions docs deploy (example):
```
name: Deploy docs
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
```
