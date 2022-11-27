import argparse
from unicodedata import decimal
import uvicorn
import os 
import json
import bpy
from fastapi import FastAPI, File
from shaderverse.model import Metadata, Attributes, RenderedResults 
from shaderverse.api.model import SessionData, SessionStatus
from typing import List
import tempfile
import base64
import sys

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

app = FastAPI()
session = SessionData()

@app.post("/generate", response_model=Metadata)
async def generate():
    run_generate_operator = bpy.ops.shaderverse.generate()

    generated_metadata: List[Attributes] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

    metadata = Metadata(
        filename=bpy.data.filepath,attributes=generated_metadata)

    print(metadata)
    return metadata

@app.post("/session", response_model=SessionData)
async def get_session_data():
    return session



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

def get_export_materials_option()-> str:
    option = "EXPORT"
    if not bpy.context.scene.shaderverse.enable_materials_export:
        option = "NONE"
    return option

def render_glb(glb_filename: str):
    # reset_scene()
    # parent_object = bpy.data.objects[object_name]
    # # object_children = parent_object.children
    # # object_list = []
    # # object_list.append(parent_object)
    # # object_list.extend(object_children)
    # # set_objects_to_active(object_list)
    export_materials = get_export_materials_option()

    bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='JPEG', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials=export_materials, export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, export_selected=False, use_selection=False, use_visible=True, use_renderable=True, use_active_collection=False, export_extras=False, export_yup=True, export_apply=True, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=False, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=False, export_morph_normal=True, export_morph_tangent=False, export_lights=False, export_displacement=False, will_save_settings=True, filter_glob='*.glb;*.gltf')


@app.post("/glb", response_model=RenderedResults)
async def generate(batch: List[Metadata]):
    session.status = SessionStatus.running
    session.total_count = len(batch)
    # object_to_render = get_parent_node()
    # glb_temp_file = tempfile.NamedTemporaryFile()
    for count, metadata in enumerate(batch):
        session.current_count = count
        session.current_id = metadata.id
        metadata_dict = metadata.dict()
        traits_dict = metadata_dict["traits"]
        bpy.context.scene.shaderverse.generated_metadata = json.dumps(traits_dict)

    
        temp_dir_name = tempfile.mkdtemp(prefix='shaderverse_')
        temp_file_name = f"{next(tempfile._get_candidate_names())}.glb"
        glb_temp_file_name = os.path.join(temp_dir_name,temp_file_name)
        render_glb(glb_temp_file_name)

        print(glb_temp_file_name)
        
        print("In update")
        # Open binary file for reading
        f = open(glb_temp_file_name, 'rb')

        # Get a string from binary file
        d = f.read()

        # print(d)
        encoded_bytes = base64.urlsafe_b64encode(d)


        # glb_bytes = base64.urlsafe_b64encode(glb_bytes)
        glb = RenderedResults(buffer=encoded_bytes)


    return glb

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    parser.add_argument('--port', 
                        help='the port', 
                        dest='port', type=float, required=False,
                        default=8119)

    # args = parser.parse_args(sys.argv[sys.argv.index("--")+1:]) #read args past '--'
    
    python_args = sys.argv[sys.argv.index("--")+1:]
    args, unknown = parser.parse_known_args(args=python_args)
    return args

# def get_port() -> int:

#     # args = parser.parse_args(sys.argv[sys.argv.index("--")+1:]) #read args past '--'
#     args = sys.argv
#     port = args[args.index("--port")+1]
#     print(port)
#     return port


if __name__ == "__main__":
    args = get_args()

    uvicorn.run(app="shaderverse_blender:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=args.port)