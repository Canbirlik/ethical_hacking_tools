import socket
import termcolor
import threading
from datetime import datetime

def get_banner(sock):
    # Try to grab service banner by sending HTTP HEAD request
    try:
        sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
        banner = sock.recv(1024).decode().strip().split('\n')[0]
        return banner
    except:
        return ''

def scan_port(ipaddress, port):
    # Try to connect to the port, print if open
    try:
        sock = socket.socket()
        sock.settimeout(0.5)  # 0.5s timeout to avoid long waits
        sock.connect((ipaddress, port))
        banner = get_banner(sock)
        if banner:
            print(termcolor.colored(f"[+] Port {port} Open | {banner}", 'green'))
        else:
            print(termcolor.colored(f"[+] Port {port} Open", 'green'))
        sock.close()
    except:
        pass  # Port is closed or filtered, skip silently

def scan(target, ports):
    # Resolve hostname to IP address
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(termcolor.colored(f"[-] Could not resolve {target}", 'red'))
        return

    print(termcolor.colored(f"\n[*] Scanning {target} ({ip})", 'blue'))
    print(termcolor.colored(f"[*] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'blue'))
    print("-" * 50)

    threads = []
    for port in range(1, ports + 1):
        # Create a thread for each port to scan in parallel
        t = threading.Thread(target=scan_port, args=(ip, port))
        threads.append(t)
        t.start()

        # Wait for every 100 threads to avoid overwhelming the system
        if len(threads) % 100 == 0:
            for t in threads:
                t.join()
            threads = []

    # Wait for remaining threads to finish
    for t in threads:
        t.join()

    print("-" * 50)
    print(termcolor.colored(f"[*] Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'blue'))

# Main program — accept single or multiple comma-separated targets
targets = input("[*] Enter Targets to Scan (Split them by ,): ")
ports = int(input("[*] Enter How Many Ports You Want to Scan: "))

if ',' in targets:
    print(termcolor.colored("[*] Scanning Multiple Targets", 'yellow'))
    for ip_addr in targets.split(','):
        scan(ip_addr.strip(), ports)
else:
    scan(targets, ports)
