import argparse
import uvicorn
import os 
import json
import requests
from fastapi import  FastAPI, Request, HTTPException
from shaderverse.model import Parameters2d
from shaderverse.dynamic_model import Metadata, MetadataList
from typing import List
import tempfile
import sys
from shaderverse.mesh import Mesh
from shaderverse import bl_info
import bpy
from fastapi.responses import FileResponse, JSONResponse
from fastapi.routing import APIRoute
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
sys.path.append(SCRIPT_PATH) # this is a hack to make the import work in Blender
from celery.app import Proxy
from config.celery_utils import create_celery
from celery_tasks import tasks
from config.celery_utils import get_task_info, get_batch_info
from celery import group
import logging
from shaderverse.api.utils import get_temporary_directory

def get_shaderverse_version():
    version_tuple = bl_info["version"]
    version = ".".join([str(v) for v in version_tuple])
    return version

description = """
Shaderverse Generative 3D API 🚀

## Geneate Metadata

You can **generate new json metadata** based on assets in the Blender project file.

## Render 2D and 3D files

You can **render files** from metadata json.
"""

def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"

def create_app() -> FastAPI:
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
    app.celery_app = create_celery()
    return app

app = create_app()
celery: Proxy = app.celery_app

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

# @app.on_event("startup")
# async def startup_event():
#     bpy.ops.preferences.addon_enable(module="shaderverse")
#     BLEND_FILE = os.environ.get("BLEND_FILE")
#     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

@app.on_event("shutdown")
async def shutdown_event():
    bpy.ops.wm.quit_blender()

@app.post("/generate", response_class=JSONResponse, tags=["generator"])
async def generate():
    task = tasks.generate_task.apply_async()
    return JSONResponse({"task_id": task.id})

@app.get("/task/{task_id}", tags=["task"])
async def get_task_status(task_id: str, request: Request) -> dict:
    """
    Return the status of the submitted Task
    """
    task_info = get_task_info(task_id)
    if type(task_info["task_result"]) == Metadata:
        metadata: Metadata = task_info["task_result"]
        metadata.set_attributes_from_json()
        if metadata.rendered_file_url:
            rendered_file_url = metadata.rendered_file_url.replace("http://localhost:8118/", str(request.base_url))
            metadata.rendered_file_url = rendered_file_url

        task_info["task_result"] = metadata
    return task_info

@app.get("/batch/{batch_id}", tags=["task"])
async def get_batch_status(batch_id: str) -> dict:
    """
    Return the status of the submitted Batch
    """
    return get_batch_info(batch_id)

@app.get("/batch_metadata/{batch_id}", tags=["task"])
async def get_batch_metadata_status(batch_id: str, request: Request) -> dict:
    """
    Return the metadata of the submitted Batch
    """
    result = get_batch_info(batch_id)
    _metadata_list: List[Metadata] = []
    try:
        for task_result in result["batch_result"]:
            metadata: Metadata = task_result["task_result"]
            metadata.set_attributes_from_json()
            _metadata_list.append(metadata)
            if metadata.rendered_file_url:
                rendered_file_url = metadata.rendered_file_url.replace("http://localhost:8118/", str(request.base_url))
                metadata.rendered_file_url = rendered_file_url
            
        metadata_list = MetadataList(metadata_list=_metadata_list)
        logging.info(f"metadata_list: {metadata_list}")
    except Exception as e:
        metadata_list = JSONResponse({"error": str(e)})

    return metadata_list


@app.get("/rendered/{file_id}", response_class=FileResponse, tags=["download"])
def get_rendered_file(file_id: str):
    """Get a rendered file"""
    temp_dir = get_temporary_directory()
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

@app.post("/render_glb", response_class=JSONResponse, tags=["render"])
async def render_glb(metadata: Metadata):
    metadata.generate_json_attributes()
    task = tasks.render_glb_task.apply_async(args=[metadata.dict()])
    return JSONResponse({"task_id": task.id})

@app.post("/render_usdz", response_class=JSONResponse, tags=["render"])
async def render_usdz(metadata: Metadata):
    metadata.generate_json_attributes()
    task = tasks.render_usdz_task.apply_async(args=[metadata.dict()])
    return JSONResponse({"task_id": task.id})

@app.post("/render_vrm", response_class=JSONResponse, tags=["render"])
async def render_vrm(metadata: Metadata):
    is_vrm_installed = len(dir(bpy.ops.vrm)) > 0
    if not is_vrm_installed:
        raise HTTPException(status_code=404, detail="VRM addon not installed")
    
    metadata.generate_json_attributes()
    task = tasks.render_vrm_task.apply_async(args=[metadata.dict()])
    return JSONResponse({"task_id": task.id})

@app.post("/render_fbx", response_class=JSONResponse, tags=["render"])
async def render_fbx(metadata: Metadata):
    metadata.generate_json_attributes()
    task = tasks.render_fbx_task.apply_async(args=[metadata.dict()])
    return JSONResponse({"task_id": task.id})

@app.post("/render_jpeg", response_class=JSONResponse, tags=["render"])
async def render_jpeg(metadata: Metadata, render_params: Parameters2d | None = None ):
    if render_params is None:
        render_params = Parameters2d()
    metadata.generate_json_attributes()

    task = tasks.render_2d_task.apply_async(args=[metadata.dict(), render_params.dict(), "jpg"])
    # return metadata
    return JSONResponse({"task_id": task.id})


@app.post("/render_mp4", response_class=JSONResponse, tags=["render"])
async def render_mp4(metadata: Metadata, render_params: Parameters2d | None = None):
    if render_params is None:
        render_params = Parameters2d()
    metadata.generate_json_attributes()
    task = tasks.render_2d_task.apply_async(args=[metadata.dict(), render_params, "mp4"])
    # return metadata
    return JSONResponse({"task_id": task.id})

@app.post("/render_mov", response_class=JSONResponse, tags=["render"])
async def render_mov(metadata: Metadata, render_params: Parameters2d | None = None):
    if render_params is None:
        render_params = Parameters2d()
    metadata.generate_json_attributes()
    task = tasks.render_2d_task.apply_async(args=[metadata.dict(), render_params, "mov"])
    # return metadata
    return JSONResponse({"task_id": task.id})

@app.post("/render_gif", response_class=JSONResponse, tags=["render"])
async def render_gif(metadata: Metadata, render_params: Parameters2d | None = None):
    if render_params is None:
        render_params = Parameters2d()
    metadata.generate_json_attributes()
    task = tasks.render_2d_task.apply_async(args=[metadata.dict(),render_params.dict(), "gif"])
    # return metadata
    return JSONResponse({"task_id": task.id})

@app.post("/generate_batch", response_class=JSONResponse, tags=["generator"])
def generate_batch(number_to_generate: int, starting_id: int = 1):
    group_list = []
    for i in range(starting_id, number_to_generate+starting_id):
        #TODO add handle i as id in generate_task
        task = tasks.generate_task.s(id=i)
        group_list.append(task)
         
    job = group(group_list)
    result = job.apply_async()
    result.save()

    return JSONResponse({"batch_id": result.id})

@app.post("/render_batch", response_class=JSONResponse, tags=["render"])
def render_batch(metadata_list: MetadataList, should_render_jpeg: bool = False, jpeg_params: Parameters2d | None = None, should_render_fbx: bool = False, should_render_glb: bool = False, should_render_vrm: bool = False, should_render_usdz: bool = False, should_render_mp4: bool = False, mp4_params: Parameters2d | None = None, should_render_mov: bool = False, mov_params: Parameters2d | None = None, should_render_gif:bool = False,  gif_params: Parameters2d | None = None, should_open_blend_file: bool = False):
    group_list = []
    for metadata in metadata_list.metadata_list:
        metadata.generate_json_attributes()
        if should_render_glb:
            if glb_params is None:
                glb_params = Parameters2d()
            task = tasks.render_glb_task.s(metadata.dict(), should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_jpeg:
            if jpeg_params is None:
                jpeg_params = Parameters2d()
            task = tasks.render_2d_task.s(metadata.dict(),params_2d=jpeg_params.dict(), render_file_type="jpg",should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_mp4:
            if mp4_params is None:
                mp4_params = Parameters2d()
            task = tasks.render_2d_task.s(metadata.dict(),params_2d=mp4_params.dict(), render_file_type="mp4" ,should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_mov:
            if mov_params is None:
                mov_params = Parameters2d()
            task = tasks.render_2d_task.s(metadata.dict(),params_2d=mov_params.dict(), render_file_type="mov",should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_gif:
            if gif_params is None:
                gif_params = Parameters2d()
            task = tasks.render_2d_task.s(metadata.dict(),params_2d=gif_params.dict(), render_file_type="gif" ,should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_fbx:
            task = tasks.render_fbx_task.s(metadata.dict(), should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_vrm:
            task = tasks.render_vrm_task.s(metadata.dict(), should_open_blend_file=should_open_blend_file)
            group_list.append(task)
        if should_render_usdz:
            task = tasks.render_usdz_task.s(metadata.dict(), should_open_blend_file=should_open_blend_file)
            group_list.append(task)
         
    job = group(group_list)
    result = job.apply_async()
    result.save()

    return JSONResponse({"batch_id": result.id})

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    parser.add_argument('--port', 
                        help='the port', 
                        dest='port', type=int, required=False,
                        default=8118)
   
    python_args = sys.argv[sys.argv.index("--")+1:]
    args, unknown = parser.parse_known_args(args=python_args)
    return args

if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(message)s')

    uvicorn.run(app="main:app", app_dir=SCRIPT_PATH, host="::", port=args.port)