import os
import zipfile

os.system('cd /opt && curl -LOk https://github.com/Skullmaker90/PyInstall/archive/dev.zip')
with zipfile.ZipFile('dev.zip', 'r') as z:
  z.extractall()
os.system('python /opt/PyInstall-dev/main.py')
