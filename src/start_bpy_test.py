import subprocess
import os
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
# BLENDER_SCRIPT = "shaderverse/api/shaderverse_blender.py"
BLEND_FILE = "C:\\Users\\goldm\\Downloads\\Telegram Desktop\dumpster-8.0.5.blend"
BLENDER_SCRIPT = "shaderverse/api/blender_service.py"

blender_script_abs_path = os.path.join(SCRIPT_PATH, BLENDER_SCRIPT)



port = "8119"

command = ["blender", "--factory-startup", "--background", BLEND_FILE, "--addons", "shaderverse", "--python", blender_script_abs_path, "--", "--port", port]
process = subprocess.Popen(command, shell=True)
