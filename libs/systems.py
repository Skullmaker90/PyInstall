import os
import platform
from subprocess import check_call

class SysBase(object):
  distro, version, flavor = platform.dist()
  def __init__(self):
#    self.distro, self.version, self.flavor = platform.dist()
    self.pkg_cmd = None
    self._set_cmd()

  def _set_cmd(self):
    pkg_mgrs = {'centos': 'yum', 'Ubuntu': 'apt-get'}
    self.pkg_cmd = [pkg_mgrs[self.distro], 'install', '-y']

  def install(self, *pkgs):
    cmd = self.pkg_cmd[:]
    for pkg in pkgs:
      cmd.append(pkg)
    check_call(cmd)

class Centos(SysBase):
  pass

class Ubuntu(SysBase):
  pass
    
__name__ = 'SystemConfigClasses'
