import argparse
import uvicorn
import os 
import json
import requests
from fastapi import Depends, FastAPI, File, BackgroundTasks, Request, Response, HTTPException
from shaderverse.model import Metadata, Attribute, RenderedResults
from shaderverse.api.model import SessionData, SessionStatus, RenderedFile
from typing import Generator, List
import tempfile
import base64
import sys
from shaderverse.mesh import Mesh
from shaderverse.api import deps
from shaderverse import bl_info
import bpy
# import ray
# from ray import serve
from fastapi.responses import FileResponse, JSONResponse
import asyncio
from fastapi.routing import APIRoute

from typing import Callable
from uuid import uuid4
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

rendered_files: List[RenderedFile] = []

def get_shaderverse_version():
    version_tuple = bl_info["version"]
    version = ".".join([str(v) for v in version_tuple])
    return version

description = """
Shaderverse Asset Generation API helps you do awesome stuff. 🚀

## Geneate Metadata

You can **generate new json metadata** based on assets in the Blender project file.

## Render a GLB

You can **Render a GLB** from metadata json.

"""



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


# app = FastAPI()
# # app.router.route_class = CustomRoute
# # session = SessionData()


# # def set_scene():
# #     window = get_context_window()
# #     print(window)
# #     print(window.scene)
# #     window.scene = bpy.data.scenes[0]


# # def get_parent_node()->bpy.types.Object | None:
# #     for obj in bpy.data.objects:
# #         parent_node = None
# #         if hasattr(obj, "shaderverse"):
# #             if obj.shaderverse.is_parent_node:
# #                 parent_node = obj
# #                 break
# #     return parent_node

# def reset_scene():
#     for obj in bpy.data.objects:
#         obj.hide_set(True)

# def set_objects_to_active(object_list):
#     for obj in object_list:   
#         print("activating object: {}".format(obj))
#         obj.hide_set(False)

# def get_export_materials_option()-> str:
#     option = "EXPORT"
#     if not bpy.context.scene.shaderverse.enable_materials_export:
#         option = "NONE"
#     return option

# def run_generator(nft: NFT):
#     nft.run_pre_generation_script()
#     nft.create_animated_objects_collection()
#     nft.reset_animated_objects()
#     nft.run_metadata_generator()
#     nft.run_post_generation_script()


# # def get_context_window():
# #     for window in bpy.data.window_managers['WinMan'].windows:   
# #         if window:
# #             print("window found")
# #             return window
# #     return None



# def export_glb_file(glb_filename: str):
#         bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='JPEG', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials='EXPORT', export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, use_selection=False, use_visible=True, use_renderable=True, use_active_collection=False, export_extras=False, export_yup=True, export_apply=True, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=False, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=False, export_morph_normal=True, export_morph_tangent=False, export_lights=False)

# # @app.on_event("startup")
# # async def startup_event():
# #     BLEND_FILE = "C:\\Users\\goldm\\Downloads\\chibies-mixamo-1.4.0.1.blend"
# #     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)


# @app.post("/generate", response_model=Metadata)
# async def generate(nft: NFT = Depends(deps.get_nft)):
#     print(bpy.context.active_object.name)
#     print("NFT attributes before running generator")
#     print(nft.attributes)
#     run_generator(nft)
#     print(bpy.context.active_object.name)
#     # nft.run_pre_generation_script()
#     # nft.create_animated_objects_collection()
#     # nft.reset_animated_objects()
#     # nft.run_metadata_generator()

#     print("NFT attributes after running generator")
#     print(nft.attributes)

#     generated_metadata: List[Attribute] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

#     metadata = Metadata(
#         filename=bpy.data.filepath,attributes=generated_metadata)


#     print("NFT metadata")
#     print(metadata)
#     print("reverting file")
#     # bpy.ops.wm.revert_mainfile()

#     return metadata

# def set_active_object(object_ref):
#     bpy.context.view_layer.objects.active = object_ref
    

# class GlbResponse(FileResponse):
#     media_type = "model/gltf-binary"

# async def handle_rendering(nft):
#     nft.update_geonodes_from_metadata()
#     nft.make_animated_objects_visible()
#     bpy.ops.shaderverse.realize()

#     generated_metadata: List[Attribute] = json.loads(bpy.context.scene.shaderverse.generated_metadata)
#     metadata = Metadata(
#         filename=bpy.data.filepath,attributes=generated_metadata)


#     temp_dir_name = tempfile.mkdtemp(prefix='shaderverse_')
#     temp_file_name = f"{next(tempfile._get_candidate_names())}.glb"
#     glb_temp_file_name = os.path.join(temp_dir_name,temp_file_name)
#     export_glb_file(glb_temp_file_name)


#     rendered_file = RenderedFile(id=uuid4(),file_path=glb_temp_file_name)
#     # print(rendered_file)

#     rendered_files.append(rendered_file)
#     print("reverting file")
#     bpy.ops.wm.revert_mainfile()
#     return rendered_file

# async def make_glb_response(rendered_file: RenderedFile):
#     return GlbResponse(rendered_file.file_path,media_type="model/gltf-binary")

# @app.post("/render_glb", response_class=GlbResponse)
# async def render_glb(nft: NFT = Depends(deps.get_nft)):
#     run_generator(nft)
#     rendered_file = await handle_rendering(nft)
  
    
    
#     return GlbResponse(rendered_file.file_path,media_type="model/gltf-binary")

#     # return file_response

def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"



app = FastAPI(
    title="Shaderverse API",
    description=description,
    version=get_shaderverse_version(),
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Michael Gold",
        "url": "http://mike.gold",
        "email": "gold@shaderverse.com",
    },
    license_info={
        "name": "GPL-3.0 License",
        "url": "https://github.com/shaderverse/shaderverse/blob/main/LICENSEl",
    },
    generate_unique_id_function=custom_generate_unique_id
)

origins = [
    "http://shaderverse.com",
    "https://shaderverse.com",
    "http://localhost",
    "http://localhost:8118",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

def run_generator(mesh: Mesh):
    mesh.run_pre_generation_script()
    mesh.create_animated_objects_collection()
    mesh.reset_animated_objects()
    mesh.run_metadata_generator()
    mesh.run_post_generation_script()



async def export_glb_file(glb_filename: str):
        bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='AUTO', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials='EXPORT', export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, use_selection=False, use_visible=True, use_renderable=True, use_active_collection=False, export_extras=False, export_yup=True, export_apply=False, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=True, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=True, export_morph_normal=True, export_morph_tangent=False, export_lights=False, export_anim_single_armature=True)

# @app.on_event("startup")
# async def startup_event():
#     bpy.ops.preferences.addon_enable(module="shaderverse")
#     BLEND_FILE = os.environ.get("BLEND_FILE")
#     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

@app.on_event("shutdown")
async def shutdown_event():
    bpy.ops.wm.quit_blender()



@app.post("/generate", response_model=Metadata, tags=["generator"])
async def generate(mesh: Mesh = Depends(deps.get_mesh)):
    # print(bpy.context.active_object.name)
    print("NFT attributes before running generator")
    print(mesh.attributes)
    run_generator(mesh)
    # print(bpy.context.active_object.name)


    print("NFT attributes after running generator")
    print(mesh.attributes)

    generated_metadata: List[Attribute] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

    metadata = Metadata(
        filename=bpy.data.filepath,attributes=generated_metadata)

    print("NFT metadata")
    print(metadata)
    print("reverting file")
    # bpy.ops.wm.revert_mainfile()

    return metadata

def set_active_object(object_ref):
    bpy.context.view_layer.objects.active = object_ref
    

class GlbResponse(FileResponse):
    media_type = "model/gltf-binary"



@app.get("/rendered/{file_id}", response_class=FileResponse, tags=["download"])
def get_rendered_file(file_id: str):
    """Get a rendered file"""
    temp_dir = tempfile.gettempdir()
    file_path = Path(temp_dir, file_id)
    print(f"file_path: {file_path}")
    return FileResponse(str(file_path))


@app.get("/openapi", response_class=JSONResponse, tags=["download"])
def get_openapi_json(request: Request):
    """Reformat the OpenAPI JSON document"""
    openapi_url = f"{request.base_url}openapi.json"
    response = requests.get(openapi_url)
    openapi_content = json.loads(response.content)
    for path_data in openapi_content["paths"].values():
        for operation in path_data.values():
            tag = operation["tags"][0]
            operation_id = operation["operationId"]
            to_remove = f"{tag}-"
            new_operation_id = operation_id[len(to_remove) :]
            operation["operationId"] = new_operation_id
    return JSONResponse(openapi_content)

def generate_filepath(extension: str) -> str:
    """ Generate a temporary file path with the given extension"""
    temp_dir_name = tempfile.gettempdir()
    temp_file_name = f"{next(tempfile._get_candidate_names())}.{extension}"
    temp_file_path = os.path.join(temp_dir_name,temp_file_name)
    return temp_file_path

def set_object_visibility(mesh: Mesh):
    """ Set the visibility of all objects in the generated mesh to be visible"""
    objects = mesh.get_objects()

    for obj in objects:
        print(f"setting visibility of {obj.name} to visible")
        obj.hide_set(False)
        obj.hide_render = False
    

async def handle_rendering(mesh: Mesh):
    mesh.update_geonodes_from_metadata()
    # nft.make_animated_objects_visible()
    set_object_visibility(mesh)
    bpy.ops.shaderverse.realize() 
    
    
    generated_metadata: List[Attribute] = json.loads(bpy.context.scene.shaderverse.generated_metadata)
    metadata = Metadata(
        filename=bpy.data.filepath,attributes=generated_metadata)

    


    # rendered_file = RenderedFile(id=uuid4(),file_path=glb_temp_file_name)
    # print(rendered_file)



    # rendered_files.append(rendered_file)

    return (metadata)

async def make_glb_response(rendered_file: RenderedFile):
    return GlbResponse(rendered_file.file_path,media_type="model/gltf-binary")

@app.post("/render_glb", response_model=Metadata, tags=["render"])
async def render_glb(metadata: Metadata, background_task: BackgroundTasks, mesh: Mesh = Depends(deps.get_mesh)):
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata.dict()["attributes"])
    metadata = await handle_rendering(mesh)
    rendered_glb_file = generate_filepath("glb")
    await export_glb_file(rendered_glb_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()


    # background_task.add_task(upload_file, rendered_glb_file)
    # upload_file(rendered_glb_file)
    # background_task.add_task(trigger_usdz_render, rendered_glb_file)
    # trigger_usdz_render(rendered_glb_file)


    # did_file_upload = upload_file(rendered_glb_file, settings.S3_BUCKET)
    # print(f"did_file_upload: {did_file_upload}")
    # if did_file_upload:
    #     rendered_file_name = Path(rendered_glb_file).name
    #     file_url = f"https://s3.amazonaws.com/{settings.S3_BUCKET}/{rendered_file_name}" 
    #     metadata.rendered_file_url = file_url

    rendered_file_name = Path(rendered_glb_file).name
    rendered_glb_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_glb_url = rendered_glb_url
    metadata.rendered_file_url = rendered_glb_url
    # metadata.rendered_usdz_url = rendered_glb_url.replace(".glb",".usdz")


    return metadata 
    
    # return GlbResponse(rendered_file.file_path,media_type="model/gltf-binary")

    # return file_response



async def export_vrm_file(rendered_file):
    bpy.ops.export_scene.vrm(filepath=rendered_file)


@app.post("/render_vrm", response_model=Metadata, tags=["render"])
async def render_vrm(metadata: Metadata, background_task: BackgroundTasks, mesh: Mesh = Depends(deps.get_mesh)):
    is_vrm_installed = len(dir(bpy.ops.vrm)) > 0
    if not is_vrm_installed:
        raise HTTPException(status_code=404, detail="VRM addon not installed")
    
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata.dict()["attributes"])
    metadata = await handle_rendering(mesh)
    rendered_file = generate_filepath("vrm")
    await export_vrm_file(rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
    # metadata.rendered_usdz_url = rendered_glb_url.replace(".glb",".usdz")


    return metadata 




async def export_fbx_file(rendered_file):
    # unpack all files so that textures are detected
    bpy.ops.file.unpack_all(method='USE_LOCAL')
    # use FBX export options with best Unreal compatibility 
    bpy.ops.export_scene.fbx(filepath=rendered_file,
                            apply_scale_options='FBX_SCALE_UNITS',
                            apply_unit_scale=False,
                            mesh_smooth_type='EDGE',
                            use_tspace=True,
                            add_leaf_bones=False,  
                            path_mode="COPY", 
                            embed_textures=True )

def delete_all_objects():
    """ Delete all objects in the scene"""
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)

@app.post("/render_fbx", response_model=Metadata, tags=["render"])
async def render_fbx(metadata: Metadata, background_task: BackgroundTasks, mesh: Mesh = Depends(deps.get_mesh)):
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata.dict()["attributes"])
    metadata = await handle_rendering(mesh)

    rendered_glb_file = generate_filepath("glb")
    await export_glb_file(rendered_glb_file)
    print (Path(rendered_glb_file))
    delete_all_objects()
    bpy.ops.import_scene.gltf(filepath=rendered_glb_file)
    rendered_file = generate_filepath("fbx")
    await export_fbx_file(rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
    # metadata.rendered_usdz_url = rendered_glb_url.replace(".glb",".usdz")


    return metadata 





async def render_jpeg_file(rendered_file):
    bpy.context.scene.render.filepath = rendered_file
    bpy.ops.render.render(use_viewport = False, write_still=True)
    

@app.post("/render_jpeg", response_model=Metadata, tags=["render"])
async def render_jpeg(metadata: Metadata, background_task: BackgroundTasks,  resolution_x: int = 720, resolution_y: int = 720, samples: int = 64, file_format: str = "JPEG", quality: int = 90,  mesh: Mesh = Depends(deps.get_mesh)):
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    bpy.data.scenes["Scene"].cycles.samples = samples
    bpy.context.scene.render.resolution_percentage = 100
    # TODO: makeformat an enum
    bpy.context.scene.render.image_settings.file_format = file_format
    if file_format == 'JPEG':
        bpy.context.scene.render.image_settings.quality = quality
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata.dict()["attributes"])
    metadata = await handle_rendering(mesh)
    rendered_file = generate_filepath("jpg")
    await render_jpeg_file(rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
  

    return metadata 
    










def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    parser.add_argument('--port', 
                        help='the port', 
                        dest='port', type=float, required=False,
                        default=8118)
    
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

    uvicorn.run(app="main:app", app_dir=SCRIPT_PATH, host="::", port=args.port)