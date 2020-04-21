import sys
from scapy.all import *
import scapy_ospf
import threading
import time

###---------------------------------###
### --------- CONFIG DATA --------- ###
###---------------------------------###
OSPF_VERSION = "2"
AREA_ID = "0.0.0.0"
LSUINT = 10
HELLOINT = 10
NEIGHBOR_TIMEOUT = 3*HELLOINT
ROUTER_INTERFACES =[
    { "name": "s1-eth0",    "address":"192.168.1.1",     "mask":"24",   "mac":"00:00:00:00:01:00",  "neighbour_ip":"192.168.1.2"},
    { "name": "s1-eth1",    "address":"192.168.11.1",    "mask":"24",   "mac":"00:00:00:00:01:01",  "neighbour_ip":"192.168.11.2"},
    { "name": "s1-eth2",    "address":"192.168.12.1",    "mask":"24",   "mac":"00:00:00:00:01:02",  "neighbour_ip":"192.168.12.2"}]
ROUTER_CP_INTERFACE = {"name": "s1-eth4",    "address":"192.168.101.2",     "mask":"24",   "mac":"00:00:00:00:01:04"}
ROUTER_ID = ROUTER_INTERFACES[0].get("address")
ALLSPFRouters = "224.0.0.5"
AUTH_TYPE = "0"

###---------------------------------###
### --------- DEFINITIONS --------- ###
###---------------------------------###
class OspfInterface:
    def __init__(self, ip_address, mask = "24", helloint = HELLOINT, neighbour_ip = "0", neighbour_id = "0"):
        self.ip_address = ip_address
        self.mask = mask
        self.helloint = helloint
        self.neighbour_ip = neighbour_ip
        self.neighbour_id = neighbour_ip

class OspfHelloThread(threading.Thread):
    def __init__(self,*args, **kwargs):
        super(OspfHelloThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
    def run(self):
        while(True):
            if self.stopped():
                return
            self.generate_hello()
            time.sleep(HELLOINT)
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()
    def generate_hello(self):
        for i in ROUTER_INTERFACES:
            p = scapy_ospf.Ether(src = ROUTER_CP_INTERFACE.get("mac"), dst = i.get("mac"))/IP(src = i.get("address"), dst = i.get("neighbour_ip"))/scapy_ospf.OSPF_Hdr(src=ROUTER_ID,area=AREA_ID)/scapy_ospf.OSPF_Hello()
            p.show()
            sendp(p, iface=i.get("name"))

class OspfSnifferThread(threading.Thread):
    def __init__(self,*args, **kwargs):
        super(OspfSnifferThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
    def run(self):
        t = AsyncSniffer(iface=ROUTER_CP_INTERFACE.get("name"), prn=self.process_packet)
        t.start()
        while(True):
            if self.stopped():
                t.stop()
                return
            time.sleep(0.5)
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()
    def process_packet(self, packet):
        packet.show()

def generate_lsu(    
    eth_src = ROUTER_CP_INTERFACE.get("mac"), 
    eth_dst = ROUTER_CP_INTERFACE.get("mac"), 
    ip_src =  ROUTER_CP_INTERFACE.get("address"),
    ip_dst =  ALLSPFRouters):
    #TODO tutaj dst nie all routers
    p = scapy_ospf.Ether(src = eth_src, dst = eth_dst)/IP(src = ip_src, dst = ip_dst )/scapy_ospf.OSPF_Hdr(src=ROUTER_ID,area=AREA_ID)/scapy_ospf.OSPF_LSUpd()
    return p
    
def validate_packet(packet):
    is_packet_valid = True
    if( packet[scapy_ospf.OSPF_Hdr].version == OSPF_VERSION and packet[scapy_ospf.OSPF_Hdr].area == AREA_ID and packet[scapy_ospf.OSPF_Hdr].authtype == AUTH_TYPE):
        is_packet_valid = False
    return is_packet_valid

def generate_OSPF_Interfaces():
    OSPF_Interfaces = []
    for interface in ROUTER_INTERFACES:
        OSPF_Interfaces.append(OspfInterface(
            ip_address = interface["address"],
            mask = interface["mask"],
            helloint = HELLOINT))
        print("{} OSPF Interface = {} generated!".format(time.strftime('%H:%M:%S'), interface["name"]))
    return OSPF_Interfaces


###---------------------------------###
### ----------- RUNNING ----------- ###
###---------------------------------###

def main():
#Create OSPF Interfaces for every sX-ethX
    OSPF_Interfaces = generate_OSPF_Interfaces()
    
    OspfHello = OspfHelloThread()
    OspfHello.start()
    print("{} OSPF_Hello_Thread started!".format(time.strftime('%H:%M:%S')))
    #OspfSniffer = OspfSnifferThread()
    #OspfSniffer.start()
    #print("{} OSPF_Sniffer_Thread started!".format(time.strftime('%H:%M:%S')))

    time.sleep(25)

    OspfHello.stop()
    OspfHello.join()
    #OspfSniffer.stop()
    #OspfSniffer.join()
    
if __name__ == "__main__":
    main()




