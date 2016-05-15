import os
import types
import time
import tarfile
from getpass import getpass
from subprocess import Popen

from libs.engines import mysql, replace

# LNMP Stack

def LNMP(sys, root_pass=None):
  if not root_pass:
    root_pass = getpass("What pass would you like to use for mysql root account?: ")
  stack = (nginx, mariadb, php)
  for block in stack:
    if block is mariadb:
      block(root_pass, sys)
    else:
      block(sys)
  sys.port(80)

def nginx(sys):
  install_nginx_repo(sys)
  sys.install('nginx')
  sys.start('nginx')

def mariadb(root_pass, sys):
  install_mariadb_repo(sys)
  auth = False
  if sys.is_deb():
    Popen("debconf-set-selections <<< 'maria-db-server mysql-server/root_password password %s'" % root_pass,
          shell = True,
          executable = "bash")
    time.sleep(5)
    Popen("debconf-set-selections <<< 'maria-db-server mysql-server/root_password_again password %s'" % root_pass,
          shell = True,
          executable = "bash")
    auth = True
  sys.install('MariaDB-server')
  sys.start('mysql')
  mysql_secure(root_pass, sys, auth = auth)

def php(sys):
  if sys.is_deb():
    services = ('php5-fpm', 'php5-mysqlnd')
  else:
    services = ('php-fpm', 'php-mysql',)
  sys.install(*services)
  sys.start('php-fpm')
  sys.start('php5-fpm')

# Configuration Functions

def nginx_config(html_path, sys):
  nginx_rdict = {'{root}': html_path,
                 '{server_name}': sys.name}
  replace('./docs/nginx_default.conf', nginx_rdict)
  sys.system('mv ./docs/nginx_default.conf /etc/nginx/conf.d/default.conf')
  sys.system("service nginx restart")

def php_config(sys):
  php_rdict = {'/var/run/nginx.sock': '127.0.0.1:9000'}
  if sys.is_deb():
    path = '/etc/php'
  else:
    path = '/etc/php-fpm.d/www.conf'
  replace(path, php_rdict)
  service = 'php-fpm'
  if sys.is_deb():
    service = 'php5-fpm'
  sys.system('service %s restart' % service)


# Repo Installation

def install_mariadb_repo(sys):
  if sys.distro == 'centos':
    path = '/etc/yum.repos.d/mariadb.repo'
    sys.system('touch %s' % path)
    with open(path, 'a') as f:
      f.write(
        '[mariadb]\n'
        'name = MariaDB\n'
        'baseurl = http://yum.mariadb.org/10.1/{distro}{version}-amd64\n'
        'gpgkey = https://yum.mariadb.org/RPM-GPG-KEY-MariaDB\n'
        'gpgcheck = 0\n'
        'enabled = 1'.format(distro = sys.distro.lower(), version = sys.version[0]))
    f.close()
  elif sys.is_deb():
    sys.install('software-properties-common')
    sys_commands = ('apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db',
                    "add-apt-repository 'deb [arch=amd64,i386] "
                    "http://sfo1.mirrors.digitalocean.com"
                    "/mariadb/repo/10.1/{distro} {flavor} main'".format(distro = sys.distro.lower(), flavor = sys.flavor),
                    'apt-get update -y')
    for com in sys_commands:
      sys.system(com)

def install_nginx_repo(sys):
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
  elif sys.is_deb():
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

def wordpress(sys):
  wp_config = sys.conf['Wordpress']
  nginx_config = sys.conf['nginx']
  html_path = nginx_config['html_path']
  url = wp_config['dl_url']
  root_pass = getpass("Please choose a password for the ROOT MySQL user: ")
  wp_pass = getpass("Please choose a password for the Wordpress MySQL user: ")
  LNMP(sys, root_pass=root_pass)
  get_wordpress(url, wp_config['extract_path'])
  set_database(root_pass, wp_pass)
  set_config(wp_config['wp_user'], 
             wp_config['wp_database'], 
             wp_pass, 
             wp_config['extract_path'])
  os.system('cp -r %s/wordpress/* %s' % (wp_config['extract_path'], html_path))
  os.system('touch %s/.htaccess' % html_path)
  with open('%s/.htaccess' % html_path, 'r+') as f:
    f.write('DirectoryIndex index.php index.htm')
  nginx_config(html_path, sys)
  php_config(sys)
  sys.port(80)
  
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
  mysql(comm_list, auth=True, root_pass=root_pass)

def set_config(wp_user, wp_database, wp_pass, path):
  path = path + '/wordpress'
  settings = {'database_name_here': wp_database, 
		'username_here': wp_user,
		'password_here': wp_pass}
  os.system("cp %s/wp-config-sample.php %s/wp-config.php" % (path, path))
  replace(path + '/wp-config.php', settings)

# MySQL Secure Install

def mysql_secure(root_pass, sys, auth = False):
  secure_list = ("UPDATE mysql.user SET Password = PASSWORD('%s') WHERE User = 'root'" % (root_pass),
		 "DROP USER ''@'localhost'",
		 "DROP USER ''@'%s'" % (sys.name),
		 "DROP DATABASE test",
		 "FLUSH PRIVILEGES")
  mysql(secure_list, auth = auth, root_pass = root_pass)
