---
name: stealth-harvester
description: "Master stealth scraping and anti-bot bypass skill using nodriver (pure CDP, zero webdriver signatures) and curl_cffi (Chrome 130+ JA4 TLS fingerprint impersonation). Use when bypassing Cloudflare Turnstile, Akamai, DataDome, or extracting medical data without 403 Forbidden errors."
risk: low
source: "community-curated"
date_added: "2026-10-15"
---

# 🥷 Stealth Harvester — Anti-Bot & Cloudflare Bypass Mastery

## Overview
Standard Python HTTP libraries (`requests`, `urllib`, raw `playwright`, `selenium`) are immediately flagged and blocked by modern WAFs (Cloudflare Turnstile, Akamai, DataDome) due to **TLS Fingerprinting (JA3/JA4)** and **WebDriver signatures (`navigator.webdriver = true`)**.

This skill provides the exact architectural patterns to bypass these protections with 100% human-emulation reliability using:
1. **`curl_cffi`**: C-based TLS fingerprint impersonator matching real desktop Chrome 130+ cipher suites.
2. **`nodriver`**: The official next-generation successor to `undetected-chromedriver`. Completely eliminates WebDriver flags and communicates directly via Chrome DevTools Protocol (CDP).

---

## 🚀 1. High-Speed API & File Fetching with `curl_cffi`

Replace `requests` with `curl_cffi.requests`. It automatically handles HTTP/2 frame settings, ALPN, and SSL cipher ordering.

```python
from curl_cffi import requests

# Emulate exact desktop Chrome 130 TLS signature
session = requests.Session(impersonate="chrome124")

response = session.get(
    "https://example-protected-by-cloudflare.com/api/data",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
)

if response.status_code == 200:
    data = response.json()
    print("Successfully bypassed WAF!")
```

---

## 🌐 2. Interactive Browser Automation with `nodriver`

For sites that require JavaScript execution or interactive Turnstile challenge solving:

```python
import asyncio
import nodriver as uc

async def fetch_protected_page(url: str):
    # Starts Chromium without any automation flags (navigator.webdriver is absent)
    browser = await uc.start(
        headless=False,  # Set to True for server headless mode
        browser_args=["--disable-blink-features=AutomationControlled"]
    )
    
    page = await browser.get(url)
    
    # Wait for Cloudflare verification to complete naturally
    await page.sleep(4)
    
    content = await page.get_content()
    cookies = await page.send(uc.cdp.network.get_cookies())
    
    browser.stop()
    return content, cookies

if __name__ == "__main__":
    uc.loop().run_until_complete(fetch_protected_page("https://example.com"))
```

---

## 🛠️ 3. Dual-Mode Pipeline: The 100x Acceleration Pattern

1. **Step 1:** Use `nodriver` once to clear the Cloudflare Turnstile challenge and harvest the clearance session cookies (`cf_clearance`, `__cf_bm`).
2. **Step 2:** Pass the harvested cookies to `curl_cffi.Session(impersonate="chrome124")`.
3. **Step 3:** Stream bulk video/PDF files at multi-megabit speeds through pure C-sockets without launching further browser windows.
