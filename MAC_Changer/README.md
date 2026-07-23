# Manual MAC Address Change

Use the following commands to manually change the MAC address of the `eth0` interface:

```bash
sudo ifconfig eth0 down
sudo ifconfig eth0 hw ether 00:11:22:33:44:55
sudo ifconfig eth0 up
```

## Explanation

- `sudo` runs the command with administrative privileges.
- `ifconfig` is used to configure network interfaces.
- `eth0` is the interface whose MAC address will be changed.
- `down` disables the interface before changing the MAC address.
- `hw ether` specifies the hardware MAC address.
- `00:11:22:33:44:55` is the new MAC address.
- `up` brings the interface back online after the change.

## Verify the change

To confirm the new MAC address:

```bash
ifconfig eth0
```

or:

```bash
ip link show eth0
```

## Note

Replace `eth0` with the correct interface name on your system if needed.
