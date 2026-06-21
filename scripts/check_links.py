#!/usr/bin/env python3
"""On-demand link checker for the Hari.me portfolio site.

Extracts every http(s) URL from index.html and data/portfolio.json, requests
each one, and reports its status. Exits non-zero if any link is genuinely
broken (404 / 5xx / connection error), so it can gate a deploy or CI run.

Usage:
    python3 scripts/check_links.py            # check everything
    python3 scripts/check_links.py --verbose  # also list OK links

No third-party dependencies — uses only the standard library.
"""
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [ROOT / "index.html", ROOT / "data" / "portfolio.json"]

# Asset / non-navigable endpoints that aren't user-facing links.
SKIP_SUBSTRINGS = (
    "schema.org",            # JSON-LD vocabulary, not a real page
    "fonts.googleapis.com",  # font stylesheet
    "img.shields.io",        # badge image (dynamic)
    "goatcounter.com/count", # analytics beacon
)

# Hosts that block automated clients (Cloudflare / anti-bot) and return
# 403/999/429 to scripts while working fine in a browser. Treated as a
# warning, not a failure.
BOT_BLOCKED_HOSTS = (
    "linkedin.com",
    "medium.com",
    "towardsdev.com",
    "researchgate.net",
)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
TIMEOUT = 25
URL_RE = re.compile(r'https?://[^\s"\'<>)\\]+')


def extract_urls():
    urls = set()
    for path in SOURCES:
        text = path.read_text(encoding="utf-8")
        for raw in URL_RE.findall(text):
            url = raw.rstrip(".,;")
            if any(s in url for s in SKIP_SUBSTRINGS):
                continue
            urls.add(url)
    return sorted(urls)


def check(url):
    """Return (status_code_or_None, error_string_or_None).

    Shells out to curl so we use the system CA trust store and a real
    browser User-Agent, following redirects.
    """
    try:
        proc = subprocess.run(
            ["curl", "-sSL", "-o", "/dev/null", "-w", "%{http_code}",
             "-A", UA, "--max-time", str(TIMEOUT), url],
            capture_output=True, text=True, timeout=TIMEOUT + 5,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    code_str = proc.stdout.strip()
    if code_str.isdigit() and code_str != "000":
        return int(code_str), None
    err = proc.stderr.strip().splitlines()
    return None, (err[-1] if err else "connection failed")


def is_bot_blocked(url):
    return any(h in url for h in BOT_BLOCKED_HOSTS)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    urls = extract_urls()
    print(f"Checking {len(urls)} links from {', '.join(s.name for s in SOURCES)}\n")

    results = {}
    with ThreadPoolExecutor(max_workers=10) as pool:
        for url, (code, err) in zip(urls, pool.map(check, urls)):
            results[url] = (code, err)

    failures, warnings, ok = [], [], []
    for url in urls:
        code, err = results[url]
        if err is not None or (code is not None and code >= 400):
            if is_bot_blocked(url) and (code in (403, 429, 999) or err):
                warnings.append((url, code, err))
            else:
                failures.append((url, code, err))
        else:
            ok.append((url, code))

    if verbose:
        for url, code in ok:
            print(f"  OK   {code}  {url}")

    if warnings:
        print("Warnings (bot-blocked host — verify manually in a browser):")
        for url, code, err in warnings:
            print(f"  WARN {code or err}  {url}")
        print()

    if failures:
        print("BROKEN links:")
        for url, code, err in failures:
            print(f"  FAIL {code or err}  {url}")
        print()

    print(f"Summary: {len(ok)} OK, {len(warnings)} warnings, {len(failures)} broken")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
