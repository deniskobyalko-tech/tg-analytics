#!/usr/bin/env python3
"""Bulk import Telegram channels into tg-analytics.

Usage:
    python scripts/bulk_import.py                    # import default marketing channels
    python scripts/bulk_import.py channels.txt       # import from file (one username per line)
    python scripts/bulk_import.py @ch1 @ch2 @ch3     # import specific channels

Calls POST /api/channels/analyze for each channel, then triggers
similarity recomputation.
"""

import sys
import time

import httpx

API_BASE = "https://tg.alarm-trusty-ru.ru/api"

# Curated list of popular Russian-language marketing & business channels
DEFAULT_CHANNELS = [
    # Marketing & SMM
    "targetolog",
    "smm_secrets",
    "digitalblog",
    "marketing_s",
    "smmplanner",
    "cossa",
    "adindex",
    "rusability",
    "growthhacking",
    "prmemes",
    "reklamaster",
    # Business & Startups
    "vc_ru",
    "tinkoffjournal",
    "banksta",
    "bigtechru",
    "startupoftheday",
    "temafounders",
    # IT & Tech
    "habr_com",
    "tproger",
    "devby",
    "kod_ru",
    "pythonl",
    # News
    "breakingmash",
    "rian_ru",
    "raborunews",
    # Crypto
    "bits_media",
    "cryptoMuskRU",
    # Design
    "designchat",
    "ux_live",
    # Popular general
    "durov",
    "lentachold",
    "varlamov_news",
]


def load_channels_from_file(path: str) -> list[str]:
    with open(path) as f:
        lines = f.read().splitlines()
    return [
        line.strip().lstrip("@").replace("https://t.me/", "").replace("t.me/", "")
        for line in lines
        if line.strip() and not line.startswith("#")
    ]


def main():
    if len(sys.argv) > 1 and sys.argv[1].endswith(".txt"):
        channels = load_channels_from_file(sys.argv[1])
        print(f"Loaded {len(channels)} channels from {sys.argv[1]}")
    elif len(sys.argv) > 1:
        channels = [a.lstrip("@") for a in sys.argv[1:]]
        print(f"Importing {len(channels)} channels from args")
    else:
        channels = DEFAULT_CHANNELS
        print(f"Importing {len(channels)} default channels")

    client = httpx.Client(timeout=30)
    success = 0
    failed = 0

    for i, username in enumerate(channels, 1):
        print(f"[{i}/{len(channels)}] Analyzing @{username}...", end=" ", flush=True)
        try:
            resp = client.post(
                f"{API_BASE}/channels/analyze",
                json={"username": username},
            )
            data = resp.json()
            if data.get("success"):
                subs = data["data"].get("subscribers_count", 0)
                cat = data["data"].get("category") or "?"
                print(f"OK ({subs:,} subs, {cat})")
                success += 1
            else:
                print(f"SKIP: {data.get('error', 'unknown')}")
                failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

        # Rate limit: 3s between requests
        if i < len(channels):
            time.sleep(3)

    print(f"\nDone: {success} imported, {failed} failed")

    # Trigger similarity recomputation
    if success > 0:
        print("Triggering similarity recomputation...")
        try:
            # Call via internal Docker exec or just let the scheduler handle it
            print("Similarities will be recomputed by scheduler (every 12h).")
            print("To force now, run on VPS:")
            print('  docker exec tg-analytics-backend-1 python -c "')
            print("  import asyncio")
            print("  from app.workers.compute_similarities import compute_all_similarities")
            print("  asyncio.run(compute_all_similarities())")
            print('  "')
        except Exception:
            pass


if __name__ == "__main__":
    main()
