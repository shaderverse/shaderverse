import argparse
from email.charset import BASE64
import os 
import json
import bpy
from .model import Metadata, Attributes, GlbFile, GenRange
from typing import List
import tempfile
import base64
import datetime
import sys


class Render():

    old = ""
    fd = ""
    basepath: str
    batch_name: str

    SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

    gen_range: GenRange

    def __init__(self, gen_range: GenRange, basepath: str, batch_name: str) -> None:
        self.gen_range = gen_range
        self.basepath = bpy.path.abspath(basepath)
        self.batch_name = batch_name


    def generate(self):
        bpy.ops.shaderverse.generate()
        bpy.ops.shaderverse.realize()

        generated_metadata: List[Attributes] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

        metadata = Metadata(
            filename=bpy.data.filepath,attributes=generated_metadata)

        return metadata


    def get_parent_node(self)->bpy.types.Object | None:
        for obj in bpy.data.objects:
            parent_node = None
            if hasattr(obj, "shaderverse"):
                if obj.shaderverse.is_parent_node:
                    parent_node = obj
                    break
        return parent_node

    def revert_file(self):
        bpy.ops.wm.revert_mainfile()

    def set_objects_to_active(self, object_list):
        for obj in object_list:   
            print("activating object: {}".format(obj))
            obj.hide_set(False)

    def get_export_materials_option(self)-> str:
        option = "EXPORT"
        if not bpy.context.scene.shaderverse.enable_materials_export:
            option = "NONE"
        return option

    def disable_stdout(self):
        global fd, old
        logfile = 'blender_render.log'
        open(logfile, 'a').close()
        old = os.dup(sys.stdout.fileno())
        sys.stdout.flush()
        os.close(sys.stdout.fileno())
        fd = os.open(logfile, os.O_WRONLY)

    def enable_stdout(self):
        global fd
        global old
        os.close(fd)
        os.dup(old)
        os.close(old)


    def export_glb(self, glb_filename: str):
        # reset_scene()
        # parent_object = bpy.data.objects[object_name]
        # # object_children = parent_object.children
        # # object_list = []
        # # object_list.append(parent_object)
        # # object_list.extend(object_children)
        # # set_objects_to_active(object_list)
        # bpy.ops.shaderverse.realize()

        for obj in bpy.data.objects:
            if not obj.shaderverse.render_in_3D:
                obj.hide_set(True)

        export_materials = self.get_export_materials_option()
        
        bpy.ops.export_scene.gltf(filepath=glb_filename, check_existing=False, export_format='GLB', ui_tab='GENERAL', export_copyright='', export_image_format='JPEG', export_texcoords=True, export_normals=True, export_draco_mesh_compression_enable=False, export_tangents=False, export_materials=export_materials, export_colors=True, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, use_selection=False, use_visible=True, use_renderable=True, use_active_collection=False, export_extras=False, export_yup=True, export_apply=True, export_animations=True, export_frame_range=True, export_frame_step=1, export_force_sampling=True, export_nla_strips=False, export_def_bones=False, export_current_frame=False, export_skins=True, export_all_influences=False, export_morph=False, export_morph_normal=True, export_morph_tangent=False, export_lights=False, export_displacement=False, will_save_settings=True, filter_glob='*.glb;*.gltf')


    def configure_scene(self):
        bpy.context.scene.render.resolution_x = 720
        bpy.context.scene.render.resolution_y = 720
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.cycles.samples = 256

    def render_scene(self, filename):
        bpy.context.scene.render.filepath = filename
        bpy.ops.render.render(use_viewport = False, write_still=True)


    def enable_cuda(self):      
        # Set the device_type
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"

        # Set the device and feature set
        preferences = bpy.context.preferences.addons['cycles'].preferences
        preferences.compute_device_type = 'CUDA'
        bpy.ops.wm.save_userpref()
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.scene.cycles.feature_set = "SUPPORTED"
        bpy.context.preferences.system.use_gpu_subdivision = False

        for device_type in preferences.get_device_types(bpy.context):
            preferences.get_devices_for_type(device_type[0])

        for device in preferences.devices:
            print('Device {} of type {} using: {} '.format(device.name, device.type, device.use))


        print(preferences.get_devices())


    def write_json(self, metadata, file_path):
        with open(file_path, 'w') as outfile:
            outfile.write(json.dumps(metadata, indent=2))

    def make_path_if_not_exist(self, path):
        isExist = os.path.exists(path)
        if not isExist:
            # Create a new directory because it does not exist 
            os.makedirs(path)

    def execute(self):
        # object_to_render = get_parent_node()
        # glb_temp_file = tempfile.NamedTemporaryFile()
        
        # filepath = "/home/mg/blender/projects/dumpster-fire/8.0.6.blend"
        # bpy.ops.wm.open_mainfile(filepath=filepath)
        filepath = os.path.join(self.basepath, self.batch_name)
        self.make_path_if_not_exist(filepath)


        start_time = datetime.datetime.now()
        count = 0

        for item in range(self.gen_range.start, self.gen_range.end + 1):
            item_count = item
            current_time = datetime.datetime.now()
            total_items = self.gen_range.end + 1 - self.gen_range.start 
            items_remaining = total_items - count
            time_per_item = None if count < 1 else (current_time - start_time)/count
            time_remaining = None if count < 1 else time_per_item * items_remaining

            print("now rendering item: {}/{}, id: {}".format(item_count, total_items, item))
            print("time per item: {}".format(time_per_item))
            print("time remaining: {}".format(time_remaining))
            # if (self.gen_range.start and item_count < self.gen_range.end):
            #     continue
            # if (self.gen_range.end and item_count > self.gen_range.end):
            #     continue
            
                    
            self.enable_cuda()
            self.configure_scene()
            metadata = self.generate()
            
            # temp_dir_name = tempfile.mkdtemp(prefix='shaderverse_')
            # temp_file_name = f"{next(tempfile._get_candidate_names())}.glb"
            # glb_temp_file_name = os.path.join(temp_dir_name,temp_file_name)
            # export_glb(glb_temp_file_name)

            # print(glb_temp_file_name)
            
            # # Open binary file for reading
            # f = open(glb_temp_file_name, 'rb')

            # # Get a string from binary file
            # d = f.read()

            # # print(d)
            # encoded_bytes = base64.urlsafe_b64encode(d)


            # # glb_bytes = base64.urlsafe_b64encode(glb_bytes)
            # glb = GlbFile(buffer=encoded_bytes)



            # basepath = os.path.dirname(os.path.realpath(__file__))
            image_filename = f"{item}.jpg"
            image_path = os.path.join(self.basepath, self.batch_name, image_filename)
            self.render_scene(image_path)

            print(image_path)

            glb_filename = f"{item}.glb"
            glb_path = os.path.join(self.basepath, self.batch_name, glb_filename)
            
            self.export_glb(glb_path)
            
            print(glb_path)

            json_filename = f"{item}.json"
            json_path = os.path.join(self.basepath, self.batch_name, json_filename)

            self.write_json(metadata.dict(), json_path)

            self.revert_file()

            print(json_path)
            count +=1 




            # return glb

    if __name__ == "__main__":

        execute()

