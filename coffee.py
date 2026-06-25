"""
Download 100 coffee GIFs from the Giphy API.

Requirements:
    pip install requests

Usage:
    1. Get a free Giphy API key at https://developers.giphy.com/
    2. Set your API key below (or export GIPHY_API_KEY=your_key)
    3. Run: python download_coffee_gifs.py
"""

import os
import sys
import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY    = os.getenv("GIPHY_API_KEY", "YOUR_API_KEY_HERE")
QUERY      = "coffee"
TOTAL      = 100          # how many GIFs to download
BATCH_SIZE = 50           # Giphy max per request
OUTPUT_DIR = "coffee_gifs"
DELAY      = 0.2          # seconds between downloads (be polite)
# ─────────────────────────────────────────────────────────────────────────────


def fetch_gif_urls(api_key: str, query: str, total: int, batch: int) -> list[str]:
    """Pull GIF URLs from the Giphy search endpoint in batches."""
    urls = []
    endpoint = "https://api.giphy.com/v1/gifs/search"

    for offset in range(0, total, batch):
        limit = min(batch, total - offset)
        params = {
            "api_key": api_key,
            "q":       query,
            "limit":   limit,
            "offset":  offset,
            "rating":  "g",
            "lang":    "en",
        }
        resp = requests.get(endpoint, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])

        for item in data:
            url = item["images"]["original"]["url"]
            urls.append(url)

        print(f"  Fetched metadata: {len(urls)}/{total}")

    return urls[:total]


def download_gifs(urls: list[str], out_dir: str, delay: float) -> None:
    """Download each GIF to out_dir."""
    os.makedirs(out_dir, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        # Strip query-string so we get a clean filename
        clean_url = url.split("?")[0]
        filename  = f"coffee_{i:03d}.gif"
        filepath  = os.path.join(out_dir, filename)

        if os.path.exists(filepath):
            print(f"  [{i:>3}/{len(urls)}] Already exists — skipping {filename}")
            continue

        try:
            resp = requests.get(url, timeout=30, stream=True)
            resp.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            size_kb = os.path.getsize(filepath) / 1024
            print(f"  [{i:>3}/{len(urls)}] ✓ {filename}  ({size_kb:.1f} KB)")

        except requests.RequestException as exc:
            print(f"  [{i:>3}/{len(urls)}] ✗ Failed: {exc}", file=sys.stderr)

        time.sleep(delay)


def main() -> None:
    if API_KEY == "YOUR_API_KEY_HERE":
        sys.exit(
            "Error: set your Giphy API key in the script or via the "
            "GIPHY_API_KEY environment variable.\n"
            "Get one free at https://developers.giphy.com/"
        )

    print(f"Fetching metadata for {TOTAL} '{QUERY}' GIFs …")
    urls = fetch_gif_urls(API_KEY, QUERY, TOTAL, BATCH_SIZE)
    print(f"Got {len(urls)} URLs.\n")

    print(f"Downloading to ./{OUTPUT_DIR}/ …")
    download_gifs(urls, OUTPUT_DIR, DELAY)

    downloaded = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".gif")])
    print(f"\nDone! {downloaded} GIFs saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
