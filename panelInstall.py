import os
import socket
import fcntl
import struct
import tarfile
from getpass import getpass

# cPanel

def cPanel():
  url = 'https://securedownloads.cpanel.net/latest'
  path = '/home'
  os.system("yum install -y perl gcc")
  os.chdir(path)
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
  os.system("iptables -I INPUT 2 -p tcp --dport 8443 -j ACCEPT")

# LAMP Stack

def LAMP():
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
  ex_path = '/home'
  wp_pass = getpass("Please choose a password for the Wordpress MySQL user: ")
  LAMP()
  get_wordpress(url, ex_path)
  set_database(wp_pass)
  set_config(wp_pass)
  os.system("cp -r /home/wordpress/* /var/www/html")
  yum_engine(('php-gd',))
  os.system('touch /var/www/html/.htaccess')
  with open('/var/www/html/.htaccess', 'r+') as f:
    f.write('DirectoryIndex index.php index.htm')
  os.system('iptables -I INPUT 3 -p tcp --dport 80 -j ACCEPT')
  os.system("service httpd restart")
  
def get_wordpress(url, ex_path):
  os.system("cd /home && wget %s" % (url))
  tar = tarfile.open('/home/latest.tar.gz')
  tar.extractall(path=ex_path)

def set_database(wp_pass):
  comm_list = ("CREATE DATABASE wordpress",
		"CREATE USER 'wp_user'@'localhost'",
		"SET PASSWORD FOR 'wp_user'@'localhost' = PASSWORD('%s')" % (wp_pass),
		"GRANT ALL PRIVILEGES ON wordpress.* TO 'wp_user'@'localhost' IDENTIFIED BY '%s'" % (wp_pass),
		"FLUSH PRIVILEGES")
  mysql_bash_engine(comm_list, auth=True, wp_pass=wp_pass)

def set_config(wp_pass):
  path = '/home/wordpress'
  settings = {'database_name_here': 'wordpress', 
		'username_here': 'wp_user',
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

def mysql_bash_engine(commands, auth=False, wp_pass=None):
  q = 'mysql'
  if auth:
    q = q + (" -uroot --password='%s'" % (wp_pass))
  for command in commands:
    os.system('%s -e "%s"' % (q, command))

# Networking

def port_engine(service):
  service_ports = {plesk: ['8443'], LAMP: ['80'], wordpress: ['80']}
  if type(service) == types.FunctionType:
    for port in service_ports[service]:
      os.system('iptables -I INPUT -p tcp --dport %s -j ACCEPT' % (port))

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
    populate(info[0], info[1], info[2])

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
