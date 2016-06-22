import os
from ast import literal_eval

from panelInstall import cPanel, Plesk, Webmin
from cmsInstall import LNMP, wordpress
from libs.libs import fqdn_check
from libs.systems import SysBase

# Main

def main():
  conf_path = './docs/default.cfg'
  sys = SysBase(conf_path)
  print("Please select an option to install.\n")
  options = [['cPanel', '1', cPanel], 
             ['Plesk', '2', Plesk],
             ['Webmin', '3', Webmin],
             ['LNMP Stack', '4', LNMP],
             ['Wordpress', '5', wordpress]]
  display = ''
  for opt in options:
    display = display + ('%s :: %s\n' % (opt[0], opt[1]))
  print display
  choice = int(raw_input("Choice: "))
  if 1 <= choice <= (len(options)):
    fqdn_check(sys.conf['core'])
    sys.update()
    options[choice-1][2](sys)
  else:
    print("Please select a valid menu option.\n\n\n")
    main()

main()
