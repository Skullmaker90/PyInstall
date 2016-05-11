import os
import platform
from ast import literal_eval
from subprocess import check_call

from libs import get_info

class SysBase(object):
  def __init__(self, conf_path):
    self.distro, self.version, self.flavor = platform.dist()
    info = get_info()
    self.name, self.ip = info[1], info[2]
    self.fire_keys = {'table': None,
                      'action': None,
                      'proto': 'tcp'}
    self.pkg_cmd = None
    self.conf = self._readConf(conf_path)
    self._set_cmd()

  def __call__(self):
    return platform.dist()

  def _readConf(self, conf_path):
    with open(conf_path, 'r') as f:
      c = literal_eval(f.read())
      return c

  def _set_cmd(self):
    pkg_mgrs = {'centos': 'yum', 'Ubuntu': 'apt-get'}
    self.pkg_cmd = [pkg_mgrs[self.distro], 'install', '-y']
    if self.distro == 'Ubuntu':
      self.pkg_cmd.append('--force-yes')

  def update(self):
    self.pkg_cmd[1] = 'update'
    check_call(self.pkg_cmd)

  def install(self, *pkgs):
    cmd = self.pkg_cmd[:]
    for pkg in pkgs:
      cmd.append(pkg)
    check_call(cmd)

  def port(self, *ports):
    s = self.conf['iptables']
    self.fire_keys['table'] = 'INPUT'
    self.fire_keys['action'] = 'ACCEPT'
    if (self.distro == 'centos' and self.version[0] == '7'):
      s = self.conf['firewall-cmd']
      self.fire_keys['table'] = 'public'
      self.fire_keys['action'] = 'add'
    for port in ports:
      self.fire_keys['port'] = port
      print("Instating rule: " + s % self.fire_keys)
      os.system(s % self.fire_keys)

  def start(self, service):
    s = 'service '
    if (self.distro == 'centos' and self.version[0] == '7'):
      s = 'systemctl '
    self.system(s + service + ' start')

  def system(self, command):
    os.system(command)

__name__ = 'SystemConfigClass'
