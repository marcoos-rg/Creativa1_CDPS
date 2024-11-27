#!/usr/bin/env python

from lib_vm import VM, NET
import logging, sys, os, json, subprocess
from subprocess import call
from lxml import etree

with open('manage-p2.json', 'r') as json_file:
    json_data = json.load(json_file)

number_of_servers = json_data['number_of_servers']
debug = json_data['debug']

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

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

if (number_of_servers > 5 or number_of_servers < 1):
    print("The number of servers should be from 1 to 5")
    sys.exit() 

def print_creativa_ascii():
    print(r"""
     $$$$$$\                                 $$\     $$\                             $$\   
    $$  __$$\                                $$ |    \__|                          $$$$ |  
    $$ /  \__| $$$$$$\   $$$$$$\   $$$$$$\ $$$$$$\   $$\ $$\    $$\ $$$$$$\        \_$$ |  
    $$ |      $$  __$$\ $$  __$$\  \____$$\\_$$  _|  $$ |\$$\  $$  |\____$$\         $$ |  
    $$ |      $$ |  \__|$$$$$$$$ | $$$$$$$ | $$ |    $$ | \$$\$$  / $$$$$$$ |        $$ |  
    $$ |  $$\ $$ |      $$   ____|$$  __$$ | $$ |$$\ $$ |  \$$$  / $$  __$$ |        $$ |  
    \$$$$$$  |$$ |      \$$$$$$$\ \$$$$$$$ | \$$$$  |$$ |   \$  /  \$$$$$$$ |      $$$$$$\ 
     \______/ \__|       \_______| \_______|  \____/ \__|    \_/    \_______|      \______|
                                                                                       
    """)

# Main
init_log()

def create(number_of_servers):
    print_creativa_ascii() # Imprime el Ascii Art
    print("Guillermo Peláez Cañizares y Marcos Rosado González") # Imprime autores
    print()
    image = "./cdps-vm-base-pc1.qcow2"
    number_of_servers = int(number_of_servers)
    json_data['number_of_servers'] = number_of_servers

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
        rango = str(n + 1)
        name = "s" + rango
        interfaces_server = [{"addr": f"10.1.2.1{n+1}", "mask": "255.255.255.0"}]
        server = VM(str(name))
        server.create_vm(image, interfaces_server)
    
    LAN1 = NET("LAN1")
    LAN1.create_net()
    LAN2 = NET("LAN2")
    LAN2.create_net()
    call(["sudo", "ifconfig", "LAN1", "10.1.1.3/24"])
    call(["sudo", "ip", "route", "add", "10.1.0.0/16", "via", "10.1.1.1"])

    # Guardar el nuevo número de servidores en el archivo JSON
    with open('manage-p2.json', 'w') as json_file: # Actualiza el JSON para que "number of servers cambie al valor introducido en el create (asi los demas comandos funcionan bien)"
        json.dump(json_data, json_file, indent=4)

    logger.debug("Correctly created the network")

def start(server):

    aux = server # Si no se especifica maquina, asume que son todas (all) (mirar los arguments abajo)
    if aux == "all":
        c1 = VM('c1') 
        c1.start_vm()
        lb = VM('lb')
        lb. start_vm()

        for n in range(0,number_of_servers):
            rango = str(n+1)
            name = "s" + rango
            server = VM(str(name))
            server.start_vm()

    else: # Si se especifica maquina, lo hace solo para esa
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

        for n in range(0,number_of_servers):
            rango = str(n+1)
            name = "s" + rango
            server = VM(str(name))
            server.stop_vm()

    else: 
        server = VM(server)
        server.stop_vm()

    logger.debug("Correctly stopped the network")

def destroy(): # No se puede hacer para una sola maquina por que no quiero afectar las redes e interfaces que se comparten, para eso mejor la apago la maquina que quiero
    c1 = VM('c1')
    c1.destroy_vm()
    lb = VM('lb')
    lb. destroy_vm()

    for n in range(0,number_of_servers):
        rango = str(n+1)
        name = "s" + rango
        server = VM(str(name))
        server.destroy_vm()
    
    eth0 = NET('LAN1')
    eth0.destroy_net()
    eth1 = NET('LAN2')
    eth1.destroy_net()

    logger.debug("Correctly destroyed the network")

# Funcionalidades Opcionales

def show_help(): # Un print de todos los comandos que hay y su uso
    print("\nLista de comandos disponibles:")
    commands_info = {
        "create (<num_servers>)": "Crea la red y el número de servidores especificado.",
        "start (<server_name>)": "Arranca todas las máquinas o una específica.",
        "stop (<server_name>)": "Detiene todas las máquinas o una específica.",
        "destroy": "Elimina todas las máquinas y redes configuradas.",
        "monitor (<server_name>)": "Muestra el estado actual de todas las máquinas virtuales.",
        "info (<server_name>)": "Muestra información detallada de una máquina virtual o de todas.",
        "help": "Muestra esta lista de comandos y su funcionalidad."
    }
    for command, description in commands_info.items():
        print(f"  {command}: {description}")
    print("\nEjemplo de uso:")
    print("  python3 manage-p2.py create 5")
    print("  python3 manage-p2.py info")
    print("  python3 manage-p2.py info s1\n")

def monitor(machine=None):
    print("\nEstado de las máquina(s) virtuales:")

    if (machine): # Si se especifica una maquina (Equivalente a "server" pero incluye tmb a c1 y lb)
        machines = [machine]
    else: # Si no se especifica imprime la info de todas las maquinas 
        machines = ["c1", "lb"] + [f"s{n}" for n in range(1, json_data['number_of_servers'] + 1)] 

    for machine in machines:
        # Ejecutar el comando virsh domstate
        result = subprocess.run( #Se utiliza .run en vez de .call porque es mas completo y me permite capturar la salida en stdout y stderr
            ["sudo", "virsh", "domstate", machine], 
            stdout=subprocess.PIPE, # Guarda los resultados del comando
            stderr=subprocess.PIPE, # O el error
            text=True
        )
        if result.returncode == 0:  # Comando ejecutado correctamente
            print(f"{machine}: {result.stdout.strip()}") # Imprime los resultados
        else:  # Error al ejecutar el comando
            print(f"{machine}: Error - {result.stderr.strip()}")
    
    print()

def info(machine=None):
    print("\nInformación de las máquina(s) virtuales:\n")

    if (machine): # Si se especifica una maquina (Equivalente a "server" pero incluye tmb a c1 y lb)
        machines = [machine]
    else: # Si no se especifica imprime la info de todas las maquinas 
        machines = ["c1", "lb"] + [f"s{n}" for n in range(1, json_data['number_of_servers'] + 1)]

    for machine in machines:
        # Ejecutar virsh dominfo para obtener información detallada
        result = subprocess.run( #Se utiliza .run en vez de .call porque es mas completo y me permite capturar la salida en stdout y stderr
            ["sudo", "virsh", "dominfo", machine],
            stdout=subprocess.PIPE, # Guarda los resultados del comando
            stderr=subprocess.PIPE, # O el error
            text=True
        )
        if result.returncode == 0:  # Comando ejecutado correctamente
            print(f"Máquina: {machine}") 
            print(result.stdout.strip()) # Imprime los resultados
            print("-" * 60)
        else:  # Error al ejecutar el comando
            print(f"{machine}: Error - {result.stderr.strip()}")

    print()

arguments = sys.argv

if len(arguments) == 1: # python3 manage-p2.py
    print("No se especificó ningún comando. Usa 'help' para ver la lista de comandos.")

if len(arguments) == 2: # python3 manage-p2.py <comando>
    if arguments[1] == "create":
        create(number_of_servers)
    elif arguments[1] == "start":
        start("all")
    elif arguments[1] == "stop":
        stop("all")
    elif arguments[1] == "destroy":
        destroy()
    elif arguments[1] == "monitor":
        monitor()  
    elif arguments[1] == "info":
        info() 
    elif arguments[1] == "help":
        show_help()
    else:
        print("Comando no reconocido. Usa 'help' para ver la lista de comandos.")

if len(arguments) >= 3: # python3 manage-p2.py <comando> <maquina(s)>
    if arguments[1] == "create":
        for server in arguments[2:]:
            create(server)
    if arguments[1] == "stop":
        for server in arguments[2:]:
            stop(server)
    if arguments[1] == "start":
        for server in arguments[2:]:
            start(server)
    if arguments[1] == "destroy":
        for server in arguments[2:]:
            destroy(server)
    if arguments[1] == "info":
        for server in arguments[2:]:
            info(server)
    if arguments[1] == "monitor":
        for server in arguments[2:]:
            monitor(server)

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
