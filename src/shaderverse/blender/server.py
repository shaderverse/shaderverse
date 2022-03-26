import os
import subprocess
import sys
import bpy
from shaderverse.fastapi import controller


# class FastApiProcess():

#     data = None
#     process = None
#     error = None
#     output = None

#     def __init__(self):
#         addon_file = os.path.realpath(__file__)
#         addon_dir = os.path.dirname(addon_file)
#         self.script_path = os.path.join(addon_dir, "fastapi/app.py")


#     def start(self):
#         """ Start the process """
#         self.process = subprocess.Popen([sys.executable, self.script_path], stderr=self.error, stdout=self.output, shell=True)

#         self.running = True


#     def stop(self):
#         """ Stop the process """
#         self.process.kill()
#         self.running = False

def init_fastapi():
    # global fastapi
    # fastapi = FastApiProcess()
    # fastapi.start()
    print(bpy.app.version)
    controller.start()

def kill_fastapi():
    # global fastapi
    # fastapi = FastApiProcess()
    # fastapi.start()
    controller.proxy.process.kill()

if __name__ == "__main__":
    init_fastapi()
