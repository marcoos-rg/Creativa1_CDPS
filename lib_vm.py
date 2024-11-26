import logging, os
from subprocess import call
from lxml import etree

log = logging.getLogger('manage-p2')

servers = ["s1", "s2", "s3", "s4" ,"s5"]

bridges = {
          "c1":["LAN1"],
          "lb":["LAN1"],
          "s1":["LAN2"],
          "s2":["LAN2"],
          "s3":["LAN2"],
          "s4":["LAN2"],
          "s5":["LAN2"]
          }

network = {
          "c1":["10.1.1.2", "10.1.1.1"],
          "s1":["10.1.2.11", "10.1.2.1"],
          "s2":["10.1.2.12", "10.1.2.1"], 
          "s3":["10.1.2.13", "10.1.2.1"],
          "s4":["10.1.2.14", "10.1.2.1"],
          "s5":["10.1.2.15", "10.1.2.1"]
          }


def editXml(vm):

  cwd = os.getcwd()
  path = cwd + "/" + vm

  tree = etree.parse(path + ".xml")

  root = tree.getroot()

  name = root.find("name")
  name.text = vm

  sourceFile = root.find("./devices/disk/source")
  sourceFile.set("file", path + ".qcow2")

  bridge = root.find("./devices/interface/source")
  bridge.set("bridge", bridges[vm][0])

  fout = open(path + ".xml", "w")
  fout.write(etree.tounicode(tree, pretty_print = True))
  fout.close()
  if vm == "lb":
    fin = open(path + ".xml",'r')   #fin es el XML correspondiente a lb, en modo solo lectura
    fout = open("tmp.xml",'w')  #fout es un XML temporal abierto en modo escritura
    for line in fin:
      if "</interface>" in line:
        fout.write("</interface>\n <interface type='bridge'>\n <source bridge='"+"LAN2"+"'/>\n <model type='virtio'/>\n </interface>\n")
      #si el XML de lb contiene un interface (que lo va a contener, ya que previamente se le habrá añadido el bridge LAN1), se le añade al XML temporal otro bridge: LAN2
      else:
        fout.write(line)
    fin.close()
    fout.close()

    call(["cp","./tmp.xml", path + ".xml"])  #sustituimos es XML por el temporal, que es el que contiene las dos LAN
    call(["rm", "-f", "./tmp.xml"])

def configurateNet(vm):

  cwd = os.getcwd()
  path = cwd + "/" + vm

  fout = open("hostname", 'w')
  fout.write(vm + "\n")
  fout.close()
  call(["sudo", "virt-copy-in", "-a", vm + ".qcow2", "hostname", "/etc"])
  call(["rm", "-f", "hostname"])

  call("sudo virt-edit -a" + vm + ".qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1" + vm + "/", shell=True)

  fout = open("interfaces", 'w')
  if vm == "lb":
    fout.write("auto lo\niface lo inet loopback\n\nauto eth0\niface eth0 inet static\n  address 10.1.1.1\n netmask 255.255.255.0\n gateway 10.1.1.1\nauto eth1\niface eth1 inet static\n  address 10.1.2.1\n netmask 255.255.255.0\n gateway 10.1.2.1")
  else: 
    fout.write("auto lo \niface lo inet loopback\n auto eth0\n iface eth0 inet static\n address " + network[vm][0] +"\nnetmask 255.255.255.0 \n gateway " + network[vm][1] + "\n")
  fout.close()
  call(["sudo", "virt-copy-in", "-a", vm + ".qcow2", "interfaces", "/etc/network"])
  call(["rm", "-f", "interfaces"])

  if vm == "lb":
    call("sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'", shell=True)


class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)

  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       aÃ±adir los campos que se necesiten
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    call(["qemu-img","create", "-f", "qcow2", "-F", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2",  self.name + ".qcow2"])
    call(["cp", "plantilla-vm-pc1.xml", self.name + ".xml"])
    vm = self.name
    editXml(vm)
    call(["sudo", "virsh", "define", self.name +".xml"])
    configurateNet(vm)
    # for i in interfaces:
    #  log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"]) 

  def start_vm (self):
    log.debug("start_vm " + self.name)
    call(["sudo", "virsh", "start", self.name])
    os.system("xterm -e 'sudo virsh console "+ self.name +"'&")

  def show_console_vm (self):
    log.debug("show_console_vm " + self.name)
    os.system("xterm -e 'sudo virsh console "+ self.name +"'&")

  def stop_vm (self):
    log.debug("stop_vm " + self.name)
    call(["sudo","virsh", "shutdown", self.name])

  def destroy_vm (self):
    log.debug("destroy_vm " + self.name)
    call(["sudo", "virsh", "destroy", self.name])
    call(["sudo", "virsh", "undefine", self.name])
    call(["rm", "-f", self.name+".qcow2"])
    call(["rm", "-f", self.name+".xml"])

class NET:
  def __init__(self, name):
    self.name = name
    log.debug('init net ' + self.name)

  def create_net(self):
      log.debug('create_net ' + self.name)
      call(["sudo", "brctl", "addbr", self.name])
      call(["sudo", "ifconfig", self.name, "up"])

  def destroy_net(self):
      log.debug('destroy_net ' + self.name)
      call(["sudo", "ifconfig", self.name, "down"])
      call(["sudo", "brctl", "delbr", self.name])
