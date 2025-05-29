from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station
from mn_wifi.cli import CLI_wifi
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.wmediumdConnector import interference
import time
import threading
import subprocess
import os

def create_adhoc_network():
    """Create Ad-Hoc network for emergency response units"""
    
    setLogLevel('info')
    
    # Create Mininet-WiFi network with ad-hoc support
    net = Mininet_wifi(
        link=wmediumd,
        wmediumd_mode=interference
    )
    
    info("*** Creating Ad-Hoc Emergency Network\n")
    
    # Add emergency response stations with ad-hoc configuration
    adhoc1 = net.addStation('adhoc1',
                           ip='192.168.2.1/24',
                           mac='02:00:00:00:21:00',
                           position='60,10,1',  # x,y,antenna_height
                           range=30,
                           antennaGain=5)
    
    adhoc2 = net.addStation('adhoc2', 
                           ip='192.168.2.2/24',
                           mac='02:00:00:00:22:00',
                           position='75,25,2',  # x,y,antenna_height
                           range=30,
                           antennaGain=6)
    
    adhoc3 = net.addStation('adhoc3',
                           ip='192.168.2.3/24', 
                           mac='02:00:00:00:23:00',
                           position='90,15,3',  # x,y,antenna_height
                           range=30,
                           antennaGain=7)
    
    # Configure propagation model for outdoor emergency scenario
    net.setPropagationModel(model="logDistance", exp=2.5)
    
    info("*** Configuring Ad-Hoc nodes\n")
    net.configureWifiNodes()
    
    # Create ad-hoc links between stations
    info("*** Creating Ad-Hoc mesh topology\n")
    net.addLink(adhoc1, adhoc2, cls=adhoc, 
                ssid='adhocUH', 
                mode='g',
                channel=6,
                ht_cap='HT40+')
    
    net.addLink(adhoc1, adhoc3, cls=adhoc,
                ssid='adhocUH',
                mode='g', 
                channel=6,
                ht_cap='HT40+')
    
    net.addLink(adhoc2, adhoc3, cls=adhoc,
                ssid='adhocUH',
                mode='g',
                channel=6, 
                ht_cap='HT40+')
    
    # Plot network for visualization 
    net.plotGraph(max_x=100, max_y=40)
    
    # Build and start network
    info("*** Starting Ad-Hoc network\n")
    net.build()
    net.start()
    
    return net

def configure_olsr(net):
    """Configure OLSR routing protocol on all ad-hoc nodes"""
    
    info("*** Configuring OLSR routing protocol\n")
    
    # OLSR configuration template
    olsr_config = """
# OLSR configuration for emergency ad-hoc network
DebugLevel 2
IpVersion 4
AllowNoInt yes
TosValue 16
RtProto 0
RtTable 254
RtTableDefault 0
Willingness 7
IpcConnect
{
    MaxConnections 2
    Host 127.0.0.1
    Net 0.0.0.0 0.0.0.0
}
LoadPlugin "olsrd_arprefresh.so.0.1"
LoadPlugin "olsrd_dyn_gw.so.0.5"
LoadPlugin "olsrd_txtinfo.so.1.1"
{
    PlParam "port" "2006"
    PlParam "Accept" "127.0.0.1"
}

Interface "{interface}"
{
    HelloInterval 2.0
    HelloValidityTime 20.0
    TcInterval 5.0
    TcValidityTime 30.0
    MidInterval 5.0 
    MidValidityTime 30.0
}
"""
    
    stations = ['adhoc1', 'adhoc2', 'adhoc3']
    
    for station_name in stations:
        station = net.get(station_name)
        interface = f"{station_name}-wlan0"
        
        # Create OLSR config file for this station
        config_content = olsr_config.format(interface=interface)
        config_file = f"/tmp/olsrd_{station_name}.conf"
        
        # Write config file
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Start OLSR daemon
        info(f"*** Starting OLSR on {station_name}\n")
        olsr_cmd = f"olsrd -f {config_file} -d 1 &"
        station.cmd(olsr_cmd)
        
        # Wait for OLSR to initialize
        time.sleep(2)
    
    # Allow OLSR convergence time
    info("*** Waiting for OLSR convergence\n")
    time.sleep(10)

def test_icmp_connectivity(net):
    """Test ICMP connectivity between closest ad-hoc stations"""
    
    info("*** Testing ICMP connectivity between stations\n")
    
    # Get stations
    adhoc1 = net.get('adhoc1')
    adhoc2 = net.get('adhoc2') 
    adhoc3 = net.get('adhoc3')
    
    results = {}
    
    # Test adhoc1 to adhoc2 
    info("*** Testing adhoc1 -> adhoc2 connectivity\n")
    result1 = adhoc1.cmd('ping -c 5 192.168.2.2')
    results['adhoc1_to_adhoc2'] = result1
    print("ADHOC1 to ADHOC2 ping result:")
    print(result1)
    print("-" * 60)
    
    # Test adhoc2 to adhoc3  
    info("*** Testing adhoc2 -> adhoc3 connectivity\n")
    result2 = adhoc2.cmd('ping -c 5 192.168.2.3')
    results['adhoc2_to_adhoc3'] = result2
    print("ADHOC2 to ADHOC3 ping result:")
    print(result2)
    print("-" * 60)
    
    # Test adhoc1 to adhoc3 
    info("*** Testing adhoc1 -> adhoc3 connectivity\n") 
    result3 = adhoc1.cmd('ping -c 5 192.168.2.3')
    results['adhoc1_to_adhoc3'] = result3
    print("ADHOC1 to ADHOC3 ping result:")
    print(result3)
    print("-" * 60)
    
    return results

def setup_tcp_transfer(net):
    """Setup TCP transfer test with iperf3"""
    
    info("*** Setting up TCP transfer test\n")
    
    # Get stations
    adhoc1 = net.get('adhoc1')
    adhoc2 = net.get('adhoc2')
    
    # Start iperf3 server on adhoc2
    info("*** Starting iperf3 server on adhoc2\n")
    server_cmd = "iperf3 -s -p 5001 -D"  # -D for daemon mode
    adhoc2.cmd(server_cmd)
    
    # Wait for server to start
    time.sleep(2)
    
    return adhoc1, adhoc2

def run_tcp_transfer(client_station, server_ip, duration=120):
    """Run TCP transfer test for specified duration"""
    
    info(f"*** Running TCP transfer for {duration} seconds\n")
    
    # Run iperf3 client for 120 seconds with JSON output
    client_cmd = f"iperf3 -c {server_ip} -p 5001 -t {duration} -J"
    result = client_station.cmd(client_cmd)
    
    return result

def analyze_tcp_results(iperf_result):
    """Analyze TCP transfer results and extract throughput"""
    
    import json
    
    try:
        # Parse JSON output from iperf3
        data = json.loads(iperf_result)
        
        # Extract throughput information
        sent_bps = data['end']['sum_sent']['bits_per_second']
        received_bps = data['end']['sum_received']['bits_per_second']
        
        # Convert to Mbps
        sent_mbps = sent_bps / 1000000
        received_mbps = received_bps / 1000000
        
        # Calculate success rate
        sent_bytes = data['end']['sum_sent']['bytes']
        received_bytes = data['end']['sum_received']['bytes']  
        success_rate = (received_bytes / sent_bytes) * 100 if sent_bytes > 0 else 0
        
        results = {
            'sent_mbps': sent_mbps,
            'received_mbps': received_mbps,
            'success_rate': success_rate,
            'duration': data['end']['sum_sent']['seconds']
        }
        
        return results
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing iperf3 results: {e}")
        return None

def check_routing_tables(net):
    """Check OLSR routing tables on all stations"""
    
    info("*** Checking OLSR routing tables\n")
    
    stations = ['adhoc1', 'adhoc2', 'adhoc3']
    routing_info = {}
    
    for station_name in stations:
        station = net.get(station_name)
        
        # Check routing table
        route_result = station.cmd('route -n')
        
        # Check OLSR-specific routes
        olsr_result = station.cmd('echo "/routes" | nc 127.0.0.1 2006 2>/dev/null || echo "OLSR info not available"')
        
        routing_info[station_name] = {
            'routing_table': route_result,
            'olsr_routes': olsr_result
        }
        
        print(f"\n{station_name.upper()} Routing Information:")
        print("System Routing Table:")
        print(route_result)
        print("OLSR Routes:")
        print(olsr_result)
        print("-" * 80)
    
    return routing_info

def capture_network_traffic(interface, duration=130, filename="adhoc_traffic.pcap"):
    """Capture network traffic using tcpdump for Wireshark analysis"""
    
    info(f"*** Starting traffic capture on {interface}\n")
    
    # Start tcpdump in background
    capture_cmd = f"tcpdump -i {interface} -w {filename} &"
    subprocess.Popen(capture_cmd, shell=True)
    
    return filename

def main():
    """Main function for Task 2 Ad-Hoc network implementation"""
    
    try:
        # Create ad-hoc network
        net = create_adhoc_network()
        
        print("Ad-Hoc network created successfully!")
        input("Press Enter to configure OLSR routing...")
        
        # Configure OLSR protocol
        configure_olsr(net)
        
        print("OLSR configured and converged!")
        input("Press Enter to test ICMP connectivity...")
        
        # Test ICMP connectivity
        icmp_results = test_icmp_connectivity(net)
        
        input("Press Enter to setup TCP transfer...")
        
        # Setup TCP transfer
        client, server = setup_tcp_transfer(net)
        server_ip = "192.168.2.2"
        
        # Start traffic capture for Wireshark analysis
        capture_file = capture_network_traffic("adhoc1-wlan0")
        
        print("Starting 120-second TCP transfer...")
        print("Traffic capture started - this will be used for Wireshark analysis")
        
        # Run TCP transfer for 120 seconds
        tcp_result = run_tcp_transfer(client, server_ip, 120)
        
        # Stop traffic capture
        subprocess.run("pkill tcpdump", shell=True)
        
        print(f"TCP transfer completed!")
        print(f"Traffic capture saved to: {capture_file}")
        
        # Analyze TCP results
        tcp_analysis = analyze_tcp_results(tcp_result)
        if tcp_analysis:
            print("\nTCP Transfer Results:")
            print(f"Sent: {tcp_analysis['sent_mbps']:.2f} Mbps")
            print(f"Received: {tcp_analysis['received_mbps']:.2f} Mbps") 
            print(f"Success Rate: {tcp_analysis['success_rate']:.2f}%")
        
        input("Press Enter to check routing tables...")
        
        # Check routing information
        routing_info = check_routing_tables(net)
        
        print("\n*** Task 2 Implementation Completed Successfully! ***")
        print("\nDeliverables collected:")
        print("✓ ICMP connectivity test results")
        print("✓ TCP transfer performance data")  
        print(f"✓ Network traffic capture: {capture_file}")
        print("✓ OLSR routing table information")
        
        # Start CLI for additional testing
        print("\nStarting CLI for additional manual testing...")
        CLI_wifi(net)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if 'net' in locals():
            info("*** Stopping network\n")
            # Kill OLSR processes
            subprocess.run("pkill olsrd", shell=True)
            net.stop()

if __name__ == '__main__':
    main()