class DeviceInfo:
    def __init__(self, name):
        self.interface_IPs = []
        self.neighbor = []
        self.name = name 
        
    
    def get_name(self):
        return self.name
    
    def get_neighbor(self):
        return self.neighbor

    def get_neighbor_v2(self):
        arr = self.neighbor
        same_first_dict = {}
        diff_first = []

        for elem in arr:
            if elem[1] in same_first_dict:
                same_first_dict[elem[1]].append(elem)
            else:
                same_first_dict[elem[1]] = [elem]

        for k, v in same_first_dict.items():
            if len(v) > 1:
                diff_first.append(v)
        same = [elem[0] for elem in arr if elem not in sum(diff_first, [])]
        
        return same, diff_first
    
    def set_name(self, name):
        self.name = name
        
    def set_interface_IPs(self, ips):
        self.interface_IPs = ips
    
    def set_neighbor(self, ips):
        self.neighbor = ips
         
    def __call__(self):
        return self.get_name()
    
    
class DeviceDict:
    def __init__(self):
        self.devices = {}
        self.mac_ip = {}

    def add_device(self, device):
        for interface in device.interface_IPs:            
            self.devices[interface[0]] = device
            self.mac_ip[interface[1]] = interface[0]

    def get_devices_dict(self):
        return self.devices
        
    def get_device(self, ip):
        return self.devices.get(ip)
    
    def get_IP_from_MAC(self, mac):
        return self.mac_ip.get(mac)
    
