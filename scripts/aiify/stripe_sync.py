#!/usr/bin/env python3
"""AIify price ladder: make the Stripe payment links once, then keep the
page's sold count current.

Reads STRIPE_AIIFY_KEY (a restricted Stripe key; Payment Links read is
enough now that the four links exist, add Products and Payment Links write
only to rebuild them) from the environment and writes
docs/aiify-status.json, which docs/aiify.html reads.

  python3 scripts/aiify/stripe_sync.py            # create what is missing, then count
  python3 scripts/aiify/stripe_sync.py --dry-run  # print the plan, call nothing

Ladder: 5 spots at each of $1,500, $2,000, $2,500, $3,000. Each price has
its own payment link capped at 5 completed checkouts by Stripe itself
(restrictions.completed_sessions.limit), so a price cannot oversell even if
this script has not run yet. Standard library only.

Manual equivalent (no script): in the Stripe dashboard make four payment
links for "AIify" at the four prices, set "Limit the number of payments" to
5 on each, paste the four URLs into docs/aiify-status.json "links", and bump
"sold" by hand after each sale.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.stripe.com/v1"
PRICES = [1500, 2000, 2500, 3000]
PER_TIER = 5
PRODUCT_NAME = "AIify: 4 weekly AI coaching sessions with Chris Graham"
INACTIVE = ("These 5 spots are gone. The current price is at "
            "https://chrisgraham.com/aiify")
THANKS = ("You're in. Chris will email you within one business day to "
          "schedule your four sessions.")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs",
                   "aiify-status.json")


def call(key, method, path, params=None):
    data = None
    url = API + path
    if params and method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    elif params:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    token = base64.b64encode((key + ":").encode()).decode()
    req.add_header("Authorization", "Basic " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit("Stripe said %s on %s %s: %s" % (e.code, method, path, body))


def listing(key, path, params):
    """Every object from a Stripe list endpoint."""
    out, params = [], dict(params, limit=100)
    while True:
        page = call(key, "GET", path, params)
        out.extend(page["data"])
        if not page.get("has_more") or not page["data"]:
            return out
        params["starting_after"] = page["data"][-1]["id"]


def ensure_links(key):
    """One payment link per price, found by metadata or created."""
    have = {}
    for link in listing(key, "/payment_links", {}):
        tier = (link.get("metadata") or {}).get("aiify_tier")
        if tier is not None and tier.isdigit() and int(tier) not in have:
            have[int(tier)] = link
    product = None
    for i, dollars in enumerate(PRICES):
        if i in have:
            continue
        if product is None:
            for p in listing(key, "/products", {"active": "true"}):
                if (p.get("metadata") or {}).get("aiify") == "1":
                    product = p["id"]
                    break
        if product is None:
            product = call(key, "POST", "/products", {
                "name": PRODUCT_NAME, "metadata[aiify]": "1"})["id"]
        have[i] = call(key, "POST", "/payment_links", {
            "line_items[0][price_data][currency]": "usd",
            "line_items[0][price_data][product]": product,
            "line_items[0][price_data][unit_amount]": str(dollars * 100),
            "line_items[0][quantity]": "1",
            # Plain Fugio Consulting charge, not Stripe as merchant of record.
            "managed_payments[enabled]": "false",
            "restrictions[completed_sessions][limit]": str(PER_TIER),
            "inactive_message": INACTIVE,
            "after_completion[type]": "hosted_confirmation",
            "after_completion[hosted_confirmation][custom_message]": THANKS,
            "metadata[aiify_tier]": str(i)})
        print("created the $%d link" % dollars)
    return [have[i] for i in range(len(PRICES))]


def main():
    if "--dry-run" in sys.argv:
        for d in PRICES:
            print("would ensure a payment link at $%d capped at %d sales"
                  % (d, PER_TIER))
        return
    key = os.environ.get("STRIPE_AIIFY_KEY", "").strip()
    if not key:
        print("STRIPE_AIIFY_KEY is not set; leaving the page as it is.")
        return
    links = ensure_links(key)
    # Stripe keeps the running count on each link.
    sold = 0
    for link in links:
        done = ((link.get("restrictions") or {}).get("completed_sessions")
                or {}).get("count", 0)
        sold += min(int(done), PER_TIER)
    status = {"sold": sold, "links": [l["url"] for l in links]}
    with open(OUT, "w") as f:
        json.dump(status, f, indent=2)
        f.write("\n")
    print("sold %d of %d" % (sold, len(PRICES) * PER_TIER))


if __name__ == "__main__":
    main()
