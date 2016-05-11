import os

# Webmin

def Webmin(sys):
  conf = sys.conf['Webmin']
  urls = conf['dl_url']
  packages = ('wget', 'perl', 'perl-Net-SSLeay', 'openssl', 'perl-IO-Tty')
  sys.install(*packages)
  for url in urls:
    sh.append("wget %s" % url)
  sh.append("rpm --import jcameron-key.asc",
            "rpm --Uvh webmin-*.rpm")
  sys.system(*sh)
  sys.port(10000)

# cPanel

def cPanel(sys):
  conf = sys.conf['cPanel']
  url = conf['dl_url']
  pkgs = ('perl, gcc')
  sys.install(*pkgs)
  os.chdir(conf['dl_path'])
  sys.system("curl -o latest -L %s && sh latest" % (url))

# Plesk

def Plesk(sys):
  conf = sys.conf['Plesk']
  build = ('cd %s && curl -O %s && sh plesk-installer ' % (conf['dl_path'], conf['dl_url']) +
           '--select-product-id plesk ' +
           '--select-release-%s ' % conf['release'] +
           '--installation-type Full ' +
           '--notify-email service@cari.net')
  sys.system(build)
  sys.port(*[8443, 8447])
