import os
import types

# This file contains the engines that are most commonly used throughout the scripts.

# Yum Engine

def yum(packages):
  for package in packages:
    system("yum install -y %s" % package)

# Port Engines

class Port_engine(object):
  def __init__(self, version):
    self.defaults = None
    self.command = None
    self._ver_check(version)

  def _ver_check(self, version):
    if version[0] == '6':
      self.defaults = {'table': 'INPUT', 'action': 'ACCEPT', 'proto': 'tcp'}
      self.command = "iptables -I %(table)s -p %(proto)s --dport %(port)s -j %(action)s"
    else:
      self.defaults = {'table': 'public', 'action': 'add', 'proto': 'tcp'}
      self.command = "firewall-cmd --zone=%(table)s --%(action)s-port=%(port)s/%(proto)s --permanent"

  def __call__(self, ports):
    for port in ports:
      self.defaults['port'] = port
      print(self.command % self.defaults)

# System Engine (By far the most important.)

def system(args):
  if type(args) is types.StringType:
    os.system(args)
  else:
    for arg in args:
      os.system(arg)
