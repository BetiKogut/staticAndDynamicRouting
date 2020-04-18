import sys
from scapy.all import *
import scapy_ospf

###---------------------------------###
### --------- CONFIG DATA --------- ###
###---------------------------------###
AREA_ID = "0.0.0.0"
LSUINT = 10
HELLOINT = 10
ROUTER_INTERFACES =[
    {"name:": "s1-eth0",    "address":"192.168.1.1",     "mask":"24"},
    {"name:": "s1-eth1",    "address":"192.168.11.1",    "mask":"24"},
    {"name:": "s1-eth2",    "address":"192.168.12.1",    "mask":"24"}]
ROUTER_ID = ROUTER_INTERFACES[0].get("address")
ALLSPFRouters = "224.0.0.5"
###---------------------------------###
### --------- DEFINITIONS --------- ###
###---------------------------------###
class OspfInterface:
    def __init__(self, ip_address, mask, helloint, neighbour_ip, neighbour_id):
        self.ip_address = ip_address
        self.mask = mask
        self.helloint = helloint
        self.neighbour_ip = neighbour_ip
        self.neighbour_id = neighbour_id

def generate_hello(**hello_param):
    p = scapy_ospf.Ether()/IP()/scapy_ospf.OSPF_Hdr()/scapy_ospf.OSPF_Hello()
    return p

def generate_lsu(**lsu_param):
    p = scapy_ospf.Ether()/IP()/scapy_ospf.OSPF_Hdr()/scapy_ospf.OSPF_LSUpd()
    return p

###---------------------------------###
### ----------- RUNNING ----------- ###
###---------------------------------###

#Create OSPF Interfaces for every sX-ethX
OSPF_Interfaces = []

for interface in ROUTER_INTERFACES:
    OSPF_Interfaces.append(OspfInterface(
        interface["address"],
        interface["mask"],
        HELLOINT,
        "0",
        "0"
    ))

