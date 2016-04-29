import os
import zipfile

os.system('cd /opt && curl -O https://github.com/Skullmaker90/PyInstall/archive/master.zip')
z = zipfile.ZipFile('/opt/master.zip')
z.extractall()
os.system('python /opt/PyInstall-master/main.py')
