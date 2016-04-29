import os
import types

# This file contains the engines that are most commonly used throughout the scripts.

# Yum Engine

def yum(packages):
  for package in packages:
    system("yum install -y %s" % package)

# Port Engine

def port(ports, table='INPUT', action='ACCEPT'):
  for port in ports:
    system("iptables -I %s --p tcp --dport %s -j %s" % (table,
                                                        port,
                                                        action))

# System Engine (By far the most important.)

def system(args):
  if type(args) is types.StringType:
    os.system(args)
  else:
    for arg in args:
      os.system(arg)
