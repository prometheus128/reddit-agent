#!/usr/bin/env python3
"""Minimal, well-behaved Reddit API client for the u/valvetwister1 account.

Single-account, human-operated, rate-limited to the free personal-use tier.
The only dependency is `requests`.

Usage:
    python3 client.py            # self-check: GET /api/v1/me
    python3 client.py search r/mecanica "piping" 2
    python3 client.py post r/mecanica "Title" "Body text"
    python3 client.py comment <link_id> "Comment text"

All write operations are single-action, explicit, and human-directed.
There is no autonomous posting, no mass operations, no data collection.
"""
import os
import sys
import time

import requests

# --- config (credentials come from .env, never hardcoded) -------------------
BASE = os.path.dirname(os.path.abspath(__file__))


def _load_env():
    env = {}
    path = os.path.join(BASE, ".env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


ENV = _load_env()
CLIENT_ID = ENV.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = ENV.get("REDDIT_CLIENT_SECRET")
REFRESH_TOKEN = ENV.get("REDDIT_REFRESH_TOKEN")
REDIRECT_URI = "http://localhost"
USER_AGENT = "linux:valvetwister1-personal-client:v1.0 (personal account)"

# Hard client-side cap: 10 req/min = well under the 100 QPM free tier.
RATE_LIMIT = 10
_last = [0.0]


def _throttle():
    wait = 60.0 / RATE_LIMIT - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()


# --- token handling ----------------------------------------------------------
def refresh_access_token() -> str:
    """Exchange the long-lived refresh token for a short-lived access token."""
    r = requests.post(
        "https://www.reddit.com/api/v1/refresh",
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _headers():
    return {"User-Agent": USER_AGENT,
            "Authorization": f"Bearer {refresh_access_token()}"}


# --- read -------------------------------------------------------------------
def get(path, params=None):
    _throttle()
    r = requests.get("https://www.reddit.com" + path,
                     headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def me():
    return get("/api/v1/me")


def search(sub, query, limit=10):
    return get(f"{sub}/search",
               {"q": query, "restrict_sr": 1, "limit": min(limit, 100)})


def listing(sub, sort="hot", limit=10):
    return get(f"{sub}/" + sort, {"limit": min(limit, 100)})


# --- write (explicit, single-action, human-directed) --------------------------
def post(sub, title, body):
    _throttle()
    r = requests.post(
        "https://www.reddit.com/api/submit",
        headers=_headers(),
        data={"sr": sub.lstrip("r/"), "title": title,
              "text": body, "kind": "t3"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("json", {}).get("data", {})


def comment(link_id, text):
    _throttle()
    r = requests.post(
        "https://www.reddit.com/api/comment",
        headers=_headers(),
        data={"link_id": link_id, "text": text, "kind": "t1"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("json", {}).get("data", {})


# --- self-check ---------------------------------------------------------------
if __name__ == "__main__":
    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
        print("Missing credentials in .env (REDDIT_CLIENT_ID / "
              "REDDIT_CLIENT_SECRET / REDDIT_REFRESH_TOKEN)")
        sys.exit(1)
    info = me()
    print("OK - logged in as u/%s (id %s, created %s)" %
          (info.get("name"), info.get("id"), info.get("created_utc")))
