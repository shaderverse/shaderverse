import os
import sys
import site

BPY_SYS_PATH = list(sys.path) # Make instance of `bpy`'s modified sys.path
BPY_USER_BASE = site.USER_BASE
BPY_SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

bl_info = {
  "name": "Shaderverse",
  "description": "Create generative art collections using Geometry Nodes",
  "author": "Michael Gold",
  "version": (1, 1, 1, 1),
  "blender": (3, 1, 0),
  "location": "Object > Modifier",
  "warning": "",
  "doc_url": "Shaderverse",
  "tracker_url": "https://github.com/shaderverse/shaderverse",
  "support": "COMMUNITY",
  "category": "Generative Art"
}



import bpy
from . import blender

custom_icons = None



classes = [
    blender.SHADERVERSE_PG_restrictions_item,
    blender.SHADERVERSE_PG_main,
    blender.SHADERVERSE_PG_parent_node,
    blender.SHADERVERSE_PG_render,
    blender.SHADERVERSE_PG_scene,
    blender.SHADERVERSE_PG_preferences,
    blender.SHADERVERSE_PT_main,
    blender.SHADERVERSE_PT_preferences,
    blender.SHADERVERSE_PT_rarity,
    blender.SHADERVERSE_PT_metadata,
    blender.SHADERVERSE_PT_generated_metadata,
    blender.SHADERVERSE_PT_rendering,
    blender.SHADERVERSE_PT_batch,
    blender.SHADERVERSE_PT_settings,
    blender.SHADERVERSE_PT_restrictions,
    blender.SHADERVERSE_UL_restrictions,
    blender.SHADERVERSE_OT_restrictions_new_item,
    blender.SHADERVERSE_OT_restrictions_delete_item,
    blender.SHADERVERSE_OT_restrictions_move_item,
    blender.SHADERVERSE_OT_generate,
    blender.SHADERVERSE_OT_realize,
    blender.SHADERVERSE_OT_live_preview,
    blender.SHADERVERSE_OT_stop_live_preview,
    blender.SHADERVERSE_OT_install_modules,
    blender.SHADERVERSE_OT_render,
    blender.SHADERVERSE_OT_start_api,
    blender.SHADERVERSE_OT_stop_api
]

def register():
    blender.handle_adding_sites_to_path()

    import bpy.utils.previews
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    addon_path =  os.path.dirname(__file__)
    icons_dir = os.path.join(addon_path, "blender/icons")
    
    custom_icons.load("shaderverse_icon", os.path.join(icons_dir, "icon.png"), 'IMAGE')


    for this_class in classes:
        bpy.utils.register_class(this_class)

    #adds the property group class to the object context (instantiates it)
    bpy.types.Object.shaderverse = bpy.props.PointerProperty(type=blender.SHADERVERSE_PG_main)
    bpy.types.Scene.shaderverse = bpy.props.PointerProperty(type=blender.SHADERVERSE_PG_scene)

    blender.SHADERVERSE_OT_install_modules.first_install()



#same as register but backwards, deleting references
def unregister():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    #delete the custom property pointer
    #NOTE: this is different from its accessor, as that is a read/write only
    #to delete this we have to delete its pointer, just like how we added it
    del bpy.types.Object.shaderverse 
    del bpy.types.Scene.shaderverse

    for this_class in classes:
        bpy.utils.unregister_class(this_class)  

#a quick line to autorun the script from the text editor when we hit 'run script'
if __name__ == '__main__':
    register()

