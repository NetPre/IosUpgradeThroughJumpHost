# from operator import ipow
from concurrent.futures import thread
from traceback import print_tb
from netmiko import Netmiko
from netmiko import redispatch , NetmikoAuthenticationException , NetmikoTimeoutException
import time
import logging

# logging.basicConfig(format='%(asctime)s :%(levelname)s:%(message)s',filename='./CombinationLogging.log', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

import re


def copyFileToSwitch(netCom, switchIosDict, ios):
    # print('------ Copy file to switch ------')
    #copy ftp:/ftpuser:password123@192.168.0.14/files/something.txt flash:something.txt
    out = netCom.send_command(
        'copy ftp:/{user}:{pas}@{ip}/files/{img} flash:{img}'.format(
            user=jump_host.get('username'),
            pas = jump_host.get('password'),
            ip  = jump_host.get('host'),
            img = switchIosDict[ios]['img'],
        ),
        delay_factor = 3,
        read_timeout = 100,
    )
    
    
def verifyMd5(netCom, switchIosDict, ios):
    # print('------ verify Md5 ------')
    md5Out = netCom.send_command('verify /md5 flash:/'+switchIosDict[ios]['img'])
    md5Out = re.search(r'[a-z0-9]{32}',md5Out)
    md5Out = md5Out.group() if md5Out else 'unknow'

    if md5Out == switchIosDict[ios]['md5']:
        return True
    elif md5Out =='unknow' or not md5Out:
        print('Check Md5 regex')
    else:
        return False

def copyIosToDevice(jump_host,device, switchIosDict):
    deviceIp = device['host']
    deviceUser = device['username']
    devicePass = device['password']
    print('--------------------{}'.format(deviceIp))
    try:
        netCom = Netmiko(**jump_host)
        junpHostPrompt = netCom.find_prompt()
        out = netCom.send_command_timing(
            'ssh -o ConnectTimeout=2 {}@{}\n'.format(deviceUser,deviceIp),
            last_read=4,
            read_timeout=8,
            strip_prompt=False,
            strip_command=False
            )
        # print(out)
        if 'assword' in out:
            out = netCom.send_command_timing(devicePass+'\n')            
            if 'assword' in out:
                print(deviceIp+'------Wrong device Password')
                #print(out)
                netCom.disconnect()
                return            
        elif 'The authenticity of host ' in out:
            out = netCom.send_command_timing('yes\n')
            out = netCom.send_command_timing(devicePass+'\n')
            if 'assword' in out:
                print(deviceIp+'------Wrong device Password')
                #print(out)
                netCom.disconnect()
                return            
        elif 'Connection timed out' in out:
            print(deviceIp+'-----device not reachble from jumpHost error "Connection timed out" ')
            #print(out)
            netCom.disconnect()
            return
        else:
            print(deviceIp+'------Unknown return from ssh session\n'+out+'\n--------------')
            netCom.disconnect()
            return

        # print(out)
        redispatch(netCom,device_type=device['device_type'])
        netCom.send_command_timing('enable')
        devicePrompt = netCom.find_prompt()
        if junpHostPrompt == devicePrompt:
            print(deviceIp+'error connecting to device junpHostPrompt is the same as devicePrompt')
            netCom.disconnect()
            return
        showVersion = netCom.send_command('show version')
        # print(out)
        iosFound = False
        for ios in switchIosDict:
            if ios in showVersion:
                iosFound = True
                corectMd5 = False
                retryCount = 3
                inc = 1
                while not corectMd5 and inc <=retryCount:
                    print(deviceIp+'------Copying seq# '+str(inc))
                    copyFileToSwitch(netCom, switchIosDict, ios)
                    corectMd5 = verifyMd5(netCom, switchIosDict, ios)
                    inc+=1
                else:
                    if corectMd5:
                        print(deviceIp+'!!!!!!!!!!!! Image copied correctly !!!!!!!!!!!!!!!!!!!')

                    else:
                        print(deviceIp+'!!!!!!!!!!!! please check why the image is not copied correctly')
        if not iosFound:
            print(deviceIp+' Device Type not found ')

    except  NetmikoAuthenticationException:
        print(deviceIp+' NetmikoAuthenticationException ')
    except NetmikoTimeoutException:
        print(deviceIp+' NetmikoTimeoutException ')
    except Exception as e :
        print(e)


switchIosDict = {
    '4.28.2F-28369039.4282F':{'img':'iosImag.txt','md5':'xf4e37596638b169716590aaec7a7ee1d'},
    '4.22.12M-23314347.42212M':{'img':'iosImag2.txt','md5':'a6beaca3dfeaabe721801a3e74b07eb2'},
    'b4.28.2F-28369039.4282F':{'img':'iosImg2.file','md5':'630eb8d254dd9c35b81a164bcdd8cc09'},
    'b4.22.12M-23314347.42212M':{'img':'iosImg.file','md5':'61eabaf2bf278703738b433ff884c91f'},
}


device = {
    'host':'192.168.0.201',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
}

jump_host = {
    'host':'192.168.0.14',
    'username':'ftpuser',
    'password':'password123',
    'device_type':'linux_ssh',
}


device_list = [
{
    'host':'192.168.0.200',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.201',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.202',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.203',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.204',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.205',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.206',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
},
{
    'host':'192.168.0.207',
    'username':'cisco',
    'password':'cisco',
    'device_type':'cisco_ios',
}
]




#for device in device_list:
#    copyIosToDevice(jump_host,device, switchIosDict)

from threading import Thread


numOfWork = 4


def work(jump_host,switchIosDict):
    while device_list:
        device = device_list.pop()
        copyIosToDevice(jump_host,device, switchIosDict)


thread_list = []

for w in range(numOfWork):
    t = Thread(target=work,args=(jump_host,switchIosDict,))
    t.start()
    thread_list.append(t)

for t in thread_list:
    t.join()

