import os
import types
from getpass import getpass

from libs.engines import mysql

# LNMP Stack

def LNMP(sys, root_pass=None):
  if not root_pass:
    root_pass = getpass("What pass would you like to use for mysql root account?: ")
  stack = (nginx, meriadb, php)
  for block in stack:
    if block is mysql:
      block(root_pass)
    else:
      block()
  yum_engine(config['add_packages'])
  port_engine(LAMP)

def nginx(sys):
  install_repo(sys)
  os.install('nginx')

def meriadb(root_pass):
  services = ('mysql-server',)
  yum_engine(services)
  os.system("service mysqld start")
  mysql_secure(root_pass)

def php():
  services = ('php', 'php-mysql',)
  yum_engine(services)

def install_repo(sys):
  if sys.distro == 'centos':
    path = '/etc/yum.repos.d/nginx.repo'
    sys.system("touch %s" % path)
    with open(path, 'a') as f:
      f.write(
        '[nginx]\n'
        'name=nginx repo\n'
        'baseurl=http://nginx.org/packages/mainline/{distro}/{version}/$basearch/\n'
        'gpgcheck=0\n'
        'enabled=1'.format(distro = sys.distro, version = sys.version[0]))
    f.close()
  elif (sys.distro == 'Ubuntu' or sys.distro == 'Debian'):
    sys.system('wget http://nginx.org/keys/nginx_signing.key '
               '&& apt-key add nginx_signing.key')
    path = '/etc/apt/sources.list'
    with open(path, 'a') as f:
      string = (
          """
          deb http://nginx.org/packages/mainline/{distro}/ {flavor} nginx
          deb-src http://nginx.org/packages/mainline/{distro}/ {flavor} nginx
          """.format(distro = sys.distro.lower(), flavor = sys.flavor))
      f.write(string)
    f.close()
    sys.system('apt-get update')

# Joomla

# PrestaShop

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
  mysql(secure_list)
