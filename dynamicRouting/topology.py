import sys
sys.path.append('../')
from p4_mininet import P4Switch, P4Host
from mininet.node import Controller, RemoteController
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import argparse

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable', type=str, action="store", required=True)
parser.add_argument('--json', help='Path to JSON config file', type=str, action="store", required=True)
args = parser.parse_args()


class DemoTopo(Topo):
    "Demo topology"

    def __init__(self, sw_path, json_path, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        s1 = self.addSwitch('s1',
                            sw_path=sw_path,
                            json_path=json_path,
                            thrift_port=9091)
        s2 = self.addSwitch('s2',
                            sw_path=sw_path,
                            json_path=json_path,
                            thrift_port=9092)
        s3 = self.addSwitch('s3',
                            sw_path=sw_path,
                            json_path=json_path,
                            thrift_port=9093)
        s4 = self.addSwitch('s4',
                            sw_path=sw_path,
                            json_path=json_path,
                            thrift_port=9094)
        s5 = self.addSwitch('s5',
                            sw_path=sw_path,
                            json_path=json_path,
                            thrift_port=9095)

        h1 = self.addHost('h1',
                            ip="192.168.1.2/24",
                            mac='00:00:00:00:00:01')
        h2 = self.addHost('h2',
                            ip="192.168.2.2/24",
                            mac='00:00:00:00:00:02')
        h5 = self.addHost('h5',
                            ip="192.168.5.2/24",
                            mac='00:00:00:00:00:05')

        self.addLink(s1, h1, port1 = 0, port2 = 0)
        self.addLink(s1, s2, port1 = 1, port2 = 1)
        self.addLink(s1, s3, port1 = 2, port2 = 0)

        self.addLink(s2, h2, port1 = 0, port2 = 0)
        self.addLink(s2, s4, port1 = 2, port2 = 0)
        self.addLink(s2, s5, port1 = 3, port2 = 1)

        self.addLink(s3, s4, port1 = 1, port2 = 1)
        self.addLink(s3, s5, port1 = 2, port2 = 2)
        
        self.addLink(s4, s5, port1 = 2, port2 = 3)
        
        self.addLink(s5, h5, port1 = 0, port2 = 0)


def main():
    topo = DemoTopo(args.behavioral_exe,
                            args.json)

    net = Mininet(topo=topo,
                  host=P4Host,
                  switch=P4Switch,
                  controller=None)
    # creating new controllers with specified ip addr [not sure if port is needed]
    c1 = Controller('c1', ip = '192.168.101.1/24', mac= '00:00:00:01:00:00', port = 6631)
    c2 = Controller('c2', ip = "192.168.102.1/24", mac= '00:00:00:02:00:00', port = 6632)
    c3 = Controller('c3', ip = "192.168.103.1/24", mac= '00:00:00:03:00:00', port = 6633)
    c4 = Controller('c4', ip = "192.168.104.1/24", mac= '00:00:00:04:00:00', port = 6634)
    c5 = Controller('c5', ip = "192.168.105.1/24", mac= '00:00:00:05:00:00', port = 6635)

    #add newly created controlers to net (Mininet object, not Topo(!))
    for c in [c1, c2, c3, c4, c5]:
        net.addController(c)
        c.start()

    #...
    s1 = net.get('s1')
    s2 = net.get('s2')
    s3 = net.get('s3')
    s4 = net.get('s4')
    s5 = net.get('s5')

    #Links between controlers and switches
    net.addLink(s1, c1, port1 = 4)
    net.addLink(s2, c2, port1 = 4)
    net.addLink(s3, c3, port1 = 4)
    net.addLink(s4, c4, port1 = 4)
    net.addLink(s5, c5, port1 = 4)

    #start switches with controllers
    s1.start([c1])
    s2.start([c2])
    s3.start([c3])
    s4.start([c4])
    s5.start([c5])

    #net.start()
    
    
#switch 1 configuration
    s1.setIP('192.168.1.1/24', intf = 's1-eth0')
    s1.setMAC('00:00:00:00:01:00', intf = 's1-eth0')
    s1.setIP('192.168.11.1/24', intf = 's1-eth1')
    s1.setMAC('00:00:00:00:01:01', intf='s1-eth1')
    s1.setIP('192.168.12.1/24', intf = 's1-eth2')
    s1.setMAC('00:00:00:00:01:02', intf='s1-eth2')
    #in/out ospf packets interface
    s1.setIP('192.168.101.2/24', intf = 's1-eth4')
    s1.setMAC('00:00:00:00:01:4', intf = 's1-eth4')

#switch 2 configuration
    s2.setIP('192.168.2.1/24', intf = 's2-eth0')
    s2.setMAC('00:00:00:00:02:00', intf='s2-eth0')
    s2.setIP('192.168.11.2/24', intf = 's2-eth1')
    s2.setMAC('00:00:00:00:02:01', intf='s2-eth1')
    s2.setIP('192.168.13.2/24', intf = 's2-eth2')
    s2.setMAC('00:00:00:00:02:02', intf='s2-eth2')
    s2.setIP('192.168.14.1/24', intf = 's2-eth3')
    s2.setMAC('00:00:00:00:02:03', intf='s2-eth3')
    #in/out ospf packets interface
    s2.setIP('192.168.102.2/24', intf = 's2-eth4')
    s2.setMAC('00:00:00:00:02:4', intf = 's2-eth4')

#switch 3 configuration
    s3.setIP('192.168.12.2/24', intf='s3-eth0')
    s3.setMAC('00:00:00:00:03:00', intf='s3-eth0')
    s3.setIP('192.168.15.1/24', intf='s3-eth1')
    s3.setMAC('00:00:00:00:03:01', intf='s3-eth1')
    s3.setIP('192.168.16.1/24', intf='s3-eth2')
    s3.setMAC('00:00:00:00:03:02', intf='s3-eth2')
    #in/out ospf packets interface
    s3.setIP('192.168.103.2/24', intf = 's3-eth4')
    s3.setMAC('00:00:00:00:03:4', intf = 's3-eth4') 

#switch 4 configuration
    s4.setIP('192.168.13.1/24', intf='s4-eth0')
    s4.setMAC('00:00:00:00:04:00', intf='s4-eth0')
    s4.setIP('192.168.15.2/24', intf='s4-eth1')
    s4.setMAC('00:00:00:00:04:01', intf='s4-eth1')
    s4.setIP('192.168.17.1/24', intf='s4-eth2')
    s4.setMAC('00:00:00:00:04:02', intf='s4-eth2')
    #in/out ospf packets interface
    s4.setIP('192.168.104.2/24', intf = 's4-eth4')
    s4.setMAC('00:00:00:00:04:4', intf = 's4-eth4')

#switch 5 configuration
    s5.setIP('192.168.5.1/24', intf='s5-eth0')
    s5.setMAC('00:00:00:00:05:00', intf='s5-eth0')
    s5.setIP('192.168.14.2/24', intf='s5-eth1')
    s5.setMAC('00:00:00:00:05:01', intf='s5-eth1')
    s5.setIP('192.168.16.2/24', intf='s5-eth2')
    s5.setMAC('00:00:00:00:05:02', intf='s5-eth2')
    s5.setIP('192.168.17.2/24', intf='s5-eth3')
    s5.setMAC('00:00:00:00:05:03', intf='s5-eth3')
    #in/out ospf packets interface
    s5.setIP('192.168.105.2/24', intf = 's5-eth4')
    s5.setMAC('00:00:00:00:05:4', intf = 's5-eth4')

#hosts default r
    h1 = net.get('h1')
    h1.setDefaultRoute("dev h1-eth0 via 192.168.1.1")

    h2 = net.get('h2')
    h2.setDefaultRoute("dev h2-eth0 via 192.168.2.1")

    h5 = net.get('h5')
    h5.setDefaultRoute("dev h5-eth0 via 192.168.5.1")

    print "Ready !"
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()