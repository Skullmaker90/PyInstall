import os
import types

# This file contains the engines that are most commonly used throughout the scripts.

# Mysql

def mysql(commands, auth = False, root_pass = None):
  r = []
  q = 'mysql'
  if auth:
    q = q + (" -uroot -p%s" % (root_pass))
  if type(commands) is not type(''):
    for command in commands:
      s = '%s -e "%s"' % (q, command)
      os.system(s)
      r.append(s)
  else:
    s = '%s -e "%s"' % (q, commands)
    os.system(s)
    r.append(s)
  return r

# Replace 

def replace(path, r_dict):
  data = None
  with open(path, 'r') as f:
    data = f.read()
  for key, value in r_dict.items():
    data = data.replace(key, value)
  with open(path, 'w') as f:
    f.write(data)
