import os
import types

# This file contains the engines that are most commonly used throughout the scripts.

# Yum Engine

def yum(packages):
  for package in packages:
    system("yum install -y %s" % package)

# Port Engines

def port6(ports, table='INPUT', action='ACCEPT', proto='tcp'):
  for port in ports:
    system("iptables -I %s -p %s --dport %s -j %s" % (table,
                                                      proto,
                                                      port,
                                                      action))

def port7(ports, zone='public', action='add', proto='tcp'):
  for port in ports:
    system("firewall-cmd --zone=%s --%s-port=%s/%s --permanent" % (zone,
                                                                   action,
                                                                   port,
                                                                   proto))

# System Engine (By far the most important.)

def system(args):
  if type(args) is types.StringType:
    os.system(args)
  else:
    for arg in args:
      os.system(arg)
