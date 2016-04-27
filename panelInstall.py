import os
import socket
import fcntl
import struct
import tarfile
import types
import ConfigParser
from getpass import getpass

parser = ConfigParser.ConfigParser()
parser.read('default-config.cfg')

class ConfigOptions(object):
  def __init__(self, parserObj):
    self.conf_dict = {}
    self._populate(parserObj)

  def _populate (self, parserObj):
    for item in parserObj.items('default'):
      self.conf_dict[item[0]] = item[1]

  def __call__(self, key):
    return self.conf_dict[key]

config = ConfigOptions(parser)

# cPanel

def cPanel():
  url = 'https://securedownloads.cpanel.net/latest'
  os.system("yum install -y perl gcc")
  os.chdir(config('dl_path'))
  os.system("curl -o latest -L %s && sh latest" % (url))

# Plesk

def plesk():
  url = 'http://autoinstall.plesk.com/plesk-installer'
  release = 'plesk'
  build = ('cd /home && wget %s && sh plesk-installer ' % (url) +
           '--select-product-id %s ' % (release) +
           '--select-release-latest' +
           '--installation-type Full ' +
           '--notify-email service@cari.net')
  os.system(build)
  port_engine(plesk)

# LAMP Stack

def LAMP(root_pass=None):
  if not root_pass:
    root_pass = getpass("What pass would you like to use for mysql root account?: ")
  stack = (apache, mysql, php)
  for block in stack:
    if block is mysql:
      block(root_pass)
    else:
      block()

def apache():
  services = ('httpd',)
  yum_engine(services)

def mysql(root_pass):
  services = ('mysql-server',)
  yum_engine(services)
  os.system("service mysqld start")
  mysql_secure(root_pass)

def php():
  services = ('php', 'php-mysql',)
  yum_engine(services)

def yum_engine(services):
  for s in services:
    os.system('yum install -y %s' % (s))

# Wordpress

def wordpress():
  url = 'http://wordpress.org/latest.tar.gz'
  root_pass = getpass("Please choose a password for the ROOT MySQL user: ")
  wp_pass = getpass("Please choose a password for the Wordpress MySQL user: ")
  LAMP(root_pass)
  get_wordpress(url)
  set_database(root_pass, wp_pass)
  set_config(wp_pass)
  os.system("cp -r /home/wordpress/* /var/www/html")
  yum_engine(('php-gd',))
  os.system('touch /var/www/html/.htaccess')
  with open('/var/www/html/.htaccess', 'r+') as f:
    f.write('DirectoryIndex index.php index.htm')
  port_engine(wordpress)
  os.system("service httpd restart")
  
def get_wordpress(url):
  os.system("cd %s && wget %s" % (config('dl_path'), url))
  tar = tarfile.open('/home/latest.tar.gz')
  tar.extractall(path=config('wp_extract_path'))

def set_database(root_pass, wp_pass):
  comm_list = ("CREATE DATABASE wordpress",
		"CREATE USER 'wp_user'@'localhost'",
		"SET PASSWORD FOR 'wp_user'@'localhost' = PASSWORD('%s')" % (wp_pass),
		"GRANT ALL PRIVILEGES ON wordpress.* TO 'wp_user'@'localhost' IDENTIFIED BY '%s'" % (wp_pass),
		"FLUSH PRIVILEGES")
  mysql_bash_engine(comm_list, auth=True, root_pass=root_pass)

def set_config(wp_pass):
  path = config('wp_extract_path') + '/wordpress'
  settings = {'database_name_here': config('wp_database'), 
		'username_here': config('wp_user'),
		'password_here': wp_pass}
  os.system("cp %s/wp-config-sample.php %s/wp-config.php" % (path, path))
  replace_engine(path + '/wp-config.php', settings)

def replace_engine(path, r_dict):
  data = None
  with open(path, 'r') as f:
    data = f.read()
  for key, value in r_dict.items():
    data = data.replace(key, value)
  with open(path, 'w') as f:
    f.write(data)

# MySQL Secure Install

def mysql_secure(root_pass):
  hname = get_info()[1]
  secure_list = ("UPDATE mysql.user SET Password = PASSWORD('%s') WHERE User = 'root'" % (root_pass),
		 "DROP USER ''@'localhost'",
		 "DROP USER ''@'%s'" % (hname),
		 "DROP DATABASE test",
		 "FLUSH PRIVILEGES")
  mysql_bash_engine(secure_list)

def mysql_bash_engine(commands, auth=False, root_pass=None):
  q = 'mysql'
  if auth:
    q = q + (" -uroot --password='%s'" % (root_pass))
  for command in commands:
    os.system('%s -e "%s"' % (q, command))

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

def fqdn_check():
  info = get_info()
  if os.stat(info[0]).st_size <= 158:
    if (config('fqdn_hostname') == 'default') and (config('fqdn_ip') == 'default'):
      populate(info[0], info[1], info[2])
    else:
      populate(info[0], config('fqdn_hostname'), config('fqdn_ip'))

def get_ip(ifname):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return socket.inet_ntoa(fcntl.ioctl(
    s.fileno(),
    0x8915, # SIOCGIFADDR
    struct.pack('256s', ifname[:15])
  )[20:24])

# Main

def main():
  print("Please select an option to install.\n")
  options = [['cPanel', '1', cPanel], 
             ['Plesk', '2', plesk], 
             ['LAMP Stack', '3', LAMP], 
             ['Wordpress', '4', wordpress]]
  display = ''
  for opt in options:
    display = display + ('%s :: %s\n' % (opt[0], opt[1]))
  print display
  choice = int(raw_input("Choice: "))
  if 1 <= choice <= (len(options)):
    fqdn_check()
    yum_engine(('wget',))
    options[choice-1][2]()
  else:
    print("Please select a valid menu option.\n\n\n")
    main()

main()
