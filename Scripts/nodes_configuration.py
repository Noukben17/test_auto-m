from fabric import Connection
from paramiko.ssh_exception import SSHException, NoValidConnectionsError


########## Preparation => Setup Nodes

#hosts = ["192.168.37.1", "192.168.37.4", "192.168.37.8", "192.168.37.", "192.168.37.12", "192.168.37.13", "192.168.37.15"]

hosts = []
OVS = [1, 4, 8, 10, 12, 13, 15]

ip_base = "192.168.37."

for i in range(len(OVS)):
    hosts.append(ip_base+str(OVS[i]))

##############

dict_interfaces = {}  # {'192.168.37.8': [' wlan0', ' wlan1'], .....}
dict_channels = {}
ctrl = "192.168.37.100:6633"

print("======================================== DEBUT CONFIGURATION ==================================")

for host in hosts:
    print("Init Stetp ==> ", host)    
    c = Connection(
        host=host,
        user="root",
        connect_kwargs={
            "password": "admin",
        },
    )
    
### Interfaces

    interfaces = []
    
    try:
        result_interface = c.run('ip link show | grep wlan', hide=True)
        s1 = str(result_interface.stdout.strip())
        s = s1.split("\n") # lines of interfaces
        for s_ in s:
            y = s_.split(":")
            interfaces.append(y[1])
            
        #print("Interfaces WIFI: ", interfaces)
        dict_interfaces[host] = interfaces
               
    except (SSHException, NoValidConnectionsError):
        print("PB lors de la connexion ssh avec :", host)
        pass    

print("Host -> Interfaces WIFI: ", dict_interfaces)

### Channel Configurations + OF Configurations


dict_channels = {'192.168.37.1': [44],'192.168.37.4': [44, 104], '192.168.37.8': [1, 11],  '192.168.37.10': [160, 104], '192.168.37.12': [1, 6, 160], '192.168.37.13': [6]} 
#dict_channels = {'192.168.37.1': [44],'192.168.37.4': [44, 104], '192.168.37.8': [1, 11],  '192.168.37.10': [160, 104], '192.168.37.12': [1, 6, 160], '192.168.37.13': [6]} 


for host in hosts:
    print("Configuration ==> ", host)    
    c = Connection(
        host=host,
        user="root",
        connect_kwargs={
            "password": "admin",
        },
    )    
    try:
        #O.F
        result = c.run('ovs-vsctl emer-reset', hide=True)
        cmd_ = 'ovs-vsctl set-controller br0 tcp:' + ctrl
        result = c.run(cmd_, hide=True)
        result = c.run('ovs-vsctl set-fail-mode br0 secure', hide=True)
        result = c.run('ovs-vsctl set bridge br0 other-config:disable-in-band=true', hide=True)
        
        #Channels ==> verifier apres que wlan_i <=> radio_i
        for k in range(len(dict_channels[host])):
            cmd_ = 'set wireless.radio' + str(k)+ '.channel=' + str(dict_channels[host][k])
            result = c.run(cmd_, hide=True)
            
        result = c.run('uci commit wireless;wifi', hide=True)

               
    except (SSHException, NoValidConnectionsError):
        print("PB lors de la connexion ssh avec :", host)
        pass
    
print("======================================== FIN CONFIGURATION ====================================")



#c.run('ifconfig br0 | grep "inet addr"')