import sys
from scapy.all import *
import scapy_ospf
import threading
import time
import dijkstra

###---------------------------------###
### --------- CONFIG DATA --------- ###
###---------------------------------###
OSPF_VERSION = "2"
AREA_ID = "0.0.0.0"
LSUINT = 30
HELLOINT = 10
NEIGHBOR_TIMEOUT = 3*HELLOINT
ROUTER_INTERFACES =[
    { "name": "s5-eth0",    "address":"192.168.5.1",     "mask":"24",   "subnet":"192.168.5.0",   "mac":"00:00:00:00:05:00",  "neighbor_ip":"192.168.5.2"},
    { "name": "s5-eth1",    "address":"192.168.14.2",    "mask":"24",   "subnet":"192.168.14.0",   "mac":"00:00:00:00:05:01",  "neighbor_ip":"192.168.14.1"},
    { "name": "s5-eth2",    "address":"192.168.16.2",    "mask":"24",   "subnet":"192.168.16.0",   "mac":"00:00:00:00:05:02",  "neighbor_ip":"192.168.16.1"},
    { "name": "s5-eth3",    "address":"192.168.17.2",    "mask":"24",   "subnet":"192.168.17.0",   "mac":"00:00:00:00:05:03",  "neighbor_ip":"192.168.17.1"}]
ROUTER_CP_INTERFACE = {"name": "s5-eth4",    "address":"192.168.105.2",     "mask":"24",   "mac":"00:00:00:00:05:04"}
ROUTER_ID = ROUTER_INTERFACES[0].get("address")
ALLSPFRouters = "224.0.0.5"
AUTH_TYPE = "0"

###---------------------------------###
### --------- DEFINITIONS --------- ###
###---------------------------------###
def log(msg):
    print("{}   {}".format(time.strftime('%H:%M:%S'),msg))

class TimerThread(Thread):
    def __init__(self, event, Database):
        Thread.__init__(self)
        self.stopped = event
        self.Database_Topo = Database
    def run(self):
        while not self.stopped.wait(1):
            for router in self.Database_Topo:
                if router["tictoc"] < 0:    #delete from db if router is dead
                    self.Database_Topo.remove(router)
                    log("Router {} pop".format(router))
                else: 
                    router["tictoc"]-=1     #tictocking timer
                    log("Timer tictoc'ing - {}".format(router["tictoc"]))
                    
class OspfInterface:
    def __init__(self, name, ip_address, mac, subnet, mask = "24", helloint = HELLOINT, neighbor_ip = "0", neighbor_id = "0"):
        self.name = name
        self.ip_address = ip_address
        self.mac = mac
        self.mask = mask
        self.subnet = subnet
        self.helloint = helloint
        self.neighbor_ip = neighbor_ip
        self.neighbor_id = neighbor_id

class RouterClass:
    router_id = ROUTER_ID
    area_id = AREA_ID
    lsuint = LSUINT
    ospf_interfaces = []
    def __init__(self, router_interfaces):
        for interface in router_interfaces:
            self.ospf_interfaces.append(OspfInterface(
                name = interface["name"],
                ip_address = interface["address"],
                mac = interface["mac"],
                mask = interface["mask"],
                subnet = interface["subnet"],
                helloint = HELLOINT,
                neighbor_ip = "0",
                neighbor_id = "0"))
            print("{}: OSPF Interface = {} generated".format(time.strftime('%H:%M:%S'), interface["name"]))

class DatabaseClass(list):
    def insert(self, hello):    #add router or update that it is alive
        log("Database insert hello called")
        if not self.search_with_router_id(hello):
            self.append(hello)
            log("Hello/Router appended to Database")
        else:
            x = self.get_index_with_router_id(hello)
            self[x]["tictoc"] = hello["tictoc"]
            log("TicToc updated")
    def insert_lsa(self, lsa):
        log("Database insert lsa called")
        if self.search_with_router_id(lsa) is True:
            x = self.get_index_with_router_id(lsa)
            self[x]["lsa"].append(lsa)   #TODO
            log("Database updated with lsa -> {}".format(self[x]))
    def remove(self, hello):
        index_to_remove = self.index(hello)
        self.pop(index_to_remove)
    def search_with_router_id(self, hello):
        for router in self:
            if router["router_id"] == hello["router_id"]:
                log("Router found")
                return True
        log("Nope")
        return False
    def get_index_with_router_id(self,hello):
        for router in self:
            if router["router_id"] == hello["router_id"]:
                log("Router found")
                ind = self.index(router)
                return ind
        log("Router not found")
        return False

class OspfHelloThread(threading.Thread):
    def __init__(self, router, *args, **kwargs):
        super(OspfHelloThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.router = router
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
    def generate_hello(self): #TODO
        for i in self.router.ospf_interfaces:
            p = scapy_ospf.Ether(src = ROUTER_CP_INTERFACE.get("mac"), dst = i.mac)/IP(src = i.ip_address, dst = i.neighbor_ip)/scapy_ospf.OSPF_Hdr(src=ROUTER_ID,area=AREA_ID)/scapy_ospf.OSPF_Hello(hellointerval=HELLOINT, deadinterval=NEIGHBOR_TIMEOUT)
            log("Hello generated")
            #p.show()
            sendp(p, iface=i.name)
            log("Hello sent")
            
class OspfLSUThread(threading.Thread):
    def __init__(self, router, *args, **kwargs):
            super(OspfLSUThread, self).__init__(*args, **kwargs)
            self._stop_event = threading.Event()
            self.router = router
    def run(self):
        time.sleep(3)
        while(True):
            if self.stopped():
                return
            self.generate_lsu()
            time.sleep(LSUINT)
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()
    def generate_lsu(self):
            for i in self.router.ospf_interfaces: #TODO
                p = scapy_ospf.Ether(src = ROUTER_CP_INTERFACE.get("mac"), dst = i.mac)/IP(src = i.ip_address, dst = i.neighbor_ip)/scapy_ospf.OSPF_Hdr(src=ROUTER_ID,area=AREA_ID)/scapy_ospf.OSPF_LSUpd()
                log("LSU generated")
                for k in self.router.ospf_interfaces:
                    if k is not i:
                        if k.mask == "24":
                            temp_mask = "255.255.255.0"
                        else:
                            temp_mask = mask
                        p[scapy_ospf.OSPF_LSUpd].lsalist.append(scapy_ospf.OSPF_Network_LSA(id=k.subnet,adrouter=self.router.router_id, mask = temp_mask))
                        log("LSA Appended")
                p.show()
                sendp(p, iface=i.name)
                log("LSU sent")

class OspfSnifferThread(threading.Thread):
    def __init__(self, Database, Router, *args, **kwargs):
        super(OspfSnifferThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.Database_Topo = Database
        self.Router_Inst = Router
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
        if(self.validate_packet(packet)):
            log("Packet Validated")
            packet.show()
            msg_type = packet[scapy_ospf.OSPF_Hdr].type
            log("Msg_type = {}".format(msg_type))
            msg_router_id = packet[scapy_ospf.OSPF_Hdr].src
            if msg_type == 1:                       #from scapy_ospf
                log("Handling hello packet")
                msg_hello_int = packet[scapy_ospf.OSPF_Hello].hellointerval
                mgs_deadinterval = packet[scapy_ospf.OSPF_Hello].deadinterval
                msg = {"router_id" : msg_router_id, "hello_int" : msg_hello_int, "tictoc":int(mgs_deadinterval), "lsa":[]}
                self.Database_Topo.insert(msg)
            elif msg_type == 4:                     #from scapy_ospf
                log("Handling LSU packet")
                for lsa in packet[scapy_ospf.OSPF_LSUpd].lsalist:
                    msg = {"router_id" : lsa.adrouter, "link_id" : lsa.id, "mask" : lsa.mask}
                    log("LSA = {}".format(msg))
                    self.Database_Topo.insert_lsa(msg)
    def validate_packet(self, packet):
        is_packet_valid = True
        if( packet[scapy_ospf.OSPF_Hdr].version == OSPF_VERSION and packet[scapy_ospf.OSPF_Hdr].area == AREA_ID and packet[scapy_ospf.OSPF_Hdr].authtype == AUTH_TYPE):
            is_packet_valid = False
        #return is_packet_valid
        return True

###---------------------------------###
### ----------- RUNNING ----------- ###
###---------------------------------###

def main():
    Database_Topo = DatabaseClass()
    Router = RouterClass(ROUTER_INTERFACES)
    
    OspfHello = OspfHelloThread(Router)
    OspfLSU = OspfLSUThread(Router)
    
    OspfHello.start()
    log("OSPF_Hello_Thread started")
    OspfLSU.start()
    log("OSPF_LSU_Thread started")

    stopFlag = Event()
    tictoc = TimerThread(stopFlag, Database_Topo )
    tictoc.start()
    log("Timer_Thread started")

    OspfSniffer = OspfSnifferThread(Database = Database_Topo, Router=Router)
    OspfSniffer.start()
    log("OSPF_Sniffer_Thread started")

    time.sleep(25)

    OspfHello.stop()
    OspfHello.join()
    OspfLSU.stop()
    OspfLSU.join()
    OspfSniffer.stop()
    OspfSniffer.join()
    stopFlag.set()          #stopTicToc-Timer
    
    log("---THE END---")
if __name__ == "__main__":
    main()




