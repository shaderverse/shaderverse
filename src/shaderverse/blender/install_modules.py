import re
import subprocess
import sys
import platform
import bpy
from  ..background.process import Process
from ..background.installer_process import Installer
from ..config.binaries import binary_list

process_list: list[Process] = []
install_modules_completed:bool = False

# add process for the pip install
process_list.append(Process())

for binary in binary_list:
    # add installer process for each binary to download
    process_list.append(Installer(binary.binary_name, binary.urls.windows, binary.urls.macosx64, binary.urls.macossilicon, binary.urls.linux, binary.files.windows, binary.files.macosx64, binary.files.macossilicon, binary.files.linux ))

def handle_module_install_process():
    """Check the module install process every second and reload the scrips if completed"""
    all_completed = True
    global install_modules_completed
    for process in process_list:
        print(f"Command: {process.cmd}")
        print(f"Result: {process.result}")
        print(f"Status: {process.status}")
        if process.status != "completed":
            all_completed = False
    if all_completed:
        install_modules_completed = True
        print("Modules installed")
        # bpy.context.scene.shaderverse.is_modules_installed = True
        bpy.context.preferences.addons["shaderverse"].preferences.modules_installed = True
        bpy.ops.script.reload()
        return None
    return 1.0

def install_modules():
    python_path = sys.executable

    required = {'psutil', 'uvicorn[standard]', 'fastapi', 'pydantic', 'pyngrok', 'celery', 'httpx', 'sqlalchemy==1.4.48'}

    # subprocess.run([python_path, "-m", "ensurepip"], capture_output=True)
    # subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip",])
    cmd = [python_path, "-m", "pip", "install", *required]
    process_list[0].cmd = cmd
    bpy.app.timers.register(handle_module_install_process)
    print("Installing modules...")
    for process in process_list:
        process.execute()
    
if __name__ == "__main__":
    install_modules()
