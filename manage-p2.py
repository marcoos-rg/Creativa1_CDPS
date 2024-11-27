#!/usr/bin/env python

from lib_vm import VM, NET
import logging, sys, os, json
from subprocess import call
from lxml import etree

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('manage-p2')

def init_log():
    # Creacion y configuracion del logger
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False

def pause():
    programPause = input("-- Press <ENTER> to continue...")

with open('manage-p2.json', 'r') as json_file:
    json_data = json.load(json_file)

number_of_servers = json_data['number_of_servers']
debug = json_data['debug']

if (number_of_servers > 5 or number_of_servers < 1):
    print("The number of servers should be from 1 to 5")
    sys.exit()

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)     

# Main
init_log()
print('CDPS - mensaje info1')

def create(number_of_servers):
    image = "./cdps-vm-base-pc1.qcow2"
    number_of_servers = int(number_of_servers)

    # Cliente c1
    interfaces_c1 = [{"addr": "10.1.1.2", "mask": "255.255.255.0"}]

    # Balanceador lb
    interfaces_lb = [
        {"addr": "10.1.1.1", "mask": "255.255.255.0"},
        {"addr": "10.1.2.1", "mask": "255.255.255.0"}
    ]

    c1 = VM("c1")
    c1.create_vm(image, interfaces_c1)
    lb = VM("lb")
    lb.create_vm(image, interfaces_lb)

    # Servidores s1, s2, ..., sN
    for n in range(0, number_of_servers):
        parseo = str(n + 1)
        name = "s" + parseo
        interfaces_server = [{"addr": f"10.1.2.1{n+1}", "mask": "255.255.255.0"}]
        server = VM(str(name))
        server.create_vm(image, interfaces_server)
    
    LAN1 = NET("LAN1")
    LAN1.create_net()
    LAN2 = NET("LAN2")
    LAN2.create_net()
    call(["sudo", "ifconfig", "LAN1", "10.1.1.3/24"])
    call(["sudo", "ip", "route", "add", "10.1.0.0/16", "via", "10.1.1.1"])

    logger.debug("Correctly created the network")

def start(server):
    aux = server
    if aux == "all":
        c1 = VM('c1')
        c1.start_vm()
        lb = VM('lb')
        lb. start_vm()

        for n in range(0,number_of_servers+1):
            parseo = str(n+1)
            name = "s" + parseo
            server = VM(str(name))
            server.start_vm()

    else: 
        server = VM(server)
        server.start_vm()

    logger.debug("Correctly started the network")

def stop(server):
    aux = server
    if aux == "all":
        c1 = VM('c1')
        c1.stop_vm()
        lb = VM('lb')
        lb. stop_vm()

        for n in range(0,number_of_servers+1):
            parseo = str(n+1)
            name = "s" + parseo
            server = VM(str(name))
            server.stop_vm()

    logger.debug("Correctly stopped the network")

def destroy():
    c1 = VM('c1')
    c1.destroy_vm()
    lb = VM('lb')
    lb. destroy_vm()

    for n in range(0,number_of_servers+1):
        parseo = str(n+1)
        name = "s" + parseo
        server = VM(str(name))
        server.destroy_vm()
    
    eth0 = NET('LAN1')
    eth0.destroy_net()
    eth1 = NET('LAN2')
    eth1.destroy_net()

    logger.debug("Correctly destroyed the network")

arguments = sys.argv
if len(arguments) == 2:
    if arguments[1] == "create":
        create(number_of_servers)
    if arguments[1] == "start":
        start("all")
    if arguments[1] == "stop":
        stop("all")
    if arguments[1] == "destroy":
        destroy()

if len(arguments) >= 3:
    if arguments[1] == "create":
        for server in arguments[2:]:
            create(server)
    if arguments[1] == "stop":
        for server in arguments[2:]:
            stop(server)

    

    

# Ejemplo de creacion de una maquina virtual
# s1 = VM('s1')
# pause()

# ifs = []
# ifs.tt( { "addr": "10.11.12.10", "mask": "255.255.255.0" } )
# ifs.append( { "addr": "10.11.13.10", "mask": "255.255.255.0" } )
# s1.create_vm('cdps-vm.qcow2', ifs )
# pause()

# s1.start_vm()
# pause()

# s1.stop_vm()
# pause()

# s1.destroy_vm()
