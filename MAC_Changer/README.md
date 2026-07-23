# MAC Changer

This folder contains a simple Python script that changes the MAC address of a network interface using `ifconfig` and `sudo`.

## Purpose

The script validates a new MAC address, brings the target interface down, changes the MAC address, brings it back up, and then verifies whether the change was applied.

## Files

- `cb_mac_changer.py` — Main MAC address changer script.

## Requirements

- Python 3.8+
- `ifconfig` available on the system
- Root privileges via `sudo`

## Usage

Run the script with the interface name and new MAC address:

```bash
cd /home/canbirlik/ethical_hacking_tools/MAC_Changer
sudo /home/canbirlik/ethical_hacking_tools/venv/bin/python3 cb_mac_changer.py -i eth0 -m 00:11:22:33:44:55
```

You can also use the long form:

```bash
sudo /home/canbirlik/ethical_hacking_tools/venv/bin/python3 cb_mac_changer.py --interface eth0 --mac 00:11:22:33:44:55
```

## Example

```text
MAC address for eth0 changed to 00:11:22:33:44:55
MAC address for eth0 is successfully set to 00:11:22:33:44:55
```

## Important Notes

- This script is intended for educational use only.
- Only change MAC addresses on interfaces you own or have explicit authorization to test.
- Use the correct interface name for your system, such as `eth0`, `wlan0`, or another Linux network device.

## Manual MAC Address Change

The following commands are kept here for informational purposes only. They show how the change can be done manually:

```bash
sudo ifconfig eth0 down
sudo ifconfig eth0 hw ether 00:11:22:33:44:55
sudo ifconfig eth0 up
```

### Explanation

- `sudo` runs the command with administrative privileges.
- `ifconfig` is used to configure network interfaces.
- `eth0` is the interface whose MAC address will be changed.
- `down` disables the interface before changing the MAC address.
- `hw ether` specifies the hardware MAC address.
- `00:11:22:33:44:55` is the new MAC address.
- `up` brings the interface back online after the change.

### Verify the change

To confirm the new MAC address:

```bash
ifconfig eth0
```

or:

```bash
ip link show eth0
```

### Note

Replace `eth0` with the correct interface name on your system if needed.
