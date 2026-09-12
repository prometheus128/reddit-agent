# reddit-agent

Minimal, well-behaved Reddit API client for a **single dedicated personal
account** (`valvetwister1`), operated by a human developer with the help of
an AI assistant on his own behalf.

This is the application the `u/valvetwister1` account refers to in its
Reddit API data-access request.

## What it does

- **Reads** Reddit: subreddit listings, search, thread and comment trees —
  used to keep the account informed in a small number of communities it
  participates in.
- **Writes** only when the human owner directs it: creating a post or a
  comment under the account's own identity. There is **no autonomous
  mass-posting, cross-posting, scraping, or bulk account creation** in this
  code — the write functions are explicit, single-action calls.

## How it authenticates

Standard OAuth 2.0 for a Reddit **script-type app** (the lowest-privilege
kind):

1. One-time `authorization_code` exchange using the script app's
   `client_id` / `client_secret` (password grant, as permitted for script
   apps).
2. The resulting **long-lived `refresh_token`** is stored locally in `.env`
   (never committed).
3. Fresh short-lived **access tokens** are minted from the refresh token
   whenever needed.

Credentials live only in `.env` on the owner's private machine. Nothing is
sent to any third party.

## Rate & abuse posture

- Built for the **free personal-use tier**. A built-in client-side limiter
  caps the client at **10 requests per minute** — well under the 100 QPM
  free-tier ceiling — leaving headroom for safety.
- No user data is collected, stored, or shared. The only data persisted is
  this account's own tokens.
- All content posted is for the owner's review and the account complies
  with Reddit's rules, each subreddit's rules, and this API's rate limits.

## Files

| File | Purpose |
|---|---|
| `client.py` | The client: token handling + read/write wrappers + rate limiter |
| `.env.example` | The (uncommitted) credential layout |

```bash
pip install requests   # only dependency
cp .env.example .env   # then fill in REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET
python3 client.py      # runs a self-check: GET /api/v1/me
```
