import re
import subprocess
import sys
import platform

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

    result = subprocess.run([python_path, "-m", "pip", "install", *required], capture_output=True)



    
if __name__ == "__main__":
    install_modules()
