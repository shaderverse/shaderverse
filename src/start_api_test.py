import subprocess
import os
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
# BLENDER_SCRIPT = "shaderverse/api/shaderverse_blender.py"
BLEND_FILE = "C:\\Users\\goldm\\Downloads\\chibies-mixamo-1.4.0.1.blend"
# BLENDER_SCRIPT = "shaderverse/api/blender_service.py"
BLENDER_SCRIPT = "bpy_context.py"

blender_script_abs_path = os.path.join(SCRIPT_PATH, BLENDER_SCRIPT)



port = "8119"

command = ["blender", "--factory-startup", "--background", "--addons", "shaderverse", "--python", blender_script_abs_path, "--", "--port", port]
process = subprocess.Popen(command, shell=True)
