import netmiko
from astropy.io import ascii
import configparser

global username,password,secret

config = configparser.ConfigParser()
config.read('config.ini')
username = config.get("credentials","username")
password = config.get("credentials","password")
secret = config.get("credentials","enable")

def cdpPort(mac,cdpint,rootIP):
    cisco_router = {
        'device_type': 'cisco_ios',
        'ip': rootIP,
        'username': username,
        'password':password,
        'secret': secret,
        'global_delay_factor': 0.1,
        'verbose': True,
    }
    net_connect = netmiko.ConnectHandler(**cisco_router)
    commands = "show cdp nei " + cdpint + " detail | inc IP address"
    output = net_connect.enable()
    output = net_connect.send_command(commands)
    splitIP = output.split(" ")
    # Last String is IP needed
    rootIP = (splitIP[len(splitIP) - 1])
    # check if port is a trunk port or int and output final result
    checkPort(mac,rootIP)



def checkPort(commands,rootIP):
    cisco_router = {
        'device_type': 'cisco_ios',
        'ip': rootIP,
        'username': username,
        'password':password,
        'secret': secret,
        'global_delay_factor': 0.1,
        'verbose': True,
    }
    net_connect = netmiko.ConnectHandler(**cisco_router)
    net_connect.enable()
    mac = commands
    output = net_connect.send_command(commands)
    splitInt = output.split(" ")
    commands = "show run int " + splitInt[len(splitInt) - 1]
    splitInt= (splitInt[len(splitInt) - 1])
    output = net_connect.send_command(commands)
    # check if port is a trunk port
    if (output.find("trunk") == -1):
        print("Port can be found on " + rootIP + " on int " + splitInt)
    else:
        cdpPort(mac,splitInt, rootIP)

def FindUserPort(userip):
    commands = ["do sh ip arp "+ userip + " | inc ARPA"]
    rootIP = "10.1.0.4"
    cisco_router = {
        'device_type': 'cisco_ios',
        'ip': rootIP,
        'username': username,
        'password':password,
        'secret': secret,
        'global_delay_factor': 0.1,
        'verbose': True,
    }
    net_connect = netmiko.ConnectHandler(**cisco_router)
    # Enter Enable mode because new IOS is a bit wonky with netmiko
    net_connect.enable()
    output = net_connect.send_config_set(commands)
    splito=output.split()
    #this is the row where the mac address is available
    commands="sh mac address-table address " + splito[22] + " | include Gi|TenGi"
    mac = commands
    net_connect = netmiko.ConnectHandler(**cisco_router)
    output = net_connect.send_command(commands)
    #turn data into a table
    data = ascii.read(output,delimiter=" ",comment='\*')
    #column 6 is output required
    cdpint = data['col6'][0]
    rootIP=cdpPort(mac,cdpint,rootIP)


ip = "10.1.28.166" #put the ip here
FindUserPort(ip)
