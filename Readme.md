# WiFi Network Simulation Documentation

## Completed Table 1: Network Configuration

| Name | MAC Address       | IP Address      | (X,Y) Coordinates | SSID           | Range | Channel |
| ---- | ----------------- | --------------- | ----------------- | -------------- | ----- | ------- |
| AP1  | 02:00:00:00:01:00 | 192.168.1.1/24  | (10, 15)          | cafeteria-wifi | 35    | 35      |
| AP2  | 02:00:00:00:02:00 | 192.168.1.2/24  | (20, 8)           | cafeteria-wifi | 35    | 35      |
| AP3  | 02:00:00:00:03:00 | 192.168.1.3/24  | (30, 22)          | cafeteria-wifi | 35    | 35      |
| AP4  | 02:00:00:00:04:00 | 192.168.1.4/24  | (40, 15)          | cafeteria-wifi | 35    | 35      |
| STA1 | 02:00:00:00:11:00 | 192.168.1.11/24 | (5, 10)           | N/A            | N/A   | N/A     |
| STA2 | 02:00:00:00:12:00 | 192.168.1.12/24 | (15, 25)          | N/A            | N/A   | N/A     |
| STA3 | 02:00:00:00:13:00 | 192.168.1.13/24 | (35, 5)           | N/A            | N/A   | N/A     |

## Completed Table 2: Mobility Configuration

| Name | Start Location | End Location | Start Time - End Time | Moving Speed (min-max) |
| ---- | -------------- | ------------ | --------------------- | ---------------------- |
| STA1 | (5, 10)        | (45, 10)     | 10s-20s               | min_v=1, max_v=5       |
| STA2 | (15, 25)       | (35, 15)     | 30s-60s               | min_v=5, max_v=10      |
| STA3 | (35, 5)        | (15, 20)     | 25s-60s               | min_v=2, max_v=7       |

## Requirements

To run this simulation, you need:

- Linux operating system (Ubuntu 20.04+ recommended)
- Python 3.x
- Mininet and Mininet-WiFi packages

### Installation

To install these libraries, you should run the following commands in your terminal:

```bash
# Update package lists
sudo apt update
```

```bash
# Install Mininet dependencies
sudo apt install -y git make python3-pip
```

```bash
# Install Mininet
git clone https://github.com/mininet/mininet.git
cd mininet
sudo ./util/install.sh -a
```

```bash
# Install Mininet-WiFi
git clone https://github.com/intrig-unicamp/mininet-wifi.git
cd mininet-wifi
sudo util/install.sh -Wlnfv
```

```bash
# Install wmediumd for wireless medium simulation
sudo apt install -y libnl-3-dev libnl-genl-3-dev
git clone https://github.com/bcopeland/wmediumd.git
cd wmediumd
make
sudo make install
```

### To run the simulation, execute the following command in the terminal:

1. Make sure the script has executable permissions:

```bash
sudo chmod +x task1_wifi_network.py
```

2.  Run the script with root privileges:

```bash
sudo python3 task1_wifi_network.py
```

## What the Script Does:

- **Network Creation**: Four access points are created, each with a specific MAC address and position in the network.
- **Mobility Patterns**: Implements specific movement patterns for each station:
  - **STA1**: Moves from (5,10) to (45,10) between 10-20 seconds.
  - **STA2**: Moves from (15,25) to (35,15) between 30-60 seconds.
  - **STA3:**: Moves from (35,5) to (15,20) between 25-60 seconds.
- **Connectivity Testing**: After mobility simulation completes, the script tests connectivity between stations using ping commands.
- **Association Checking**: Determines which access point each station is associated with after movement.

## Interactive Usage

The script is interactive and will prompt you at specific points:

- **Start the simulation**: You will be asked to press Enter to start the simulation.
- **Stop the simulation**: You will be asked to press Enter to stop the simulation.
- **Check connectivity**: You will be asked to press Enter to check the connectivity between stations.

## Commands for Data Collection

**AP Association Commands**

```bash
# Check STA1 association
mininet-wifi> sta1 iw dev sta1-wlan0 link

# Check STA2 association
mininet-wifi> sta2 iw dev sta2-wlan0 link

# Check STA3 association
mininet-wifi> sta3 iw dev sta3-wlan0 link
```

**AP Association Commands**

```bash
# Test inter-station connectivity
mininet-wifi> sta1 ping -c 4 sta2
mininet-wifi> sta1 ping -c 4 sta3
mininet-wifi> sta2 ping -c 4 sta3

# Test AP connectivity
mininet-wifi> sta1 ping -c 4 ap1
mininet-wifi> sta2 ping -c 4 ap2
mininet-wifi> sta3 ping -c 4 ap3
```
