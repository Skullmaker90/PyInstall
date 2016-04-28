import os
import socket
import fcntl
import struct
import tarfile
import types
from ast import literal_eval
from getpass import getpass

def readConfig(path, service):
  with open(path, 'r') as f:
    config = literal_eval(f.read())
    return config[service]

# cPanel

def cPanel(config):
  url = config['dl_url']
  os.system("yum install -y perl gcc")
  os.chdir(config['dl_path'])
  os.system("curl -o latest -L %s && sh latest" % (url))

# Plesk

def plesk(config):
  url = config['dl_url']
  release = config['release']
  build = ('cd %s && wget %s && sh plesk-installer ' % (config['dl_path'], url) +
           '--select-product-id plesk ' +
           '--select-release-%s' % (release) +
           '--installation-type Full ' +
           '--notify-email service@cari.net')
  os.system(build)
  port_engine(plesk)

# LAMP Stack

def LAMP(config, root_pass=None):
  if not root_pass:
    root_pass = getpass("What pass would you like to use for mysql root account?: ")
  stack = (apache, mysql, php)
  for block in stack:
    if block is mysql:
      block(root_pass)
    else:
      block()
  yum_engine(config['add_packages'])
  port_engine(LAMP)

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

def yum_engine(packages):
  for package in packages:
    if package is not None:
      os.system('yum install -y %s' % (package))

# Wordpress

def wordpress(config):
  url = config['dl_url']
  root_pass = getpass("Please choose a password for the ROOT MySQL user: ")
  wp_pass = getpass("Please choose a password for the Wordpress MySQL user: ")
  LAMP(config, root_pass=root_pass)
  get_wordpress(url, config['extract_path'])
  set_database(root_pass, wp_pass)
  set_config(config['wp_user'], 
             config['wp_database'], 
             wp_pass, 
             config['extract_path'])
  os.system("cp -r /home/wordpress/* /var/www/html")
  os.system('touch /var/www/html/.htaccess')
  with open('/var/www/html/.htaccess', 'r+') as f:
    f.write('DirectoryIndex index.php index.htm')
  port_engine(wordpress)
  os.system("service httpd restart")
  
def get_wordpress(url, path):
  os.system("cd %s && wget %s" % (path, url))
  tar = tarfile.open('%s/latest.tar.gz' % (path))
  tar.extractall(path=path)

def set_database(root_pass, wp_pass):
  comm_list = ("CREATE DATABASE wordpress",
		"CREATE USER 'wp_user'@'localhost'",
		"SET PASSWORD FOR 'wp_user'@'localhost' = PASSWORD('%s')" % (wp_pass),
		"GRANT ALL PRIVILEGES ON wordpress.* TO 'wp_user'@'localhost' IDENTIFIED BY '%s'" % (wp_pass),
		"FLUSH PRIVILEGES")
  mysql_bash_engine(comm_list, auth=True, root_pass=root_pass)

def set_config(wp_user, wp_database, wp_pass, path):
  path = path + '/wordpress'
  settings = {'database_name_here': wp_database, 
		'username_here': wp_user,
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

# Main

def main():
  conf_path = './default.cfg'
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
    core_conf = readConfig(conf_path, 'core')
    service_conf = readConfig(conf_path, options[choice - 1][0])
    fqdn_check(core_conf)
    os.system('yum update -y && yum install -y wget')
    options[choice-1][2](service_conf)
  else:
    print("Please select a valid menu option.\n\n\n")
    main()

main()
