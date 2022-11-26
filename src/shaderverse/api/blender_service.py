import argparse
import uvicorn
import os 
import json
from fastapi import Depends, FastAPI, File, BackgroundTasks, Request, Response
from shaderverse.model import Metadata, Trait, RenderedResults
from shaderverse.api.model import SessionData, SessionStatus, RenderedFile
from typing import Generator, List
import tempfile
import base64
import sys
from shaderverse.nft import NFT
from shaderverse.api import deps
import bpy
# import ray
# from ray import serve
from fastapi.responses import FileResponse
import asyncio
from fastapi.routing import APIRoute

from typing import Callable
from uuid import uuid4

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

rendered_files: List[RenderedFile] = []

# class CustomRoute(APIRoute):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.lock = asyncio.Lock()

#     def get_route_handler(self) -> Callable:
#         original_route_handler = super().get_route_handler()

#         async def custom_route_handler(request: Request) -> Response:
#             await self.lock.acquire()
#             response: Response = await original_route_handler(request)
#             self.lock.release()
#             return response

#         return custom_route_handler


app = FastAPI()
# app.router.route_class = CustomRoute
# session = SessionData()


# def set_scene():
#     window = get_context_window()
#     print(window)
#     print(window.scene)
#     window.scene = bpy.data.scenes[0]


# def get_parent_node()->bpy.types.Object | None:
#     for obj in bpy.data.objects:
#         parent_node = None
#         if hasattr(obj, "shaderverse"):
#             if obj.shaderverse.is_parent_node:
#                 parent_node = obj
#                 break
#     return parent_node

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

def run_generator(nft: NFT):
    nft.run_pre_generation_script()
    nft.create_animated_objects_collection()
    nft.reset_animated_objects()
    nft.run_metadata_generator()
    nft.run_post_generation_script()


# def get_context_window():
#     for window in bpy.data.window_managers['WinMan'].windows:   
#         if window:
#             print("window found")
#             return window
#     return None



def export_glb_file(glb_filename: str):
        bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='JPEG', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials='EXPORT', export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, use_selection=False, use_visible=True, use_renderable=True, use_active_collection=False, export_extras=False, export_yup=True, export_apply=True, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=False, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=False, export_morph_normal=True, export_morph_tangent=False, export_lights=False)

# @app.on_event("startup")
# async def startup_event():
#     BLEND_FILE = "C:\\Users\\goldm\\Downloads\\chibies-mixamo-1.4.0.1.blend"
#     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)


@app.post("/generate", response_model=Metadata)
async def generate(nft: NFT = Depends(deps.get_nft)):
    print(bpy.context.active_object.name)
    print("NFT attributes before running generator")
    print(nft.attributes)
    run_generator(nft)
    print(bpy.context.active_object.name)
    # nft.run_pre_generation_script()
    # nft.create_animated_objects_collection()
    # nft.reset_animated_objects()
    # nft.run_metadata_generator()

    print("NFT attributes after running generator")
    print(nft.attributes)

    generated_metadata: List[Trait] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

    metadata = Metadata(
        filename=bpy.data.filepath,traits=generated_metadata)


    print("NFT metadata")
    print(metadata)
    print("reverting file")
    # bpy.ops.wm.revert_mainfile()

    return metadata

def set_active_object(object_ref):
    bpy.context.view_layer.objects.active = object_ref
    

class GlbResponse(FileResponse):
    media_type = "model/gltf-binary"

async def handle_rendering(nft):
    nft.update_geonodes_from_metadata()
    nft.make_animated_objects_visible()
    bpy.ops.shaderverse.realize()

    generated_metadata: List[Trait] = json.loads(bpy.context.scene.shaderverse.generated_metadata)
    metadata = Metadata(
        filename=bpy.data.filepath,traits=generated_metadata)


    temp_dir_name = tempfile.mkdtemp(prefix='shaderverse_')
    temp_file_name = f"{next(tempfile._get_candidate_names())}.glb"
    glb_temp_file_name = os.path.join(temp_dir_name,temp_file_name)
    export_glb_file(glb_temp_file_name)


    rendered_file = RenderedFile(id=uuid4(),file_path=glb_temp_file_name)
    # print(rendered_file)

    rendered_files.append(rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()
    return rendered_file

async def make_glb_response(rendered_file: RenderedFile):
    return GlbResponse(rendered_file.file_path,media_type="model/gltf-binary")

@app.post("/render_glb", response_class=GlbResponse)
async def render_glb(nft: NFT = Depends(deps.get_nft)):
    run_generator(nft)
    rendered_file = await handle_rendering(nft)
  
    
    
    return GlbResponse(rendered_file.file_path,media_type="model/gltf-binary")

    # return file_response




def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    parser.add_argument('--port', 
                        help='the port', 
                        dest='port', type=float, required=False,
                        default=8119)
    
    # parser.add_argument('--blend_file', 
    #                     help='the blend file', 
    #                     dest='blend_file', required=True
    #                     )
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

# @serve.deployment(route_prefix="/")
# @serve.ingress(app)
# class FastAPIWrapper:
#     pass

if __name__ == "__main__":
    args = get_args()


    # serve.run(FastAPIWrapper.bind())

    uvicorn.run(app="blender_service:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=args.port)