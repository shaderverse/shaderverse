import re
import subprocess
import sys
import platform
import bpy
from  ..background.process import Process

process = Process()

def handle_module_install_process():
    """Check the module install process every second and reload the scrips if completed"""
    print(f"Result: {process.result}")
    print(f"Status: {process.status}")
    if process.status == "completed":
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
    process.cmd = cmd
    bpy.app.timers.register(handle_module_install_process)
    process.execute()
    print("Installing modules...")
    # print(f"Result: {process.result}")
    
if __name__ == "__main__":
    install_modules()
