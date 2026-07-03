# Ethical Hacking Tools

A collection of Python scripts built while learning ethical hacking / penetration testing fundamentals — network reconnaissance, OSINT, and web scanning.

> ⚠️ **Educational Use Only**
> These tools are built strictly for learning purposes and for use against systems you own or are explicitly authorized to test (e.g. TryHackMe rooms, personal lab environments, VulnHub VMs). Scanning or scraping systems without permission is illegal in most jurisdictions. Use responsibly.

---

## Contents

| Script | Description |
|---|---|
| [`port_scanner.py`](./port_scanner.py) | Multi-threaded TCP port scanner with service banner grabbing |
| [`e_mail_scrapper.py`](./e_mail_scrapper.py) | Crawls a target website (same-domain links) and extracts email addresses via regex |

---

## Requirements

- Python 3.8+
- See [`requirements.txt`](./requirements.txt)

### Installation

```bash
git clone https://github.com/Canbirlik/ethical_hacking_tools.git
cd ethical_hacking_tools
pip install -r requirements.txt
```

---

## 🔍 port_scanner.py

A TCP port scanner that:
- Scans one or more targets (comma-separated) in parallel using threads
- Resolves hostnames to IPs
- Grabs service banners via a basic HTTP `HEAD` request when possible
- Colorizes output for readability

### Usage

```bash
python port_scanner.py
```

You'll be prompted for input:

```
[*] Enter Targets to Scan (Split them by ,): scanme.nmap.org
[*] Enter How Many Ports You Want to Scan: 1000
```

### Example Output

```
[*] Scanning scanme.nmap.org (45.33.32.156)
[*] Started at 2026-07-03 14:02:11
--------------------------------------------------
[+] Port 22 Open
[+] Port 80 Open | HTTP/1.1 200 OK
--------------------------------------------------
[*] Scan completed at 2026-07-03 14:02:14
```

### Notes

- Uses a 0.5s socket timeout per port to keep scans fast.
- Threads are batched in groups of 100 to avoid overwhelming the system.
- Banner grabbing currently only works reliably against HTTP-speaking services; non-HTTP services (SSH, FTP, etc.) will show as open without a banner.

---

## ✉️ e_mail_scrapper.py

A breadth-first web crawler that:
- Starts from a target URL and follows same-domain links
- Extracts email addresses from each page's HTML via regex
- Stops after visiting 100 pages (configurable in code)
- Sends a browser-like `User-Agent` header to reduce trivial blocking

### Usage

```bash
python e_mail_scrapper.py
```

You'll be prompted for input:

```
[+] Enter Target URL To Scan: https://example.com
```

### Example Output

```
[1] Processing https://example.com
[2] Processing https://example.com/contact
[3] Processing https://example.com/about
...

[+] Found emails:
contact@example.com
info@example.com
```

### Notes

- Only follows links within the same domain (`netloc`) as the starting URL.
- Press `Ctrl+C` to stop early — emails found so far will still be printed.
- Respect `robots.txt` and site terms of service; this script does not check them automatically.

---

## Roadmap / Ideas

- [ ] Add `robots.txt` checking to the email scraper
- [ ] Add SSH/FTP-specific banner grabbing to the port scanner
- [ ] Export results to CSV/JSON
- [ ] Add CLI arguments (argparse) instead of interactive `input()` prompts

---

## Disclaimer

This repository is for educational purposes only, created as part of personal cybersecurity learning (TryHackMe, guided coursework). The author is not responsible for any misuse of these tools.
