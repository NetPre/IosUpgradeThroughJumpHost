from netmiko import Netmiko
from netmiko import redispatch , NetmikoAuthenticationException , NetmikoTimeoutException
import time

import logging
# logging.basicConfig(format='%(asctime)s :%(levelname)s:%(message)s',filename='./CombinationLogging.log', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')




def copyIosToDevice(jump_host,device):
    deviceIp = device['host']
    deviceUser = device['username']
    devicePass = device['password']
    netCom = Netmiko(**jump_host)
    print(netCom.find_prompt())
    out = netCom.send_command_timing('ssh {}@{}\n'.format(deviceUser,deviceIp))
    print(out)
    if 'assword' in out:
        out = netCom.send_command_timing(devicePass+'\n')
        print(out)
    elif 'The authenticity of host ':
        out = netCom.send_command_timing('yes\n')
        out = netCom.send_command_timing(devicePass+'\n')
        print(out)
    else:
        print('-----------Unknown return from ssh session')

    redispatch(netCom,device_type=device['device_type'])
    netCom.send_command_timing('enable')
    print(netCom.find_prompt())
    out = netCom.send_command('show version')
    print(out)




device = {
    'host':'192.168.0.201',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
}

jump_host = {
    'host':'192.168.0.14',
    'username':'sftpuser',
    'password':'password123',
    'device_type':'linux_ssh',
}

copyIosToDevice(jump_host,device)    
