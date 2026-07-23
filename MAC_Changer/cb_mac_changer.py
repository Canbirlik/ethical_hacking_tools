import re
import subprocess
import optparse

# subprocess.call(["ifconfig", "eth0", "down"])
# subprocess.call(["ifconfig", "eth0", "hw", "ether", "00:11:22:33:44:55"])
# subprocess.call(["ifconfig", "eth0", "up"])
    
def is_valid_mac_address(mac_address):
    """
    Validate that the supplied MAC address has the expected format.

    Expected format: XX:XX:XX:XX:XX:XX
    """
    return bool(re.fullmatch(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", mac_address))


def change_mac(interface, new_mac):
    """
    Change the MAC address of a network interface.

    :param interface: The name of the network interface (e.g., 'eth0', 'wlan0').
    :param new_mac: The new MAC address to assign to the interface.
    """
    if not is_valid_mac_address(new_mac):
        print(f"Invalid MAC address format: {new_mac}. Expected format: XX:XX:XX:XX:XX:XX")
        return

    try:
        # Bring the interface down
        subprocess.run(["sudo", "ifconfig", interface, "down"], check=True)

        # Change the MAC address
        subprocess.run(["sudo", "ifconfig", interface, "hw", "ether", new_mac], check=True)

        # Bring the interface back up
        subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)

        print(f"MAC address for {interface} changed to {new_mac}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to change MAC address: {e}")

def get_user_input():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Network interface to change MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address")

    (options, arguments) = parser.parse_args()

    if not options.interface or not options.new_mac:
            parser.error("Please provide both interface and new MAC address")

    return options.interface, options.new_mac

def control_new_mac(interface, new_mac):
    existing_mac = subprocess.check_output(["ifconfig", interface]).decode("utf-8")
    if new_mac in existing_mac:
        print(f"MAC address for {interface} is successfully set to {new_mac}")
    else:
        print(f"Change MAC address is failed for {interface} to {new_mac}")

def main():

    #interface = input("Enter the network interface (e.g., eth0, wlan0): ")
    #new_mac = input("Enter the new MAC address (format: XX:XX:XX:XX:XX:XX): ")
      
    interface, new_mac = get_user_input()

    change_mac(interface, new_mac)

    control_new_mac(interface, new_mac)

if __name__ == "__main__":
    main()