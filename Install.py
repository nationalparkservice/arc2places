from __future__ import print_function
import sys
import os
import subprocess

"""
Installs pip and prerequisites for arc2places
"""

if os.name != 'nt':
    print('This script only works on Windows')
    sys.exit()

python_path = sys.executable
if sys.version_info.major == 3:
    print('You are using Python 3.4 (ArcGIS Pro).  Looking for Python 2.7.')

    drive, tail = os.path.splitdrive(python_path)
    path = drive + r'\Python27'
    exes = [os.path.join(path, d, 'python.exe') for d in os.listdir(path) if os.path.exists(os.path.join(path, d, 'python.exe'))]
    if len(exes) > 1:
        print('You have multiple versions of python 2.7 installed {0:s}.'.format(exes))
        print('You must pick the one that matches the version of ArcGIS you are using.')
        print('The installer is not prepared for this configuration, contact regan_sarwas@nps.gov for assistance.')
        sys.exit()
    if len(exes) < 1:
        print('You have no versions of Python 2.7.  Installing for Python 3.4.')
        print('Arc2Places is not tested with ArcGIS Pro.  Sorry and Good Luck.')
    if len(exes) == 1:
        python_path = exes[0]
        print('Found Python 2.7 at {0:s}'.format(python_path))

getpip_path = os.path.join(os.path.dirname(__file__), 'get-pip.py')
if os.path.exists(getpip_path):
    print('found get-pip')
else:
    print('get-pip not found at {0:s}'.format(getpip_path))
pip_path = os.path.join(os.path.dirname(python_path), 'Scripts', 'pip.exe')
if os.path.exists(pip_path):
    print('Pip already exists')
    print('You can update it with')
    print(python_path, ' -m pip install -U pip')
else:
    print('Pip not found.')
    if not os.path.exists(getpip_path):
        print('and get-pip.py not found.')
        # TODO: download it from https://bootstrap.pypa.io/get-pip.py
        sys.exit()
    else:
        print('Installing pip ...')
        cmd = python_path + './get=pip.py'
        subprocess.call([python_path, getpip_path])
        if not os.path.exists(pip_path):
            print('Failed to install Pip')
            sys.exit()
print('Using', pip_path, 'to install requests_oauthlib')
subprocess.call([pip_path, 'install', 'requests_oauthlib'])
print('Done.')
print('If there were errors, please send them to regan_sarwas@nps.gov.')
