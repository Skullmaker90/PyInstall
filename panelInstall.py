import os
import platform
from libs.engines import system, Port_engine, yum

port = Port_engine(platform.dist()[1])

# Webmin

def Webmin(config):
  urls = config['dl_url']

  packages = ('wget', 'perl', 'perl-Net-SSLeay', 'openssl', 'perl-IO-Tty')
  yum(packages)
  for url in urls:
    os.system("wget %s" % (url))
  system("rpm --import jcameron-key.asc")
  system("rpm -Uvh webmin-*.rpm")
  port((10000,))

# cPanel

def cPanel(config):
  url = config['dl_url']
  system("yum install -y perl gcc")
  os.chdir(config['dl_path'])
  system("curl -o latest -L %s && sh latest" % (url))

# Plesk

def Plesk(config):
  url = config['dl_url']
  release = config['release']
  build = ('cd %s && curl -O %s && sh plesk-installer ' % (config['dl_path'], url) +
           '--select-product-id plesk ' +
           '--select-release-%s ' % (release) +
           '--installation-type Full ' +
           '--notify-email service@cari.net')
  system(build)
  port((8443, 8447))
