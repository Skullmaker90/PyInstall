import os
import socket
import fcntl
import struct
import platform
import yum

class SysConfig(object):
  def __init__(self):
    self.os = None
    self.install = None
    self.fwstring = None
    self.fwargs = None
    self._set_vars()

  def _set_vars(self):
    s = platform.dist()
    self.os = '%s %s' % (s[0], s[1][:2])
    configs = {'centos 6.': {
                  'install': yum_install,
                  'fwargs': {
                    'kwargs': {'table': 'INPUT',
                                'action': 'ACCEPT',
                                'proto': 'tcp'},
                    'string': ("iptables -I %(table)s "
                                  "-p %(proto)s "
                                  "--dport %(port)s "
                                  "-j %(action)s")}
                   },
               'centos 7.': {
                 'install': yum_install,
                 'fwargs': {
                   'kwargs': {'table': 'public',
                              'action': 'add',
                              'proto': 'tcp'},
                   'string': ("firewall-cmd --zone=%(table)s "
                                "--%(action)s-port=%(port)s/%(proto)s "
                                "--permanant")}
                  },
               'Ubuntu 12': {
                 'install': apt_get,
                 'fwargs': {
                    'kwargs': {'table': 'INPUT',
                                'action': 'ACCEPT',
                                'proto': 'tcp'},
                    'string': ("iptables -I %(table)s "
                                  "-p %(proto)s "
                                  "--dport %(port)s "
                                  "-j %(action)s")},
                 },
               'Ubuntu 14': {
                 'install': apt_get,
                 'fwargs': {
                    'kwargs': {'table': 'INPUT',
                                'action': 'ACCEPT',
                                'proto': 'tcp'},
                    'string': ("iptables -I %(table)s "
                                  "-p %(proto)s "
                                  "--dport %(port)s "
                                  "-j %(action)s")}
                 }
              }
    self.install = configs[self.os]['install']
    self.fwstring = configs[self.os]['fwargs']['string']
    self.fwargs = configs[self.os]['fwargs']['kwargs']

# Installers

def yum_install(*args):
  yb = yum.YumBase()
  for arg in args:
    yb.install(name='%s' % arg)
  yb.resolveDeps()
  yb.processTransaction()

def apt_get(*args):
  s = ['apt-get', 'install', '-y']
  for arg in args:
    s.append(arg)
  os.system(s)

# Networking

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
