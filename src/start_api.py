import subprocess
import os
from random import randrange

class BlenderInstance():
    SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
    # BLENDER_SCRIPT = "shaderverse/api/shaderverse_blender.py"
    BLEND_FILE = "C:\\Users\\goldm\\Downloads\\Telegram Desktop\dumpster-8.0.5.blend"
    BLENDER_SCRIPT = "shaderverse/api/blender_service.py"
    # BLENDER_SCRIPT = "bpy_context.py"

    blender_script_abs_path = os.path.join(SCRIPT_PATH, BLENDER_SCRIPT)

    def __init__(self):
        self.port = randrange(8118, 38118)
        command = ["blender", self.BLEND_FILE, "--factory-startup", "--background", "--addons", "shaderverse", "--python", self.blender_script_abs_path, "--", "--port", str(self.port)]
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
                                            