from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP, Station
from mn_wifi.cli import CLI_wifi
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.wmediumdConnector import interference
from mininet.link import Link
import time
import threading

def create_network():
    """Create and configure the WiFi network topology"""
    
    # Set log level
    setLogLevel('info')
    
    # Create Mininet-WiFi network with interference support
    net = Mininet_wifi(
        controller=Controller,
        link=wmediumd,
        wmediumd_mode=interference,
        noise_th=-70,  
        fading_cof=3  
    )
    
    info("*** Creating network components\n")
    
    # Add controller
    net.addController('c0')
    

    # By positions strategically placed to create dead spot at (25, 15)
    ap1 = net.addAccessPoint('ap1', 
                            ssid='cafeteria-wifi',
                            mode='g',
                            channel='35',
                            position='10,15,0',
                            range=35,
                            mac='02:00:00:00:01:00',
                            ip='192.168.1.1/24')
    
    ap2 = net.addAccessPoint('ap2',
                            ssid='cafeteria-wifi', 
                            mode='g',
                            channel='35',
                            position='20,8,0',
                            range=35,
                            mac='02:00:00:00:02:00',
                            ip='192.168.1.2/24')
    
    ap3 = net.addAccessPoint('ap3',
                            ssid='cafeteria-wifi',
                            mode='g', 
                            channel='35',
                            position='30,22,0',
                            range=35,
                            mac='02:00:00:00:03:00',
                            ip='192.168.1.3/24')
    
    ap4 = net.addAccessPoint('ap4',
                            ssid='cafeteria-wifi',
                            mode='g',
                            channel='35', 
                            position='40,15,0',
                            range=35,
                            mac='02:00:00:00:04:00',
                            ip='192.168.1.4/24')
    
    # Add mobile stations at initial positions
    sta1 = net.addStation('sta1',
                         position='5,10,0',
                         mac='02:00:00:00:11:00',
                         ip='192.168.1.11/24')
    
    sta2 = net.addStation('sta2', 
                         position='15,25,0',
                         mac='02:00:00:00:12:00',
                         ip='192.168.1.12/24')
    
    sta3 = net.addStation('sta3',
                         position='35,5,0', 
                         mac='02:00:00:00:13:00',
                         ip='192.168.1.13/24')
    
    # Configure propagation model for realistic wireless behavior
    net.setPropagationModel(model="logDistance", exp=3)
    
    info("*** Configuring WiFi nodes\n")
    net.configureWifiNodes()
    
    # Create linear topology: AP1 - AP2 - AP3 - AP4
    # Physical links between APs for backhaul connectivity
    info("*** Creating linear topology links\n")
    net.addLink(ap1, ap2, cls=Link)
    net.addLink(ap2, ap3, cls=Link) 
    net.addLink(ap3, ap4, cls=Link)
    
    # Plot network topology for visualization
    net.plotGraph(max_x=50, max_y=30)
    
    
    info("*** Starting network\n") # Start network
    net.build()
    net.start()
    
    return net

def implement_mobility(net):
    """Implement station mobility according to specifications"""
    
    info("*** Starting mobility simulation\n")
    
    # Get station objects
    sta1 = net.get('sta1')
    sta2 = net.get('sta2') 
    sta3 = net.get('sta3')
    
    def sta1_mobility():
        """STA1: (5,10) to (45,10) from 10s-20s, speed 1-5"""
        time.sleep(10)  # Timestamp until 10s
        info("*** STA1 starting mobility\n")
        # Move from (5,10) to (45,10) over 10 seconds
        for t in range(10):
            x_pos = 5 + (40 * t / 10)  
            sta1.setPosition(f'{x_pos},10,0')
            time.sleep(1)
        info("*** STA1 mobility completed\n")
    
    def sta2_mobility():
        """STA2: (15,25) to (35,15) from 30s-60s, speed 5-10"""
        time.sleep(30)  # Wait until 30s
        info("*** STA2 starting mobility\n")
        # Move from (15,25) to (35,15) over 30 seconds
        for t in range(30):
            x_pos = 15 + (20 * t / 30)  
            y_pos = 25 - (10 * t / 30)  
            sta2.setPosition(f'{x_pos},{y_pos},0')
            time.sleep(1)
        info("*** STA2 mobility completed\n")
    
    def sta3_mobility():
        """STA3: (35,5) to (15,20) from 25s-60s, speed 2-7"""
        time.sleep(25)  # Timestamp until 25s
        info("*** STA3 starting mobility\n")
        # Move from (35,5) to (15,20) over 35 seconds
        for t in range(35):
            x_pos = 35 - (20 * t / 35)  
            y_pos = 5 + (15 * t / 35)   
            sta3.setPosition(f'{x_pos},{y_pos},0')
            time.sleep(1)
        info("*** STA3 mobility completed\n")
    
    # Start mobility threads
    threading.Thread(target=sta1_mobility, daemon=True).start()
    threading.Thread(target=sta2_mobility, daemon=True).start() 
    threading.Thread(target=sta3_mobility, daemon=True).start()

def run_connectivity_tests(net):
    """Execute ping tests between stations"""
    
    info("*** Running connectivity tests\n")
    
    # Wait for mobility to complete
    time.sleep(65)
    
    # Get stations
    sta1 = net.get('sta1')
    sta2 = net.get('sta2')
    sta3 = net.get('sta3')
    
    # Test connectivity between stations
    info("*** Testing STA1 -> STA2 connectivity\n")
    result1 = sta1.cmd('ping -c 4 192.168.1.12')
    print("STA1 to STA2 ping result:")
    print(result1)
    
    info("*** Testing STA1 -> STA3 connectivity\n") 
    result2 = sta1.cmd('ping -c 4 192.168.1.13')
    print("STA1 to STA3 ping result:")
    print(result2)
    
    info("*** Testing STA2 -> STA3 connectivity\n")
    result3 = sta2.cmd('ping -c 4 192.168.1.13')
    print("STA2 to STA3 ping result:")
    print(result3)
    
    return result1, result2, result3

def check_ap_associations(net):
    """Check which AP each station is associated with"""
    
    info("*** Checking AP associations\n")
    
    stations = ['sta1', 'sta2', 'sta3']
    associations = {}
    
    for sta_name in stations:
        sta = net.get(sta_name)
        # Check wireless interface link status
        result = sta.cmd('iw dev ' + sta_name + '-wlan0 link')
        associations[sta_name] = result
        print(f"{sta_name} association:")
        print(result)
        print("-" * 50)
    
    return associations

def main():
    """Main function to orchestrate the network emulation"""
    
    try:
        # Create network
        net = create_network()
        
        print("Network created successfully!")
        print("Initial network state - take screenshot now")
        input("Press Enter to start mobility simulation...")
        
        # Start mobility simulation
        implement_mobility(net)
        
        # Wait for mobility to complete and take final screenshot
        print("Mobility in progress... Wait 65 seconds for completion")
        time.sleep(65)
        
        print("Mobility completed - take final screenshot now")
        input("Press Enter to check AP associations...")
        
        # Check AP associations
        associations = check_ap_associations(net)
        
        input("Press Enter to run connectivity tests...")
        
        # Run connectivity tests  
        ping_results = run_connectivity_tests(net)
        
        print("\n*** Network emulation completed successfully! ***")
        print("All required data has been collected.")
        print("You can now take screenshots and collect results.")
        
        # Start CLI for manual testing if needed
        info("*** Starting CLI for manual testing\n")
        CLI_wifi(net)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        
    finally:
        # Clean up
        if 'net' in locals():
            info("*** Stopping network\n")
            net.stop()
            
  # Run the main function
if __name__ == '__main__':
    main()