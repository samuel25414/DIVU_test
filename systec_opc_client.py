#!/usr/bin/env python
############################################
# OPC-UA client for the am2315-opc-server
# Carlos.Solans@cern.ch
############################################

from opcua import Client
from opcua import ua

class systec:
    def __init__(self,name):
        self.verbose=False
        self.name=name
        self.nodes = {"Port":None, "Address":None,
                      "Chan_00":None, "Chan_01":None, "Chan_02":None, "Chan_03":None, "Chan_04":None, 
                      "Chan_05":None, "Chan_06":None, "Chan_07":None, "Chan_08":None, "Chan_09":None,
                      "Chan_10":None, "Chan_11":None, "Chan_12":None, "Chan_13":None, "Chan_14":None, 
                      "Chan_15":None, "Chan_16":None, "Chan_17":None, "Chan_18":None, "Chan_19":None,
                      "Chan_20":None, "Chan_21":None, "Chan_22":None, "Chan_23":None, "Chan_24":None, 
                      "Chan_25":None, "Chan_26":None, "Chan_27":None, "Chan_28":None, "Chan_29":None,
                      "Chan_30":None, "Chan_31":None, "Chan_32":None, "Chan_33":None, "Chan_34":None, 
                      "Chan_35":None, "Chan_36":None, "Chan_37":None, "Chan_38":None, "Chan_39":None,
                      "Chan_40":None, "Chan_41":None, "Chan_42":None, "Chan_43":None, "Chan_44":None, 
                      "Chan_45":None, "Chan_46":None, "Chan_47":None, "Chan_48":None, "Chan_49":None,
                      "Chan_50":None, "Chan_51":None, "Chan_52":None, "Chan_53":None, "Chan_54":None, 
                      "Chan_55":None, "Chan_56":None, "Chan_57":None, "Chan_58":None, "Chan_59":None,
                      "Chan_60":None, "Chan_61":None, "Chan_62":None, "Chan_63":None,  
                      }
        pass
    def LoadNodes(self,obj):
        for obj in obj.get_children():
            if obj.get_display_name().Text in self.nodes:
                if self.verbose: print("systec::LoadNodes Found node: %s" % (obj.get_display_name().Text)) 
                self.nodes[obj.get_display_name().Text]=obj
                pass
            pass
        pass
    def SetVerbose(self, enable):
        self.verbose = enable
        pass  
    def GetVerbose(self):
        return self.verbose
    def GetName(self):
        return self.name
    def GetNodes(self):
        return self.nodes
    def GetNode(self,name):
        return self.nodes[name]
    pass
    
class systec_opc_client:
    def __init__(self, connstr,connect=False):
        self.verbose=False
        self.systec=None
        self.connstr = connstr
        self.client = Client(connstr)
        self.client.session_timeout = 600000
        self.client.secure_channel_timeout = 600000
        if connect: self.Open()
        pass
    def Open(self):
        try:
            self.client.connect()
        except:
            print("Cannot connect to server on: %s" % self.connstr)
            return False
        self.LoadNodes()
        return True
    def LoadNodes(self):
        for obj in self.client.get_objects_node().get_children():
            if self.verbose: print("Parsing : %s" % (obj.get_display_name().Text))
            if not "Systec" in obj.get_display_name().Text: continue
            if self.verbose: print("Found Systec: %s" % (obj.get_display_name().Text)) 
            ro=systec(obj.get_display_name().Text)
            ro.SetVerbose(self.verbose)
            ro.LoadNodes(obj)
            self.systec=ro
            pass
        pass
    def Close(self):
        self.client.disconnect()
        pass
    def PrintServerInfo(self):
        self.root = self.client.get_root_node()
        print("Root node is: ", self.client.get_root_node())
        print("Children of root are: ", self.client.get_root_node().get_children())
        print("Children of objects are: ", self.client.get_objects_node().get_children())
        pass
    def SetVerbose(self, v):    
        self.verbose = v
        pass
    def GetSystec(self):
        return self.systec
    pass

if __name__=="__main__":
    
    import os
    import sys
    import signal
    import argparse
    import time
    import datetime

    constr="opc.tcp://localhost:4841"
    
    parser=argparse.ArgumentParser()
    parser.add_argument('-s','--constr',help="connection string: %s" % constr, default=constr)
    parser.add_argument('-v','--verbose',help="enable verbose mode", action="store_true")
    
    args=parser.parse_args()
    
    client=systec_opc_client(args.constr)
    client.SetVerbose(args.verbose)
    if not client.Open(): sys.exit()
    
    cont = True
    def signal_handler(signal, frame):
        print("You pressed ctrl+C")
        global cont
        cont = False
        return

    signal.signal(signal.SIGINT, signal_handler)

    print("Reading")
    
    while True:
        s="Readout %s:: " % client.GetSystec().GetName()
        for node in client.GetSystec().GetNodes():
            s+="%s: %s, " % (node, client.GetSystec().GetNode(node).get_value())
            pass
        print (s)
        if cont==False: break
        time.sleep(5)
        pass
    pass
    print("Closing connection")
    client.Close()
    print("Have a nice day")
    pass
