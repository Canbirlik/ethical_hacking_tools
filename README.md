# Ethical Hacking Tools

A collection of Python scripts built while learning ethical hacking / penetration testing fundamentals — network reconnaissance, OSINT, web scanning, and reverse shell / C2 (Command & Control) basics.

> ⚠️ **Educational Use Only** > These tools are built strictly for learning purposes and for use against systems you own or are explicitly authorized to test (e.g., TryHackMe rooms, personal lab environments, VulnHub VMs, your own virtual network). Scanning, exploiting, or accessing systems without permission is illegal in most jurisdictions. Use responsibly.

## Contents

| Script | Description |
|--------|-------------|
| `port_scanner.py` | Multi-threaded TCP port scanner with service banner grabbing |
| `e_mail_scrapper.py` | Crawls a target website (same-domain links) and extracts email addresses via regex |
| `server.py` | Command & Control (C2) server for a custom backdoor — listens for incoming connections and sends commands |
| `backdoor.py` | Custom backdoor client that connects back to `server.py`, executes system commands, and handles file transfers |

## Requirements
* Python 3.8+
* See `requirements.txt` for package dependencies (mostly standard library only)

### Installation

```bash
git clone https://github.com/Canbirlik/ethical_hacking_tools.git
cd ethical_hacking_tools
pip install -r requirements.txt
```

---

## 🔍 port_scanner.py

A TCP port scanner that:
* Scans one or more targets (comma-separated) in parallel using threads
* Resolves hostnames to IPs
* Grabs service banners via a basic HTTP HEAD request when possible
* Colorizes output for readability

### Usage
```bash
python port_scanner.py
```
You'll be prompted for input:
```text
[*] Enter Targets to Scan (Split them by ,): scanme.nmap.org
[*] Enter How Many Ports You Want to Scan: 1000
```

**Example Output:**
```text
[*] Scanning scanme.nmap.org (45.33.32.156)
[*] Started at 2026-07-03 14:02:11
[+] Port 22 Open
[+] Port 80 Open | HTTP/1.1 200 OK
[*] Scan completed at 2026-07-03 14:02:14
```

**Notes:**
* Uses a 0.5s socket timeout per port to keep scans fast.
* Threads are batched in groups of 100 to avoid overwhelming the system.
* Banner grabbing currently only works reliably against HTTP-speaking services; non-HTTP services (SSH, FTP, etc.) will show as open without a banner.

---

## ✉️ e_mail_scrapper.py

A breadth-first web crawler that:
* Starts from a target URL and follows same-domain links
* Extracts email addresses from each page's HTML via regex
* Stops after visiting 100 pages (configurable in code)
* Sends a browser-like User-Agent header to reduce trivial blocking

### Usage
```bash
python e_mail_scrapper.py
```
You'll be prompted for input:
```text
[+] Enter Target URL To Scan: https://example.com
```

**Example Output:**
```text
[1] Processing https://example.com
[2] Processing https://example.com/contact
[3] Processing https://example.com/about
...
[+] Found emails:
contact@example.com
info@example.com
```

**Notes:**
* Only follows links within the same domain (netloc) as the starting URL.
* Press `Ctrl+C` to stop early — emails found so far will still be printed.
* Respect `robots.txt` and site terms of service; this script does not check them automatically.

---

## 💻 server.py & backdoor.py

A simple, educational Command & Control (C2) setup to understand reverse shell mechanics and client-server communication.
* **`server.py`** — The C2 server that listens for incoming connections, sends commands, and receives output or files.
* **`backdoor.py`** — The client-side agent that connects back to the server, executes commands, and handles file transfers.

### Features
* **Reliable Communication:** Uses JSON serialization over TCP to send and receive data robustly.
* **File Transfer:** Supports both uploading (`upload`) and downloading (`download`) files between server and client.
* **Persistence & Stealth (optional):** Includes logic for automatic reconnection with random jitter to avoid detection patterns.
* **Security Filters:** Blocks dangerous system commands (e.g., `rm -rf /`, `format`) to prevent accidental damage.
* **Cross-Platform:** Works on both Windows and Linux/macOS.

### Setup & Usage

**1. Start the Server (Attacker Machine):**
```bash
python server.py
```

**2. Run the Backdoor (Target Machine):**
```bash
python backdoor.py
```

**3. Interact with the Target via the Server Shell:**
Once the backdoor connects, the server will display a prompt.

**Available commands:**

| Command | Description |
|---------|-------------|
| `dir` / `ls` | List directory contents on the target |
| `cd <path>` | Change current directory on the target |
| `download <file>` | Download a file from the target to the server |
| `upload <file>` | Upload a file to the target from the server |
| `clear` | Clear the server's terminal screen |
| `quit` | Terminate the connection and exit |

**Example Session:**
```bash
# Server side
[+] Listening For Incoming Connections...
[+] Target Connected From: ('192.168.1.100', 49152)

* Shell~192.168.1.100: whoami
[+] user
* Shell~192.168.1.100: cd /tmp
[+] Changed directory to: /tmp
* Shell~192.168.1.100: download secret.txt
[+] File 'secret.txt' downloaded successfully from target
* Shell~192.168.1.100: quit
```

### Code Structure & Improvements
* **Robust Error Handling:** Graceful handling of connection errors, timeouts, and file I/O issues.
* **Secure Command Execution:** Commands are executed with a 30-second timeout and filtered for dangerous patterns.
* **Automatic Reconnection:** The backdoor will retry connecting with a random delay (`20 + random.randint(0, 30)` seconds) for stealth.
* **Cross-Platform `clear`:** Works correctly on both Windows (`cls`) and Unix-like (`clear`) systems.

---

## 🚀 Roadmap / Ideas
* Add `robots.txt` checking to the email scraper.
* Add SSH/FTP-specific banner grabbing to the port scanner.
* Export results to CSV/JSON.
* Add CLI arguments (`argparse`) instead of interactive `input()` prompts.
* Implement encryption (e.g., XOR or AES) for C2 communication.
* Add persistence mechanisms for the backdoor (Registry on Windows, cron jobs on Linux).

---

## ⚖️ Disclaimer
This repository is for educational purposes only, created as part of personal cybersecurity learning (TryHackMe, guided coursework). The author is not responsible for any misuse of these tools.
