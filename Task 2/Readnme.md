# Task 2 : Ad-Hoc Emergency Network

This implementation creates an emergency response ad-hoc network using Mininet-WiFi with three strategically positioned nodes in a triangular formation. The network uses the OLSR routing protocol to establish reliable multi-hop communication for emergency services.

## Completed Table 2: Ad-Hoc Network Configuration

| Name   | MAC Address       | IP Address     | Position | Range | Antenna Height | Antenna Gain | Protocol | SSID    | HT_CAP |
| ------ | ----------------- | -------------- | -------- | ----- | -------------- | ------------ | -------- | ------- | ------ |
| adhoc1 | 02:00:00:00:21:00 | 192.168.2.1/24 | (60, 10) | 30    | 1              | 5            | olsrd    | adhocUH | HT40+  |
| adhoc2 | 02:00:00:00:22:00 | 192.168.2.2/24 | (75, 25) | 30    | 2              | 6            | olsrd    | adhocUH | HT40+  |
| adhoc3 | 02:00:00:00:23:00 | 192.168.2.3/24 | (90, 15) | 30    | 3              | 7            | olsrd    | adhocUH | HT40+  |

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

# Network Design Rationale

### Positioning Strategy

Strategic Triangle Formation: Nodes are arranged in a triangle to provide redundant communication paths
Range Overlap: Each node's 30-meter range ensures connectivity with at least one other node
Variable Antenna Heights: Heights (1m, 2m, 3m) optimize coverage in 3D space
Progressive Antenna Gain: Increasing gains (5-7 dBi) compensate for distance between nodes

### OLSR Protocol Selection

Proactive Routing: Continuously maintains routes for immediate communication
Fast Convergence: Critical for emergency scenarios where delays are unacceptable
Multi-hop Support: Enables communication beyond direct radio range
Low Overhead: Optimized control messages reduce network congestion

# Implementation Details

The implementation uses the following key components:

### Network Creation

```python
def create_adhoc_network():
    """Create Ad-Hoc network for emergency response units"""

    # Create Mininet-WiFi network with ad-hoc support
    net = Mininet_wifi(
        link=wmediumd,
        wmediumd_mode=interference
    )

    # Add emergency response stations with ad-hoc configuration
    adhoc1 = net.addStation('adhoc1',
                           ip='192.168.2.1/24',
                           mac='02:00:00:00:21:00',
                           position='60,10,1',
                           range=30,
                           antennaGain=5)
    # [Additional stations omitted for brevity]

    # Configure propagation model for outdoor emergency scenario
    net.setPropagationModel(model="logDistance", exp=2.5)
```

### OLSR Configuration

The configure_olsr function sets up OLSR with optimized parameters:

```python
# OLSR configuration highlights
Interface "{interface}"
{
    HelloInterval 2.0       # Fast neighbor discovery
    HelloValidityTime 20.0  # Reliable neighbor state
    TcInterval 5.0          # Efficient topology control
    TcValidityTime 30.0     # Route stability
    MidInterval 5.0         # Multi-interface declaration
    MidValidityTime 30.0    # Interface validity period
}
```

### Testing Methodology

The implementation includes rigorous testing:

ICMP Connectivity Tests: Between all node pairs to verify routing
TCP Transfer Test: 120-second iperf3 throughput measurement
Traffic Capture: Full packet capture using tcpdump for analysis
Routing Table Verification: Confirms OLSR route establishment

# Performance Evaluation

### ICMP Test Results

The test_icmp_connectivity function tests ping connectivity:

ADHOC1 to ADHOC2 ping results:

- Direct connection with low latency (~10-15ms)
- 0% packet loss expected

ADHOC2 to ADHOC3 ping results:

- Direct connection with low latency (~10-15ms)
- 0% packet loss expected

ADHOC1 to ADHOC3 ping results:

- Multi-hop connection via OLSR
- Slightly higher latency (~20-30ms)
- Potential for minimal packet loss (0-5%)

### TCP Performance Analysis

The TCP transfer test uses iperf3 for precise throughput measurement:

```python
def analyze_tcp_results(iperf_result):
    """Analyze TCP transfer results and extract throughput"""

    # Extract key metrics
    sent_mbps = sent_bps / 1000000
    received_mbps = received_bps / 1000000
    success_rate = (received_bytes / sent_bytes) * 100
```

Expected performance metrics:

Throughput: 10-20 Mbps depending on node distance
Success Rate: 85-95% packet delivery
Stability: Minimal fluctuations after OLSR convergence

### Wireshark Analysis

The traffic capture provides insights into:

Protocol Distribution: TCP data vs. OLSR control traffic
Routing Behavior: OLSR hello packets and route advertisements
Retransmissions: Indicators of link quality
Throughput Graph: Visual representation of performance over time

# V2V/V2X Protocol Analysis

### OLSR for V2V/V2X Applications

Advantages:

Proactive routing reduces delay for safety-critical messages
Multi-hop capabilities extend communication range
Optimized control traffic minimizes overhead
Fast convergence adapts to changing vehicle positions

Limitations:

Higher memory requirements than reactive protocols
Continuous updates consume bandwidth
Less suitable for extremely high mobility (highway speeds)

## Alternative V2V Protocols

### AODV (Ad-hoc On-Demand Distance Vector)

Advantage: Lower overhead in sparse networks
Limitation: Route discovery delay unsuitable for safety applications

### GPSR (Greedy Perimeter Stateless Routing)

Advantage: Location-aware routing ideal for vehicles with GPS
Limitation: Requires accurate positioning information

### IEEE 802.11p/DSRC

Advantage: Specifically designed for vehicular communications
Limitation: Limited range compared to cellular V2X

## Recommended Protocol Selection

For emergency vehicle networks like the one implemented:

OLSR: Best for dense urban environments with moderate mobility
GPSR: Preferable for highway scenarios with GPS availability
Hybrid approach: Optimal for comprehensive V2V/V2X deployment

# Conclusion

The implemented ad-hoc emergency network demonstrates a practical application of OLSR for emergency services communication. The design prioritizes reliability, redundancy, and appropriate coverage through strategic node placement and antenna configuration.
