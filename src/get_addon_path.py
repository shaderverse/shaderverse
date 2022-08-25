import bpy
import addon_utils
import pathlib 

for mod in addon_utils.modules():
    if mod.bl_info['name'] == "Shaderverse":
        filepath = mod.__file__
        print (pathlib.Path(filepath).parent)
    else:
        pass