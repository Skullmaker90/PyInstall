import os
from ast import literal_eval

from panelInstall import cPanel, Plesk, Webmin
from libs.libs import fqdn_check
from libs.engines import system

def readConfig(path):
  with open(path, 'r') as f:
    config = literal_eval(f.read())
    return config

class Config(object):
  def __init__(self, path, service):
    self.Core = None
    self.Service = None
    self._populate(path, service)

  def _populate(self, path, service):
    self.Core = readConfig(path, 'core')
    self.Service = readConfig(path, service)

# Main

def main():
  conf_path = './default.cfg'
  print("Please select an option to install.\n")
  options = [['cPanel', '1', cPanel], 
             ['Plesk', '2', Plesk],
             ['Webmin', '3', Webmin]]
  display = ''
  for opt in options:
    display = display + ('%s :: %s\n' % (opt[0], opt[1]))
  print display
  choice = int(raw_input("Choice: "))
  if 1 <= choice <= (len(options)):
    config = Config(conf_path, options[choice-1][0])
    fqdn_check(config.Core)
    system('yum update -y')
    options[choice-1][2](config.Service)
  else:
    print("Please select a valid menu option.\n\n\n")
    main()

main()
