import bpy
import os
import random
import json
import site
import sys
import os
import pathlib
from typing import List

BPY_SYS_PATH = list(sys.path) # Make instance of `bpy`'s modified sys.path


class SHADERVERSE_PG_restrictions_item(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    def get_traits_from_metadata(self, context):
        """ Get the traits from the metadata (deprecated)"""
        generated_metadata = json.loads(bpy.context.scene.shaderverse.generated_metadata)
        items = []
        for attribute in generated_metadata:
            trait_type = attribute["trait_type"]
            items.append((trait_type, trait_type, ""))
        return items
    
    def get_traits_from_geonode(self, context):
        """ Get the traits for restrictions from the geometry """
        items = []
        for modifier in bpy.context.scene.shaderverse.main_geonodes_object.modifiers.values():
            node_group = modifier.node_group
            if node_group.type == "GEOMETRY":
                for trait_type in node_group.inputs.keys():
                    items.append((trait_type, trait_type, ""))
        return items
    

    trait: bpy.props.EnumProperty(items=get_traits_from_geonode, name="Objects", description="Traits")
    
    def __repr__(self):
        active_field_object = self.get_active_field()
        active_field_name = active_field_object.name if hasattr(active_field_object, "name") else None 
        active_condition = self.get_active_condition()
        if active_field_name and active_condition:
            return "{} {} {}".format(self.trait, self.get_active_condition(), active_field_name)
        else:
            return "Select condition"
    
    def get_trait_type(self, trait=None):
        if trait == None:
            trait = self.trait
        node_group = bpy.context.scene.shaderverse.parent_node.node_group
        if node_group:
            return (node_group.inputs[trait].type)
    
    def get_active_field(self):
        trait_type = self.get_trait_type()
        match trait_type:
            case "OBJECT":
                return self.restriction_object
            case "COLLECTION":
                return self.restriction_collection
            case "MATERIAL":
                return self.restriction_material
            case "VALUE":
                return self.restriction_value
            case "INT":
                return self.restriction_int

    def get_active_field_name(self):
        trait_type = self.get_trait_type()
        match trait_type:
            case "OBJECT":
                return "restriction_object"
            case "COLLECTION":
                return "restriction_collection"
            case "MATERIAL":
                return "restriction_material"
            case "VALUE":
                return "restriction_value"
            case "INT":
                return "restriction_int"

    def get_active_condition(self):
        trait_type = self.get_trait_type()
        match trait_type:
            case "OBJECT":
                return self.exist_condition
            case "COLLECTION":
                return self.exist_condition
            case "MATERIAL":
                return self.exist_condition
            case "VALUE":
                return self.extended_condition
            case "INT":
                return self.extended_condition

    def get_active_condition_name(self):
        trait_type = self.get_trait_type()
        match trait_type:
            case "OBJECT":
                return "exist_condition"
            case "COLLECTION":
                return "exist_condition"
            case "MATERIAL":
                return "exist_condition"
            case "VALUE":
                return "extended_condition"
            case "INT":
                return "extended_condition"  
            case None:
                return "" 
        
    restriction_object: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        description="Only make this object available for selection if one of the objects in this list have been selected"
    )

    restriction_collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        description="Only make this object available for selection if one of the collections in this list have been selected"
    )

    restriction_material: bpy.props.PointerProperty(
        name="Material",
        type=bpy.types.Material,
        description="Only make this object available for selection if this material has been selected"
    )

    restriction_value: bpy.props.FloatProperty(
        name="Float",
        description="Only make this object available for selection if one of the collection in this list have been selected"
    )

    restriction_int: bpy.props.IntProperty(
        name="Int",
        description="Only make this object available for selection if one of the collection in this list have been selected"
    )


    extended_comparison =  [
        ('==', 'Equal to', "Equal to"),
        ('!=', 'Not equal to', "Not equal to"),
        ('<', 'Less than', "Less than"),
        ('>', 'Greater than', "Greater than")
        ]

    exist_comparison =  [
        ('==', 'Equal to', "Equal to"),
        ('!=', 'Not equal to', "Not equal to")
        ]

    extended_condition: bpy.props.EnumProperty(
        items = extended_comparison,
        name = "Filter",
        description = "Choose the type of filter"
        ) 

    exist_condition: bpy.props.EnumProperty(
        items = exist_comparison,
        name = "Filter",
        description = "Choose the type of filter"
        ) 

    


class SHADERVERSE_UL_restrictions(bpy.types.UIList):
    """Restriction UI List"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                active_propname, index):

        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            text = item.__repr__() if item else "Select a trait"
            layout.label(text=text, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)


class SHADERVERSE_OT_restrictions_new_item(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "shaderverse.restrictions_new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.object.shaderverse.restrictions.add()

        return{'FINISHED'}


class SHADERVERSE_OT_restrictions_delete_item(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "shaderverse.restrictions_delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.object.shaderverse.restrictions

    def execute(self, context):
        restrictions = context.object.shaderverse.restrictions
        index = context.object.shaderverse.restrictions_index

        restrictions.remove(index)
        context.object.shaderverse.restrictions_index = min(max(0, index - 1), len(restrictions) - 1)

        return{'FINISHED'}


class SHADERVERSE_OT_restrictions_move_item(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "shaderverse.restrictions_move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                            ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.object.shaderverse.restrictions

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.object.shaderverse.restrictions_index
        list_length = len(bpy.context.object.shaderverse.restrictions) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.object.shaderverse.restrictions_index = max(0, min(new_index, list_length))

    def execute(self, context):
        restrictions = context.object.shaderverse.restrictions
        index = context.object.shaderverse.restrictions_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        restrictions.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}


class SHADERVERSE_PG_main(bpy.types.PropertyGroup):
    weight: bpy.props.FloatProperty(name='float value', soft_min=0, soft_max=1, default=1.0)
    render_in_2D: bpy.props.BoolProperty(name='bool toggle', default=True)
    render_in_3D: bpy.props.BoolProperty(name='bool toggle', default=True)
    is_parent_node: bpy.props.BoolProperty(name='bool toggle', default=False)


    restrictions: bpy.props.CollectionProperty(type=SHADERVERSE_PG_restrictions_item)
    
    restrictions_index: bpy.props.IntProperty(name = "Index for shaderverse.restrictions", default = 0)


    #builtin integer (variable)property
    int_slider: bpy.props.IntProperty(name='int value', soft_min=0, soft_max=10)
    #builting boolean (variable)property
    bool_toggle: bpy.props.BoolProperty(name='bool toggle')
    #builting string (variable)property
    metadata_prefix: bpy.props.StringProperty(name='Prefix')
    metadata_is_none: bpy.props.BoolProperty(name='Is None')

    def get_trait_value(self):
        current_name = self.id_data.name
        prefix = self.metadata_prefix
        if self.metadata_is_none:
            return "None"
        else:
            return current_name.replace(prefix, "").strip()

    def match_trait(self, trait_type: str, trait_value: str):
        """ Check whether the specified metadata key value pair matches this item """
        _trait_value = trait_value.strip().lower()
        _trait_type = trait_type.strip().lower()
        
        is_collection_matching = _trait_value in [object_name.lower() for object_name in bpy.data.collections[trait_type].all_objects.keys()]
        is_object_matching = self.get_trait_value().lower() == _trait_value

        return is_collection_matching and is_object_matching

class SHADERVERSE_PG_parent_node(bpy.types.PropertyGroup):
    modifier_name: bpy.props.StringProperty(name="Parent Node Modifier Name")
    node_group: bpy.props.PointerProperty(name="Parent Node Group",  type=bpy.types.GeometryNodeTree)
    object: bpy.props.PointerProperty(name="Parent Node's Object",  type=bpy.types.Object)

class SHADERVERSE_PG_render(bpy.types.PropertyGroup):
    range_start: bpy.props.IntProperty(name="Start Number", default=1)
    range_end: bpy.props.IntProperty(name="End Number", default=20)
    batch_name: bpy.props.StringProperty(name="Batch Name", default="batch-01")
    basepath: bpy.props.StringProperty(name="Base Path", subtype="FILE_PATH")
  
class SHADERVERSE_PG_scene(bpy.types.PropertyGroup):
    generated_metadata: bpy.props.StringProperty(name="Generated Meta Data")

    parent_node: bpy.props.PointerProperty(type=SHADERVERSE_PG_parent_node)

    render: bpy.props.PointerProperty(type=SHADERVERSE_PG_render)
    main_geonodes_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Main Geometry Nodes Object")
    
    enable_pre_generation_script: bpy.props.BoolProperty(name="Run Custom Script Before Generation", default=False)
    pre_generation_script: bpy.props.PointerProperty(name="Pre-generation Script", type=bpy.types.Text)

    enable_post_generation_script: bpy.props.BoolProperty(name="Run Custom Script After Generation", default=False)
    post_generation_script: bpy.props.PointerProperty(name="Post-generation Script", type=bpy.types.Text)

    preview_url: bpy.props.StringProperty(name="Shaderverse preview url")

    enable_materials_export: bpy.props.BoolProperty(name="Run Custom Script Before Generation", default=True)

class SHADERVERSE_PG_preferences(bpy.types.PropertyGroup):
    modules_installed: bpy.props.BoolProperty(name="Python Modules Installed", default=False)

class SHADERVERSE_OT_install_modules(bpy.types.Operator):
    """Install Python modules."""
    bl_idname = "shaderverse.install_modules"
    bl_label = "Install Python Module"
    bl_options = {'REGISTER'}

    @classmethod
    def first_install(self):
        self.install(self)

    def install(self):
        required = {'uvicorn', 'fastapi', 'pydantic'}
        
        # missing = self.get_missing_modules(required)

        is_module_installation_complete = False

        try:
            is_module_installation_complete = bpy.context.preferences.addons["shaderverse"].preferences.modules_installed
        except:
            print("Bootstrapping Shaderverse Server Instance")
            is_module_installation_complete = True

        is_running_inside_blender = True

        try:
            blender_server_environ = os.environ.get("BLENDER_SERVER")
            if blender_server_environ == "1":
                is_running_inside_blender = False
        except:
            pass

        if not is_module_installation_complete and is_running_inside_blender: 
            from . import install_modules
            try:
                install_modules.install_modules()
            except:
                raise("Unable to install Python Modules")
            

    def execute(self, context):
        self.install()

        return{'FINISHED'}

class SHADERVERSE_OT_render(bpy.types.Operator):
    """Render NFT"""
    bl_idname = "shaderverse.render"
    bl_label = "Render Batch"
    bl_options = {'REGISTER'}



    def execute(self, context):
        from ..model import GenRange
        from ..render import Render
        from . import server     
        range_start = context.scene.shaderverse.render.range_start
        range_end = context.scene.shaderverse.render.range_end
        basepath = context.scene.shaderverse.render.basepath
        batch_name = context.scene.shaderverse.render.batch_name
        
        gen_range: GenRange = GenRange(start=range_start, end=range_end)
        renderer = Render(gen_range=gen_range, basepath=basepath, batch_name=batch_name)
        if not server.is_initialized:
            server.start_server()
        renderer.handle_execute(context)
        return {'FINISHED'}

        
class SHADERVERSE_PT_preferences(bpy.types.AddonPreferences):
    bl_idname = "shaderverse"
    modules_installed: bpy.props.BoolProperty(name="Python Modules Installed", default=False)

    def draw(self, context):
        layout = self.layout

        # layout.prop(self, "modules_installed", text="Addon Installed")
        if not self.modules_installed:
            from .install_modules import process
            print(f"process status from preferences: {process.status}")
            if process.status == "running":
                layout.label(text="Installing modules...")
            else:
                layout = self.layout
                box = layout.box()
                row = box.row()
                row.alert = True
                # required = {'uvicorn', 'fastapi', 'pydantic'}
                # missing_modules = get_missing_modules(required)
                row.label(text=f"Please install missing python modules")
                row.operator(SHADERVERSE_OT_install_modules.bl_idname, text=SHADERVERSE_OT_install_modules.bl_label)



class SHADERVERSE_PT_main(bpy.types.Panel):
    bl_label = ""
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 
  
    @classmethod
    def poll(cls, context):
        return context.space_data.context in {'MODIFIER','DATA', 'OBJECT'}

    def draw_header(self, context):
        if not hasattr(context.object, "shaderverse"):
            return
        
        from .. import custom_icons
        layout = self.layout
        # left_padding_percent = .1
        # right_padding_percent = 1 - left_padding_percent

        # split = layout.split(factor=left_padding_percent)
        # left_column = split.column()
        # center_split = split.split(factor=right_padding_percent)
        # center_column = center_split.column()
        # right_column = center_split.column()

        # row = center_column.row()
        layout.label(text="Shaderverse")

        shaderverse_generate = SHADERVERSE_OT_generate

        layout.operator(shaderverse_generate.bl_idname, text= shaderverse_generate.bl_label, icon_value=custom_icons["shaderverse_icon"].icon_id, emboss=True)

    def draw(self, context):
        pass

class SHADERVERSE_PT_rarity(bpy.types.Panel):
    bl_parent_id = "SHADERVERSE_PT_main"
    bl_label = "Rarity Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 


    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.

        if not hasattr(context.object, "shaderverse"):
            return

        layout = self.layout 
        split = layout.split(factor=0.1)
        col = split.column()
        col = split.column()
        
        row = col.row()

        this_context = context.object
        #add a label to the UI
        # layout.label(text="Weighted chance of choosing this attribute")
        row.prop(this_context.shaderverse, 'weight', text="Weight Amount", slider=True)



class SHADERVERSE_PT_rendering(bpy.types.Panel):
    bl_parent_id = "SHADERVERSE_PT_main"
    bl_label =  "Rendering Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool"




    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        if not hasattr(context.object, "shaderverse"):
            return

        this_context = context.object

        layout = self.layout 
        split = layout.split(factor=0.1)
        col = split.column()
        col = split.column()
        box = col.box()
        #add a label to the UI
        # layout.label(text="Weighted chance of choosing this attribute")
        box.prop(this_context.shaderverse, 'render_in_2D', text="Include in 2D Renders")
        # subrow2 = layout.row()
        box.prop(this_context.shaderverse, 'render_in_3D', text="Include in 3D Renders")



class SHADERVERSE_PT_metadata(bpy.types.Panel):
    bl_parent_id = "SHADERVERSE_PT_main"
    bl_label =  "Metadata Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool"

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.

        if not hasattr(context.object, "shaderverse"):
            return

        layout = self.layout 
        split = layout.split(factor=0.1)
        col = split.column()
        col = split.column()
        box = col.box()
        this_context = context.object
        row1 = box.row()
        row1.prop(this_context.shaderverse, 'metadata_prefix')
        row1 = box.row()
        row1.prop(this_context.shaderverse, 'metadata_is_none')
        row2 = box.row()
        row2.label(text=f"Trait Value: {this_context.shaderverse.get_trait_value()}")
        row2.enabled = False


class SHADERVERSE_PT_generated_metadata(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shaderverse"
    bl_label = "Generated Metadata"
    bl_idname = "SHADERVERSE_PT_generated_metadata"

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        if context.preferences.addons["shaderverse"].preferences.modules_installed:
            
            from .. import custom_icons
            from .server import is_initialized

            
            layout.separator(factor=1.0) 

            shaderverse_generate = SHADERVERSE_OT_generate

            layout.operator(shaderverse_generate.bl_idname, text= shaderverse_generate.bl_label, icon_value=custom_icons["shaderverse_icon"].icon_id, emboss=True)

            # shaderverse_live_preview = SHADERVERSE_OT_live_preview

            # layout.operator(shaderverse_live_preview.bl_idname, text= shaderverse_live_preview.bl_label, icon="CAMERA_STEREO", emboss=True)


            # display start or stop api button
            if not is_initialized:
                shaderverse_start_api = SHADERVERSE_OT_start_api
                layout.operator(shaderverse_start_api.bl_idname, text= shaderverse_start_api.bl_label, icon="CONSOLE", emboss=True)
            else:
                shaderverse_stop_api = SHADERVERSE_OT_stop_api
                layout.operator(shaderverse_stop_api.bl_idname, text= shaderverse_stop_api.bl_label, icon="CONSOLE", emboss=True)

            


            
            # TODO draw module


            # split = layout.split(factor=0.1)
            # col = split.column()
            # col = split.column()

            # box.prop(this_context.shaderverse, 'is_parent_node', text="Parent Node")
            if hasattr(bpy.types.Scene, "shaderverse"):
                generated_metadata = json.loads(bpy.context.scene.shaderverse.generated_metadata)
                for attribute in generated_metadata:
                    row = layout.row()
                    grid_flow = row.grid_flow(columns=2, even_columns=True, row_major=True)


                    # grid_row = grid_flow.row()


                    col1 = grid_flow.column()
                    col2 = grid_flow.column()

                    col1.label(text="Trait Type".format(attribute["trait_type"]))
                    col1.box().label(text=attribute["trait_type"])
                    col2.label(text="Value")
                    col2.box().label(text=attribute["value"])
                    # layout.separator_spacer()
        else:
            layout.label(text="Waiting for modules to install...")


class SHADERVERSE_PT_settings(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shaderverse"
    bl_label = "Settings"
    bl_idname = "SHADERVERSE_PT_settings"

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        row = layout.row()
        grid_flow = row.grid_flow(columns=1, even_columns=True, row_major=True)
        col = grid_flow.column()
        this_context = bpy.context.scene


        # parent_node: bpy.props.PointerProperty(type=SHADERVERSE_PG_parent_node)

        box = col.box()
        box.prop(this_context.shaderverse, 'main_geonodes_object')


        
        col.prop(this_context.shaderverse, 'enable_pre_generation_script')

        if this_context.shaderverse.enable_pre_generation_script:
            box = col.box()
            box.prop(this_context.shaderverse, 'pre_generation_script', text="Python Script")

        col.prop(this_context.shaderverse, 'enable_post_generation_script')

        if this_context.shaderverse.enable_post_generation_script:
            box = col.box()
            box.prop(this_context.shaderverse, 'post_generation_script', text="Python Script")


class SHADERVERSE_PT_rendering(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shaderverse"
    bl_label = "Rendering"

    def draw(self, context):
        from .. import custom_icons
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        this_context = bpy.context.scene
        shaderverse_render = SHADERVERSE_OT_render

        layout.operator(shaderverse_render.bl_idname, text=shaderverse_render.bl_label, icon_value=custom_icons["shaderverse_icon"].icon_id, emboss=True)


        row = layout.row()
        row.prop(this_context.shaderverse.render, 'basepath')

class SHADERVERSE_PT_batch(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shaderverse"
    bl_label = "Batch"
    bl_parent_id = "SHADERVERSE_PT_rendering"

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 

        this_context = bpy.context.scene

        row = layout.row()
        row.prop(this_context.shaderverse.render, 'batch_name')

        row = layout.row()
        row.prop(this_context.shaderverse.render, 'range_start')
        row = layout.row()
        row.prop(this_context.shaderverse.render, 'range_end')






class SHADERVERSE_PT_restrictions(bpy.types.Panel):
    bl_parent_id = "SHADERVERSE_PT_main"
    bl_label = "Restrict availability to when any of these conditions are true"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        this_context = context.object

        
        split = layout.split(factor=0.1)
        col = split.column()
        col = split.column()
        
        

        row = col.row()
        row.template_list("SHADERVERSE_UL_restrictions", "The_List", this_context.shaderverse,
                        "restrictions", this_context.shaderverse, "restrictions_index")

        row = col.row()
        row.operator('shaderverse.restrictions_new_item', text='NEW')
        row.operator('shaderverse.restrictions_delete_item', text='REMOVE')
        row.operator('shaderverse.restrictions_move_item', text='UP').direction = 'UP'
        row.operator('shaderverse.restrictions_move_item', text='DOWN').direction = 'DOWN'

        if this_context.shaderverse.restrictions_index >= 0 and this_context.shaderverse.restrictions:
            item = this_context.shaderverse.restrictions[this_context.shaderverse.restrictions_index]

            row = col.row()
            row.prop(item, "trait", text="")
            active_condition_name = item.get_active_condition_name()
            row.prop(item, active_condition_name, text="")
            active_field_name = item.get_active_field_name()
            row.prop(item, active_field_name, text="")
            # row.prop(item, "random_prop")


class SHADERVERSE_OT_realize(bpy.types.Operator):
    """Realize Geonode"""
    bl_idname = "shaderverse.realize"
    bl_label = "Realize Geonode"
    bl_options = {'REGISTER', 'UNDO'}

    def realize_object(self, obj):
        print(f"realizing: {obj.name}")
        obj.hide_set(False)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        parent = obj.parent
        parent_bone = obj.parent_bone
        parent_type = obj.parent_type
        
        existing_meshes = self.get_visible_objects("MESH")    
        
        # handle realizing
        bpy.ops.object.duplicates_make_real()
        try:
            bpy.ops.object.convert(target='MESH')
        except:
            print(f"Could not convert mesh for {obj.name}")

            
        # look for new meshes
        current_meshes = self.get_visible_objects("MESH")
        
        objects_to_process : List(bpy.types.Object) = []
        
        
        for mesh in current_meshes:
            if mesh not in existing_meshes:
                print(f"found new mesh {mesh.name}")
                objects_to_process.append(mesh)
        
        if len(objects_to_process) > 0:
            
        
            for mesh_obj in objects_to_process:
                print(f"reparenting {mesh_obj.name}")
                
    
                if parent:
                        
                    if parent.type == "ARMATURE":

                        if parent_type == "BONE":
                            self.handle_bone_parenting(mesh_obj, parent, parent_bone)
                        
                        if parent_type == "OBJECT":
                            self.handle_object_parenting(mesh_obj, parent)

                    
                    # if there is no parent in the new mesh, set it to the parent of the original mesh
                    if not mesh_obj.parent:
                        mesh_obj.parent = parent
                
            bpy.data.objects.remove(obj, do_unlink=True)
            return
                
                    
        # convert UV maps
        try:
            bpy.ops.geometry.attribute_convert(mode='UV_MAP')
        except:
            print(f"Could not convert UV MAP for {obj.name}")



    def reparent_mesh_to_armature(self, armature_obj):
        ''' set the object of the armature modifier to the armature object, and add the armature modifier if it doesn't exist '''
        for obj in armature_obj.children_recursive:
            found_armature = False
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    found_armature = True
                    modifier.object = armature_obj
                    break
             
            if not found_armature:
                armature_modifier = obj.modifiers.new(name="Armature", type="ARMATURE")
                armature_modifier.object = armature_obj

    def set_pose_position(self, armature_obj, pose_position):
        ''' set the armature to rest position and reparent the mesh to the armature '''
        armature = armature_obj.data
        armature.pose_position = pose_position

    def get_visible_objects(self, object_type) -> list[bpy.types.Object]:
        objects = []
        for obj in bpy.data.objects:
            if obj.type == object_type and obj.visible_get():
                objects.append(obj)
        return objects
        
    
    def handle_bone_parenting(self, source_obj: bpy.types.Object, target_armature_obj: bpy.types.Armature, parent_bone: bpy.types.Bone):
        """ parent object to bone of armature """
        obj= source_obj
        armature_obj = target_armature_obj

        bpy.ops.object.select_all(action='DESELECT')

        armature_obj.select_set(True)
        bpy.context.view_layer.objects.active = armature_obj

        bpy.ops.object.mode_set(mode='EDIT')

        armature_obj.data.edit_bones.active = armature_obj.data.edit_bones[parent_bone]

        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')  # deselect all objects
        obj.select_set(True)
        armature_obj.select_set(True)
        bpy.context.view_layer.objects.active = armature_obj
        # the active object will be the parent of all selected object
        print(f"parenting {obj.name} to {armature_obj.name} bone {parent_bone}")

        bpy.ops.object.parent_set(type='BONE', keep_transform=False)

    def handle_object_parenting(self, source_obj, target_obj):
        """ parent object to armature object"""
        obj= source_obj
        parent_obj = target_obj

        bpy.ops.object.select_all(action='DESELECT')

        parent_obj.select_set(True)
        bpy.context.view_layer.objects.active = parent_obj

        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

    def is_geonode(self, obj: bpy.types.Object):
        """ check if object is a geonode """
        if obj.type == "MESH":
            for modifier in obj.modifiers.values():
                if modifier.type == "NODE":
                    node_group = modifier.node_group
                    if node_group.type == "GEOMETRY":
                        return True
        return False

    def execute(self, context):
        # deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        armatures_to_realize = self.get_visible_objects("ARMATURE")
        mesh_objects_to_realize = self.get_visible_objects("MESH")
        
        print(f'starting with these meshes to process: {mesh_objects_to_realize}')
            
        # set pose position to rest
        for obj in armatures_to_realize:
            self.set_pose_position(obj, 'REST')
        
        # realize all visibile meshes
        for obj in mesh_objects_to_realize:
            self.realize_object(obj)

        # reparent meshes to armatures
        for obj in armatures_to_realize:
            self.reparent_mesh_to_armature(obj)
#        
        # set pose position to pose
        for obj in armatures_to_realize:
            self.set_pose_position(obj, 'POSE')
        
        existing_objects = armatures_to_realize + mesh_objects_to_realize
        current_meshes = self.get_visible_objects("MESH")

        # hide all geonodes
        for obj in current_meshes:
            if self.is_geonode(obj):
                obj.hide_set(True)
 

        # delete extra visible meshes that may have been created
        # for obj in bpy.data.objects:
        #     if obj.type == 'MESH' and obj.visible_get() and obj not in objects_to_realize:
        #         bpy.data.objects.remove(obj, do_unlink=True)

        # parent_node_object = context.scene.shaderverse.main_geonodes_object
        # parent_node_collection = parent_node_object.users_collection[0]
        # parent_node_objects = parent_node_collection.all_objects
        # for obj in parent_node_objects:
        #     self.realize_object(obj)

        # animated_objects = bpy.data.collections['Animated Objects'].all_objects
        # for obj in animated_objects:
        #     self.realize_object(obj)

        return {'FINISHED'}


class SHADERVERSE_OT_generate(bpy.types.Operator):
    """Generate new metadata and mesh preview"""
    bl_idname = "shaderverse.generate"
    bl_label = "Generate Mesh"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        from shaderverse.mesh import Mesh
        mesh = Mesh()
        
        mesh.run_pre_generation_script()
        mesh.create_animated_objects_collection()
        mesh.reset_animated_objects()
        mesh.run_metadata_generator()
        mesh.update_geonodes_from_metadata()
        mesh.run_post_generation_script()
        mesh.make_animated_objects_visible()

        return {'FINISHED'}


class SHADERVERSE_OT_live_preview(bpy.types.Operator):
    
    """ Live preview """
    bl_idname = "shaderverse.live_preview"
    bl_label = "Live Web Preview"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from . import server
        context = bpy.context
        server.start_server(live_preview=True)
        return {'FINISHED'}

class SHADERVERSE_OT_start_api(bpy.types.Operator):
    """ Start API"""
    bl_idname = "shaderverse.start_api"
    bl_label = "Start API"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from . import server
        context = bpy.context
        server.start_server(live_preview=False)
        return {'FINISHED'}

class SHADERVERSE_OT_stop_api(bpy.types.Operator):
    """ Stop API """
    bl_idname = "shaderverse.stop_api"
    bl_label = "Stop API"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from . import server
        context = bpy.context
        server.kill_fastapi()
        return {'FINISHED'}

class SHADERVERSE_OT_stop_live_preview(bpy.types.Operator):
    
    """ Stop the shaderverse live preview """
    bl_idname = "shaderverse.stop_live_preview"
    bl_label = "Stop Live Preview"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from . import server
        context = bpy.context
        print("stopping live preview")
        server.kill_fastapi()
        server.kill_tunnel()
        return {'FINISHED'}

def handle_adding_sites_to_path():
    home_path =  pathlib.Path.home()
    # user_base = os.path.join(home_path, ".shaderverse", "python")
    # user_site =  os.path.join(user_base, "site-packages")
    user_base = os.path.realpath(site.USER_BASE)
    user_site = os.path.realpath(site.USER_SITE)

    sys.path.append(user_base)
    sys.path.append(user_site)