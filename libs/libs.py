import os
import socket
import fcntl
import struct

# Networking

def port_engine(service):
  service_ports = {plesk: ['8443'], LAMP: ['80'], wordpress: ['80']}
  if type(service) == types.FunctionType:
    for port in service_ports[service]:
      os.system('iptables -I INPUT 3 -p tcp --dport %s -j ACCEPT' % (port))

def get_info():
  hname = socket.gethostname()
  hfile = '/etc/hosts'
  ip = get_ip('eth0')
  return (hfile, hname, ip)

def populate(hfile, hname, ip):
  with open(hfile, 'a') as f:
    f.write('%s	%s' % (ip, hname))

def fqdn_check(config):
  info = get_info()
  if os.stat(info[0]).st_size <= 158:
    if (config['fqdn_hostname'] == 'default') and (config['fqdn_ip'] == 'default'):
      populate(info[0], info[1], info[2])
    else:
      populate(info[0], config['fqdn_hostname'], config['fqdn_ip'])

def get_ip(ifname):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return socket.inet_ntoa(fcntl.ioctl(
    s.fileno(),
    0x8915, # SIOCGIFADDR
    struct.pack('256s', ifname[:15])
  )[20:24])
