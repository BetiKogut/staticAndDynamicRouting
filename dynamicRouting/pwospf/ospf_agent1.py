import sys
from scapy.all import *
import scapy_ospf
import threading

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

# class OspfSniffer(threading.Thread):
#     def __init__(self, sniffed_packets):
#         threading.Thread.__init__(self)
#         self.sniffed_packets = sniffed_packets
#     def run(self):
#         sniffed_packets = sniff(iface = ROUTER_CP_INTERFACE.get("name"))

class OspfHelloThread(threading.Thread):
    def __init__(self,*args, **kwargs):
        super(OspfHelloThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
    def run(self):
        while(True):
            if self.stopped():
                return
            for i in ROUTER_INTERFACES:
                p = scapy_ospf.Ether(src = ROUTER_CP_INTERFACE.get("mac"), dst = i.get("mac"))/IP(src = i.get("address"), dst = i.get("neighbour_ip"))/scapy_ospf.OSPF_Hdr(src=ROUTER_ID,area=AREA_ID)/scapy_ospf.OSPF_Hello()
                p.show()
                sendp(p, iface=i.get("name"))
            time.sleep(HELLOINT)
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()

def generate_hello():
    for i in ROUTER_INTERFACES:
        p = scapy_ospf.Ether(src = ROUTER_CP_INTERFACE.get("mac"), dst = i.get("mac"))/IP(src = i.get("address"), dst = i.get("neighbour_ip"))/scapy_ospf.OSPF_Hdr(src=ROUTER_ID,area=AREA_ID)/scapy_ospf.OSPF_Hello()
        p.show()
        sendp(p, iface=i.get("name"))

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

###---------------------------------###
### ----------- RUNNING ----------- ###
###---------------------------------###

def main():
#Create OSPF Interfaces for every sX-ethX
    OSPF_Interfaces = []

    for interface in ROUTER_INTERFACES:
        OSPF_Interfaces.append(OspfInterface(
            ip_address = interface["address"],
            mask = interface["mask"],
            helloint = HELLOINT))
    
    #t = AsyncSniffer(iface = ROUTER_CP_INTERFACE.get("name"))
    #t.start()

    OspfHello = OspfHelloThread()
    OspfHello.start()
    print("OSPF_Hello_Thread started!")
    OspfHello.stop()
    OspfHello.join()
    


if __name__ == "__main__":
    main()




