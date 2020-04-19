import sys
from scapy.all import *
import scapy_ospf

###---------------------------------###
### --------- CONFIG DATA --------- ###
###---------------------------------###
OSPF_VERSION = "2"
AREA_ID = "0.0.0.0"
LSUINT = 10
HELLOINT = 10
NEIGHBOR_TIMEOUT = 3*HELLOINT
ROUTER_INTERFACES =[
    {"name:": "s1-eth0",    "address":"192.168.1.1",     "mask":"24",   "mac":"00:00:00:00:01:00"},
    {"name:": "s1-eth1",    "address":"192.168.11.1",    "mask":"24",   "mac":"00:00:00:00:01:01"},
    {"name:": "s1-eth2",    "address":"192.168.12.1",    "mask":"24",   "mac":"00:00:00:00:01:02"}]
ROUTER_CP_INTERFACE =
    {"name:": "s1-eth4",    "address":"192.168.101.2",     "mask":"24",   "mac":"00:00:00:00:01:04"}
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
        self.neighbour_id = neighbour_id


def generate_hello(
    eth_src = ROUTER_CP_INTERFACE["mac"], 
    eth_dst = ROUTER_CP_INTERFACE["mac"], 
    ip_src =  ROUTER_CP_INTERFACE["address"],
    ip_dst =  ALLSPFRouters):
    #TODO
    p = scapy_ospf.Ether(src = eth_src, dst = eth_dst)/IP(src = ip_src, dst = ip_dst )/scapy_ospf.OSPF_Hdr()/scapy_ospf.OSPF_Hello()
    return p

def generate_lsu(    
    eth_src = ROUTER_CP_INTERFACE["mac"], 
    eth_dst = ROUTER_CP_INTERFACE["mac"], 
    ip_src =  ROUTER_CP_INTERFACE["address"],
    ip_dst =  ALLSPFRouters):
    #TODO tutaj dst nie all routers
    p = scapy_ospf.Ether(src = eth_src, dst = eth_dst)/IP(src = ip_src, dst = ip_dst )/scapy_ospf.OSPF_Hdr()/scapy_ospf.OSPF_LSUpd()
    return p

def send_periodic_hello(){
    hello = generate_hello()
    
    #TODO

    sleep(HELLOINT)
    sendp(hello, iface = ROUTER_CP_INTERFACE["name"])
}

def sniff_packets(){
    #TODO
    sniffed_packets = sniff(iface = ROUTER_CP_INTERFACE["name"])
    #sniffed_packets to tablica zlapanych pakietow
}

def validate_packet(packet){
    is_packet_valid = True
    if( packet[scapy_ospf.OSPF_Hdr].version == OSPF_VERSION && packet[scapy_ospf.OSPF_Hdr].area == AREA_ID) && packet[scapy_ospf.OSPF_Hdr].authtype == AUTH_TYPE):
        is_packet_valid = False
    return is_packet_valid
}

def handle_incoming_packet(packet){
    if (validate_packet(packet)){
        


    }
        

}

###---------------------------------###
### ----------- RUNNING ----------- ###
###---------------------------------###

#Create OSPF Interfaces for every sX-ethX
OSPF_Interfaces = []

for interface in ROUTER_INTERFACES:
    OSPF_Interfaces.append(OspfInterface(
        ip_address = interface["address"],
        mask = interface["mask"],
        helloint = HELLOINT))

while(running){

#TODO

}




