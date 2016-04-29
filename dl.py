import os
import zipfile

os.system('cd /opt && curl -LOk https://github.com/Skullmaker90/PyInstall/archive/dev.zip')
z = zipfile.ZipFile('dev.zip', 'r')
z.extractall()
z.close()
os.system('mv -f PyInstall-dev/* ./')
os.system('python main.py')
