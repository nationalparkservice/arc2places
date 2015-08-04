from __future__ import print_function
import sys
import os
import subprocess

if os.name != 'nt':
    print('This script only works on Windows')
    sys.exit()

if sys.version_info.major == 3:
    print('find python 2.7 or make sure everything works with python 3')

getpip_path = os.path.join(os.path.dirname(__file__), 'get-pip.py')
pip_path = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'pip.exe')
if os.path.exists(pip_path):
    print('Pip already exists')
    print('You can update it with')
    print(sys.executable, ' -m pip install -U pip')
else:
    print('Pip not found.')
    if not os.path.exists(getpip_path):
        print('and get-pip.py not found.')
        # TODO: download it from https://bootstrap.pypa.io/get-pip.py
        sys.exit()
    else:
        print('Installing...')
        cmd = sys.executable + './get=pip.py'
        subprocess.call([sys.executable, getpip_path])
        if not os.path.exists(pip_path):
            print('Failed to install Pip')
            sys.exit()
print('Using', pip_path,'to install requests_oauthlib')
subprocess.call([pip_path, 'install', 'requests_oauthlib'])
