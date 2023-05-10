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
        bpy.ops.script.reload()
        return None
    return 1.0

def install_modules():
    python_path = sys.executable
    required = {'uvicorn[standard]', 'fastapi', 'pydantic', 'pyngrok', 'psutil', 'celery', 'httpx', 'sqlalchemy==1.4.48'}

    # subprocess.run([python_path, "-m", "ensurepip"], capture_output=True)
    # subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip",])

    # install direct ray[serve] whl for the detected os
    # match platform.system():
    #     case "Windows":
    #         required.add('ray[serve] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-2.0.0.dev0-cp310-cp310-win_amd64.whl')
    #     case "Linux":
    #         required.add('ray[serve] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-2.0.0.dev0-cp310-cp310-manylinux2014_x86_64.whl')
    #     case "Darwin":
    #         required.add('ray[serve] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-2.0.0.dev0-cp310-cp310-macosx_10_15_universal2.whl')
    cmd = [python_path, "-m", "pip", "install", *required]
    process.cmd = cmd
    bpy.app.timers.register(handle_module_install_process)
    process.execute()
    print("Installing modules...")
    print(f"Result: {process.result}")
    
if __name__ == "__main__":
    install_modules()
