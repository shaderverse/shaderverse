from audioop import add
from distutils.log import error
import subprocess
import os 
import shutil
from pathlib import Path

def get_addon_path() -> str:
    calling_output = subprocess.check_output(['blender','-b','-P','get_addon_path.py'])
    addon_path = calling_output.decode('utf-8')
    addon_path = addon_path.split("\n")
    addon_path = addon_path[0].replace("\r","")
    return addon_path


addon_path = Path(get_addon_path())

if (addon_path):
    try:
        print(addon_path)
        shutil.rmtree(addon_path)
        print("Removed existing Shaderverse add-on")
    except:
        print(error.__str__())
        print("No add-on directory to delete")
    
    try: 
        shutil.copytree("shaderverse", addon_path, symlinks=True,
                      ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
        print("Refreshed Shaderverse add-on")
    except:
        print("Couldn't copy add-on to location")

