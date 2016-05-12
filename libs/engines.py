import os
import types

# This file contains the engines that are most commonly used throughout the scripts.

# Mysql

def mysql(commands, auth=False, root_pass=None):
  q = 'mysql'
  if auth:
    q = q + (" -uroot --password='%s'" % (root_pass))
  for command in commands:
    os.system('%s -e "%s"' % (q, command))
