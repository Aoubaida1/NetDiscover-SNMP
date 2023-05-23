from pysnmp.hlapi import *
from device_info import DeviceInfo, DeviceDict
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import sys


ip_from_user = sys.argv[1]
community_from_user = sys.argv[2]



# SNMP credentials
community = CommunityData(community_from_user) # take it from the user
G = nx.Graph()
device_dict = DeviceDict()
possible = set()
still_possible = True  


       
def draw_G():
    pos = nx.spring_layout(G)
    node_color = [(0.225, 0.9882, 0.688) if node[0] == "R" else (0.247, 0.757, 0.788) if node[0] == "D" else (0.9882, 0.3176, 0.5216) for node in G.nodes()] 
    nx.draw(G, pos, node_color=node_color, with_labels=True)
    plt.title('Network Topology')
    plt.show()


def get_table(ip_address,OID):
    """get_table function work good to get any table that indexed 
        using the ip address
        
        return a 2-D array 
    """
    getnext_command = nextCmd(
        SnmpEngine(),
        community,
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(OID)),
        lexicographicMode=False
    )
    
    # Retrieve the table
    input_list = []
    for error_indication, error_status, error_index, var_binds in getnext_command:
        if error_indication:
            break
        elif error_status:
            break
        else:
            var_index = var_binds[0][0][-4:].prettyPrint()
            var_value = var_binds[0][1].prettyPrint()

            input_list.append([var_index, var_value])

          
    output_list = []
    temp_dict = {}

    # Iterate through the input list and group elements with the same first element
    for elem in input_list:
        if elem[0] in temp_dict:
            temp_dict[elem[0]].extend(elem[1:])
        else:
            temp_dict[elem[0]] = elem[1:]

    # Convert the dictionary into the desired output format
    for key, value in temp_dict.items():
        output_list.append([key] + value)
    return output_list
    

      
def ip_Net_To_Media_Table(ip_address):
    # OID ipNetToMediaTable
    ip_Net_To_Media_Table_OID = '1.3.6.1.2.1.4.22'
    
    # Call get_table
    output_list = get_table(ip_address, ip_Net_To_Media_Table_OID)
    return output_list

def ip_Route_Table(ip_address):
    # OID ipRouteTable
    ip_Route_Table_OID = '1.3.6.1.2.1.4.21'
    
    # Call get_table
    output_list = get_table(ip_address, ip_Route_Table_OID)
    return output_list


def ip_Addr_Table(ip_address):
    # OID ipRouteTable
    ip_Route_Table_OID = '1.3.6.1.2.1.4.20'
    
    # Call get_table
    output_list = get_table(ip_address, ip_Route_Table_OID)
    return output_list
    

def dot1dTpFdbTable(ip_address):
    # OID ipRouteTable
    ip_Route_Table_OID = '1.3.6.1.2.1.17.4.3'
    
    # Call get_table
    output_list = get_table(ip_address, ip_Route_Table_OID)
    return output_list
    
 
 
 
def sys_name(ip_address):
    SNMP_OID = '1.3.6.1.2.1.1.5'  # OID for sysName MIB object
    
    getnext_command = nextCmd(
        SnmpEngine(),
        community,
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(SNMP_OID)),
        lexicographicMode=False
    )

    # Process SNMP response
    errorIndication, errorStatus, errorIndex, varBinds = next(getnext_command)
    if errorIndication:
        # Naming convention for devices not supporting SNMP
        return('D' + ip_address.split('.')[-2] + '.' + ip_address.split('.')[-1]) 
    elif errorStatus:
        return(f'SNMP GET request returned error: {errorStatus}')
    else:
        # Extract sysName value from response
        for varBind in varBinds:
            name = varBind.prettyPrint().split('=')[1].strip()                        
            return(name)
    
"""

def table_graph(ip_address):
    node_table = []
    u_node = sys_name(ip_address)   # get the name of the center node
    table_ip = ip_Net_To_Media_Table(ip_address) # get the ip of connected node
    for element in table_ip:
        if element[4] == str(3):
            v_node = sys_name(element[3])
            if v_node == "SNMP GET request failed: No SNMP response received before timeout":
                v_node = u_node +" " +element[3]
            node_table.append([u_node,v_node])
    return node_table     
        
""" 
 
def sameInterface_conflict(array, node):
    switch_name = ""  # empty string mean False in if switch_name:
    array_val = array
    for interface_index in array: # search for switch 
        Is_switch = device_dict.get_device(interface_index[0]).get_name()
        if Is_switch[0] != "D":
            switch_name = Is_switch
            array_val.remove(interface_index)
            break
         
    if not switch_name: # the switch does not have snmp!
        switch_name = "HUB_" + node[1:]
        
    G.add_edge(switch_name,node) # connect the switch to the router 
    for interface_index2 in array_val: # connect all devices to the router through the switch 
        G.add_edge(switch_name, device_dict.get_device(interface_index2[0]).get_name())
                 
 
    
def device_register(ip_address):
    """This function registers a device by retrieving its information, 
    create a soft copy of the device using object of DeviceInfo adding it to a device dictionary, 
    and saving its MAC table as a CSV file if it is a router."""
    device_name = sys_name(ip_address)
    print(device_name + " has been added!!")
    MAC_table = ip_Net_To_Media_Table(ip_address)
    interface_IPs = [[item[0], item[2]] for item in MAC_table if item[-1] == '4']   # static 
    device = DeviceInfo(device_name)
    if interface_IPs: # True if the device havs snmp 
        device.set_interface_IPs(interface_IPs)
    else:
        device.set_interface_IPs([[ip_address,ip_address +'X']])
        
    device_dict.add_device(device)
    dynamic = [[item[0],item[1]] for item in MAC_table if item[-1] == '3'] # dynamic interface number + ip address
    dynamic_possible = [item[0] for item in MAC_table if item[-1] == '3'] # dynamic ip address only 
    for ip in dynamic_possible:
        if not device_dict.get_device(ip):
            possible.add(ip)
            
    if device_name[0] == "R": # simple chick it the device is a router
        device.set_neighbor(dynamic)
        column_titles = ["IP Address", "Interface Index", "MAC Address", "IP Address 2", "Type"]
        # Create a pandas dataframe from the data and column titles
        df = pd.DataFrame(MAC_table, columns=column_titles)

        # Save the dataframe to a CSV file
        df.to_csv(device_name +".csv", index=False)

    


def serach():
    global still_possible
    while(still_possible):# loop over all the element of possible
        if not possible:
            still_possible = False
        
        else:
            ip = next(iter(possible))
            possible.remove(ip)
            if not device_dict.get_device(ip): # if the ip is not in device_dict that mean it is a new device
                device_register(ip)


def graph():    
    dict_devices = device_dict.get_devices_dict()
    unique_values = {}
    for key in dict_devices:
        value = dict_devices[key].get_name()
        if value not in unique_values:
            unique_values[value] = key           
    node_table = []
    for key, value in unique_values.items():
        u_node = key
        
        table_ip, conflict = device_dict.get_device(value).get_neighbor_v2()
                        
        if conflict:
            for array_conflict in conflict:
                sameInterface_conflict(array_conflict, u_node)
                
        for element in table_ip:
            G.add_edge(u_node, device_dict.get_device(element).get_name())
            

        
    
    
    


def starter(ip):
    device_register(ip)
    serach()
    graph()
    draw_G()
    

print()


starter(ip_from_user)  