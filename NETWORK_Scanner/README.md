# Network Scanner

This folder contains a simple ARP-based network scanner built with Scapy.

## Purpose

The script scans a target IP range and lists active devices on the local network by sending an ARP broadcast request and collecting the responses.

## Files

- `cb_nw_scanner.py` — Main scanner script.

## Requirements

- Python 3.8+
- Scapy
- Root privileges via `sudo` because the script sends raw ARP packets

## Installation

From the repository root:

```bash
cd /home/canbirlik/ethical_hacking_tools
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the script with an IP range argument:

```bash
cd /home/canbirlik/ethical_hacking_tools/NETWORK_Scanner
sudo /home/canbirlik/ethical_hacking_tools/venv/bin/python3 cb_nw_scanner.py -r 192.168.1.1/24
```

You can also use the long form:

```bash
sudo /home/canbirlik/ethical_hacking_tools/venv/bin/python3 cb_nw_scanner.py --range 192.168.1.1/24
```

Example output:

```text
IP: 192.168.1.10, MAC: 00:11:22:33:44:55
IP: 192.168.1.15, MAC: aa:bb:cc:dd:ee:ff
```

## Notes

- This script is intended for educational use only.
- Only scan networks you own or have explicit authorization to test.
- On Linux, ARP scanning requires elevated privileges.
- The current version uses command-line arguments instead of interactive input.

## Troubleshooting

If you see `ModuleNotFoundError: No module named 'scapy'`, make sure you are using the project virtual environment Python:

```bash
/home/canbirlik/ethical_hacking_tools/venv/bin/python3 cb_nw_scanner.py -r 192.168.1.1/24
```

If you see a permissions error, run the command again with `sudo`.
