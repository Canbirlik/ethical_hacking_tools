import os
import sys

import scapy.all as scapy
import optparse

def get_user_input():
    parser = optparse.OptionParser()
    parser.add_option("-r", "--range", dest="ip_range", help="IP range to scan (e.g., 192.168.1.1/24)")
    (options, arguments) = parser.parse_args()
    if not options.ip_range:
        parser.error("Please provide the IP range to scan")
    return options.ip_range

def scan_network(ip_range):
    """
    Scan the network for active devices within the specified IP range.

    :param ip_range: The IP range to scan (e.g., '192.168.1.1/24')
    :return: A list of active devices found within the IP range.
    """
    try:
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list, _ = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)
        answered_list.summary() #Can be removed if not needed for debugging
        active_devices = []
        for _, response in answered_list:
            active_devices.append({"ip": response.psrc, "mac": response.hwsrc})

        return active_devices
    except PermissionError as exc:
        if os.geteuid() != 0:
            raise PermissionError(
                "This tool needs root privileges to send raw ARP packets. "
                "Run it with sudo: sudo python3 cb_nw_scanner.py"
            ) from exc
        raise


def main():
    # ip_range = input("Enter the IP range to scan (e.g., 192.168.1.1/24): ")

    ip_range = get_user_input()

    try:
        active_devices = scan_network(ip_range)
    except PermissionError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    for device in active_devices:
        print(f"IP: {device['ip']}, MAC: {device['mac']}")


if __name__ == "__main__":
    main()