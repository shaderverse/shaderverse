from typing import List
from celery import shared_task
from pathlib import Path
from fastapi import HTTPException
import bpy
import json
import os
import tempfile
from shaderverse.mesh import Mesh
from shaderverse.model import Parameters2d, Binary
from shaderverse.dynamic_model import Metadata, Attribute
from shaderverse.api.utils import get_temporary_directory, get_os
from shaderverse.api.third_party.usdzconvert import usdzconvert
from shaderverse.config.binaries import ffmpeg
import subprocess
import logging

def open_blend_file(filepath: str = bpy.data.filepath):
    bpy.ops.wm.open_mainfile(filepath=filepath)

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
    mesh.create_animated_objects_collection()
    mesh.reset_animated_objects()
    mesh.run_metadata_generator()


def export_glb_file(glb_filename: str):
        bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='AUTO', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials='EXPORT', export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, use_selection=False, use_visible=True, use_renderable=True, use_active_collection=False, export_extras=False, export_yup=True, export_apply=True, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=True, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=True, export_morph_normal=True, export_morph_tangent=False, export_lights=False, export_anim_single_armature=True)

# @app.on_event("startup")
# def startup_event():
#     bpy.ops.preferences.addon_enable(module="shaderverse")
#     BLEND_FILE = os.environ.get("BLEND_FILE")
#     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
              name='generate:generate_task')
def generate_task(self, should_open_blend_file: bool = False, id=None):
    if should_open_blend_file:
        open_blend_file()
    mesh = Mesh()
    print("NFT attributes before running generator")
    print(mesh.attributes)
    run_generator(mesh)
    # print(bpy.context.active_object.name)


    print("NFT attributes after running generator")
    print(mesh.attributes)

    generated_metadata: List[Attribute] = []
    if len(bpy.context.scene.shaderverse.generated_metadata) > 0:
        generated_metadata = json.loads(bpy.context.scene.shaderverse.generated_metadata)

    metadata = Metadata(
        id=id,
        filename=bpy.data.filepath,json_attributes=generated_metadata)
    
    # metadata.set_attributes_from_json()

    print("reverting file")
    bpy.ops.wm.revert_mainfile()


    return metadata

def set_active_object(object_ref):
    bpy.context.view_layer.objects.active = object_ref
    

def generate_filepath(extension: str) -> str:
    """ Generate a temporary file path with the given extension"""
    temp_dir_name = get_temporary_directory()
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
    

def handle_rendering(mesh: Mesh):
    mesh.update_geonodes_from_metadata()
    set_object_visibility(mesh)
    bpy.ops.shaderverse.realize() 
    
    generated_metadata: List[Attribute] = json.loads(bpy.context.scene.shaderverse.generated_metadata)
    metadata = Metadata(
        filename=bpy.data.filepath,json_attributes=generated_metadata)

    return (metadata)


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
              name='render:render_glb_task')
def render_glb_task(self, metadata: dict, should_open_blend_file: bool = False):
    if should_open_blend_file:
        open_blend_file()
    mesh = Mesh()
    id = metadata["id"]
    # print(f"metadata: {metadata}")
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata["json_attributes"])
    
    metadata = handle_rendering(mesh)
    rendered_glb_file = generate_filepath("glb")
    export_glb_file(rendered_glb_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_glb_file).name
    rendered_glb_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_glb_url = rendered_glb_url
    metadata.rendered_file_url = rendered_glb_url
    metadata.id = id

    return metadata 


def export_vrm_file(rendered_file):
    bpy.ops.export_scene.vrm(filepath=rendered_file)


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
              name='render:render_vrm_task')
def render_vrm_task(self, metadata: dict, should_open_blend_file: bool = False):
    is_vrm_installed = len(dir(bpy.ops.vrm)) > 0
    if not is_vrm_installed:
        raise HTTPException(status_code=404, detail="VRM addon not installed")
    
    id = metadata["id"]
    if should_open_blend_file:
        open_blend_file()
    mesh = Mesh()
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata["json_attributes"])
    metadata = handle_rendering(mesh)
    rendered_file = generate_filepath("vrm")
    mesh.set_armature_position("REST")
    export_vrm_file(rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
    metadata.id = id

    return metadata 

def export_fbx_file(rendered_file):
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


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
              name='render:render_fbx_task')
def render_fbx_task(self, metadata: dict, should_open_blend_file: bool = False):
    if should_open_blend_file:
        open_blend_file()
    mesh = Mesh()
    id = metadata["id"]
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata["json_attributes"])
    
    metadata = handle_rendering(mesh)

    rendered_glb_file = generate_filepath("glb")
    export_glb_file(rendered_glb_file)
    print (Path(rendered_glb_file))
    delete_all_objects()
    bpy.ops.import_scene.gltf(filepath=rendered_glb_file)
    rendered_file = generate_filepath("fbx")
    export_fbx_file(rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
    metadata.id = id

    return metadata 

def export_usdz_file(rendered_glb_file, rendered_usdz_file):
    argument_list = [rendered_glb_file, rendered_usdz_file]
    usdzconvert.tryProcess(argument_list)

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
              name='render:render_usdz_task')
def render_usdz_task(self, metadata: dict, should_open_blend_file: bool = False):
    if should_open_blend_file:
        open_blend_file()
    mesh = Mesh()
    id = metadata["id"]
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata["json_attributes"])
    
    metadata = handle_rendering(mesh)

    rendered_glb_file = generate_filepath("glb")
    export_glb_file(rendered_glb_file)
    
    rendered_file = generate_filepath("usdz")
    export_usdz_file(rendered_glb_file=rendered_glb_file, rendered_usdz_file=rendered_file)
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
    metadata.id = id

    return metadata 

def render_jpeg_file(rendered_file):
    bpy.context.scene.render.filepath = rendered_file
    bpy.ops.render.render(use_viewport = False, write_still=True)

def render_mp4_file(rendered_file):
    bpy.context.scene.render.filepath = rendered_file
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.ops.render.render(use_viewport = False, animation=True, write_still=True)

def render_mov_file(rendered_file):
    bpy.context.scene.render.filepath = rendered_file
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'QUICKTIME'
    bpy.context.scene.render.ffmpeg.codec = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

    bpy.ops.render.render(use_viewport = False, animation=True, write_still=True)

    
def get_render_method(render_file_type: str):
    if render_file_type == "jpg":
        return render_jpeg_file
    elif render_file_type == "mp4":
        return render_mp4_file
    elif render_file_type == "mov" or render_file_type == "gif":
        return render_mov_file
    
def convert_mov_to_gif(rendered_file):
    current_os = get_os()
    ffmpeg_binary = ffmpeg.dict()["files"].get(current_os)
    ffmpeg_path = Path(ffmpeg.base_dir, ffmpeg.binary_name, ffmpeg_binary)
    cmd = [ffmpeg_path, "-i", rendered_file, "-f", "gif", "-lavfi", "split[v],palettegen,[v]paletteuse", rendered_file.replace(".mov", ".gif")]
    logging.info(f"converting mov to gif: {cmd}")
    subprocess.run(cmd)
    

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
              name='render:render_2d_task')
def render_2d_task(self, metadata: dict, params_2d: dict, render_file_type: str, should_open_blend_file: bool = False):
    if should_open_blend_file:
        open_blend_file()
    mesh = Mesh()
    id = metadata["id"]
    render_params = Parameters2d(**params_2d)
    bpy.context.scene.render.resolution_x = render_params.resolution_x
    bpy.context.scene.render.resolution_y = render_params.resolution_y
    bpy.data.scenes["Scene"].cycles.samples = render_params.samples
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.fps = render_params.fps

    # TODO: makeformat an enum
    if render_file_type == "jpg":
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
    else:
        bpy.context.scene.render.image_settings.file_format = 'PNG'
    
    bpy.context.scene.render.image_settings.quality = render_params.quality
        
    bpy.context.scene.shaderverse.generated_metadata = json.dumps(metadata["json_attributes"])
    
    metadata = handle_rendering(mesh)
    rendered_file = generate_filepath(render_file_type)
    if render_file_type == "gif":
        rendered_file = rendered_file.replace(".gif", ".mov")
    render_method = get_render_method(render_file_type)
    render_method(rendered_file)
    if render_file_type == "gif":
        rendered_gif = rendered_file.replace(".mov", ".gif")
        convert_mov_to_gif(rendered_file)
        rendered_file = rendered_gif
    print("reverting file")
    bpy.ops.wm.revert_mainfile()

    rendered_file_name = Path(rendered_file).name
    rendered_file_url = f"http://localhost:8118/rendered/{rendered_file_name}" 
    metadata.rendered_file_url = rendered_file_url
    metadata.id = id
  
    return metadata  