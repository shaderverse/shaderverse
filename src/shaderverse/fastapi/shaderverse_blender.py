import argparse
from email.charset import BASE64
import uvicorn
import os 
import json
import bpy
from fastapi import FastAPI, File
from shaderverse.fastapi.model import Metadata, Trait, GlbFile
from typing import List
import tempfile
import base64

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

app = FastAPI()

@app.post("/generate", response_model=Metadata)
async def generate():
    run_generate_operator = bpy.ops.shaderverse.generate()

    generated_metadata: List[Trait] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

    metadata = Metadata(
        filename=bpy.data.filepath,traits=generated_metadata)

    print(metadata)
    return metadata


def get_parent_node()->bpy.types.Object | None:
    for obj in bpy.data.objects:
        parent_node = None
        if hasattr(obj, "shaderverse"):
            if obj.shaderverse.is_parent_node:
                parent_node = obj
                break
    return parent_node

def reset_scene():
    for obj in bpy.data.objects:
        obj.hide_set(True)

def set_objects_to_active(object_list):
    for obj in object_list:   
        print("activating object: {}".format(obj))
        obj.hide_set(False)

def render_glb(object_name: str, glb_filename):
    reset_scene()
    parent_object = bpy.data.objects[object_name]
    object_children = parent_object.children
    object_list = []
    object_list.append(parent_object)
    object_list.extend(object_children)
    set_objects_to_active(object_list)
    bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='AUTO', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials='EXPORT', export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, export_selected=False, use_selection=False, use_visible=True, use_renderable=False, use_active_collection=False, export_extras=False, export_yup=True, export_apply=True, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=True, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=True, export_morph_normal=True, export_morph_tangent=False, export_lights=False, export_displacement=False, will_save_settings=True, filter_glob='*.glb;*.gltf')


@app.post("/glb", response_model=GlbFile)
async def generate():
    object_to_render = get_parent_node()
    # glb_temp_file = tempfile.NamedTemporaryFile()
    glb_temp_file = "c:\\blender\\tmp.glb"
    render_glb(object_to_render.name, glb_temp_file)

    print(glb_temp_file)
    # Open binary file for reading
    f = open(glb_temp_file, 'rb')

    # Get a string from binary file
    d = f.read()
    # print(d)


    # glb_bytes = base64.urlsafe_b64encode(glb_bytes)
    glb = GlbFile(buffer=f)


    return glb

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    parser.add_argument('--port', 
                        help='the port', 
                        default=8119)

    args, unknown = parser.parse_known_args()

    port = args.port

    uvicorn.run(app="shaderverse_blender:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=args.port)