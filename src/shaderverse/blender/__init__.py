import bpy
import os
import random
import json
import site
import sys
import os
import pathlib

BPY_SYS_PATH = list(sys.path) # Make instance of `bpy`'s modified sys.path





class SHADERVERSE_PG_restrictions_item(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""


    def get_traits(self, context):
        generated_metadata = json.loads(bpy.context.scene.shaderverse.generated_metadata)
        items = []
        
        for attribute in generated_metadata:
            trait_type = attribute["trait_type"]
            items.append((trait_type, trait_type, ""))
        return items
    

    trait: bpy.props.EnumProperty(items=get_traits, name="Objects", description="Traits"
    )
    
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

    restriction_int: bpy.props.FloatProperty(
        name="Float",
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
    string_field: bpy.props.StringProperty(name='string field')
    
class SHADERVERSE_PG_parent_node(bpy.types.PropertyGroup):
    modifier_name: bpy.props.StringProperty(name="Parent Node Modifier Name")
    node_group: bpy.props.PointerProperty(name="Parent Node Group",  type=bpy.types.GeometryNodeTree)
    object: bpy.props.PointerProperty(name="Parent Node's Object",  type=bpy.types.Object)

    
class SHADERVERSE_PG_scene(bpy.types.PropertyGroup):
    generated_metadata: bpy.props.StringProperty(name="Generated Meta Data")

    parent_node: bpy.props.PointerProperty(type=SHADERVERSE_PG_parent_node)
    
    enable_pre_generation_script: bpy.props.BoolProperty(name="Run Custom Script Before Generation", default=False)
    pre_generation_script: bpy.props.PointerProperty(name="Pre-generation Script", type=bpy.types.Text)

    enable_post_generation_script: bpy.props.BoolProperty(name="Run Custom Script After Generation", default=False)
    post_generation_script: bpy.props.PointerProperty(name="Post-generation Script", type=bpy.types.Text)

    preview_url: bpy.props.StringProperty(name="Shaderverse preview url")
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
        print("in install")

        is_module_installation_complete = False

        try:
            is_module_installation_complete = bpy.context.preferences.addons["shaderverse"].preferences.modules_installed
        except:
            print("Bootstrapping Shaderverse Server Instance")
            is_module_installation_complete = True

        if not is_module_installation_complete: 
            from . import install_modules
            try:
                install_modules.install_modules()
                bpy.context.preferences.addons["shaderverse"].preferences.modules_installed = True
            except:
                raise("Unable to install Python Modules")
            

    def execute(self, context):
        self.install()

        return{'FINISHED'}
    
    

class SHADERVERSE_PT_preferences(bpy.types.AddonPreferences):
    bl_idname = "shaderverse"
    modules_installed: bpy.props.BoolProperty(name="Python Modules Installed", default=False)

    def draw(self, context):
        layout = self.layout
        if not self.modules_installed:
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
    bl_context = "modifier"
  
        


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


class SHADERVERSE_PT_object(SHADERVERSE_PG_main):
    bl_context = "object"

class SHADERVERSE_PT_modifier(SHADERVERSE_PG_main):
    bl_context = "modifier"


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

        box.prop(this_context.shaderverse, 'is_parent_node', text="Parent Node")

class SHADERVERSE_PT_generated_metadata(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shaderverse"
    bl_label = "Generated NFT Metadata"
    bl_idname = "SHADERVERSE_PT_generated_metadata"

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        from .. import custom_icons
        layout = self.layout 
        layout.separator(factor=1.0) 

        shaderverse_generate = SHADERVERSE_OT_generate

        layout.operator(shaderverse_generate.bl_idname, text= shaderverse_generate.bl_label, icon_value=custom_icons["shaderverse_icon"].icon_id, emboss=True)

        shaderverse_live_preview = SHADERVERSE_OT_live_preview

        layout.operator(shaderverse_live_preview.bl_idname, text= shaderverse_live_preview.bl_label, icon="CAMERA_STEREO", emboss=True)


        


        
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
        
        col.prop(this_context.shaderverse, 'enable_pre_generation_script')

        if this_context.shaderverse.enable_pre_generation_script:
            box = col.box()
            box.prop(this_context.shaderverse, 'pre_generation_script', text="Python Script")

        col.prop(this_context.shaderverse, 'enable_post_generation_script')

        if this_context.shaderverse.enable_post_generation_script:
            box = col.box()
            box.prop(this_context.shaderverse, 'post_generation_script', text="Python Script")

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



class SHADERVERSE_OT_generate(bpy.types.Operator):
    """Generate new metadata and NFT preview"""
    bl_idname = "shaderverse.generate"
    bl_label = "Generate NFT Preview"
    bl_options = {'REGISTER', 'UNDO'}

    def generate_random_range(self, item_ref, precision):
        start = item_ref.min_value
        stop = item_ref.max_value
        start = round(start / precision)
        stop = round(stop / precision)
        generated_int = random.randint(start, stop)
        return generated_int * precision


    all_objects =  None
    attributes = []

    geometry_node_objects = []
    parent_node = None

    def __init__(self):
        self.all_objects = bpy.data.objects.items()


    def find_geometry_nodes(self, object_ref):

        geometry_node_objects = []
        object_name = object_ref.name


        object_modifiers = object_ref.modifiers.items()

        for modifier in object_modifiers:
            modifier_name = modifier[0]
            modifier_ref = modifier[1]
            if hasattr(modifier_ref, "node_group"):
                node_group = modifier_ref.node_group
            
                if node_group.type == "GEOMETRY":
                    node_object = {
                        "object_name": object_name,
                        "object_ref": object_ref,
                        "modifier_name": modifier_name,
                        "modifier_ref": modifier_ref, 
                        "node_group": node_group,
                        "is_parent_node": object_ref.shaderverse.is_parent_node
                    }
                    geometry_node_objects.append(node_object)
        return geometry_node_objects



    collection = []

    def is_item_restriction_found(attributes, restrictions):
        found = False
        for attribute in attributes.values():
            for restriction in restrictions:
                if restriction == attribute:
                    found = True
                return found
        return found



        # attributes = {}
        # for blender_collection in blender_objects:
        #     attribute_names = []
        #     attribute_weights = []    
        #     for blender_object in blender_collection["objects"]:
        #         exclude = False
        #         # exclude if it has a restriction that isn't already in the set of attributes
        #         if (len(blender_object["restrictions"]) > 0) and ( is_item_missing_restrictions(attributes, blender_object["restrictions"])):
        #             exclude = True
                
        #         if not exclude:
        #             attribute_names.append(blender_object["name"])
        #             attribute_weights.append(blender_object["weight"])

        #     # select the trait from this collection
        #     attribute_value = random.choices(attribute_names, weights=tuple(attribute_weights), k=1)

        #     attributes[blender_collection["collection name"]] =  attribute_value[0]






    def get_object_restrictions(self, obj):
        restrictions = []
        for item in obj.shaderverse.restrictions:
            restrictions.append(item.restriction.name)
        return restrictions

    def select_object_from_collection(self, collection):
        collection_object_names = []
        collection_object_weights = []
        active_geometry_node_objects = []
        
        for obj in collection.objects:
            restrictions = self.get_object_restrictions(obj)

            # TODO Check this logic works
            print(self.attributes)

            if (len(restrictions) < 1) or (self.is_item_restriction_found(self.attributes, restrictions)):
            
                collection_object_names.append(obj.name)
                collection_object_weights.append(obj.shaderverse.weight)
            
        selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        return bpy.data.objects[selected_object_name]


    def select_collection_based_on_object(self, collection):
        collection_objects = []
        collection_object_weights = []
        
        for child_collection in collection.children:
            obj = child_collection.objects[0]
            collection_objects.append({"object_name": obj.name, "collection_name": child_collection.name})
            collection_object_weights.append(obj.shaderverse.weight)
        
        collection_object_names = [d['object_name'] for d in collection_objects]
        selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        selected_collection_name = next(item["collection_name"] for item in collection_objects if item["object_name"] == selected_object_name)
        return bpy.data.collections[selected_collection_name]


    def generate_metadata(self, node_object):
        modifier_name = node_object["modifier_name"]
        modifier = node_object["modifier_ref"]
        node_group = modifier.node_group
        node_group_name = node_group.name
        object_name = node_object["object_name"]
        object_ref = bpy.data.objects[object_name]
    

        node_group_attributes = { 
            "node_group_name": node_group_name,
            "object_name": object_name,
            "is_parent_node": object_ref.shaderverse.is_parent_node,
            "attributes": {}
        }


        for item in node_group.inputs.items():
            item_name = item[0]
            item_ref = item[1]
            
            item_type = item_ref.type
            item_input_id = item_ref.identifier 
            parent_attribute_value  = None
            is_parent_node = node_object["is_parent_node"]

            if (not is_parent_node):
                
                for item in self.collection:
                    if item["is_parent_node"]:
                        attributes = item["attributes"]
                        for key in attributes:
                            if item_name == key:
                                parent_attribute_value = attributes[key]

            is_generator_input = is_parent_node or parent_attribute_value

            if is_generator_input:

                if item_type == "VALUE":
                    precision = 0.01
                    generated_value = parent_attribute_value if parent_attribute_value else self.generate_random_range(item_ref=item_ref, precision=precision)
                    modifier[item_input_id] = generated_value
                    node_group_attributes["attributes"][item_name] = generated_value

                if item_type == "INT":
                    precision = 1
                    generated_value = parent_attribute_value if parent_attribute_value else self.generate_random_range(item_ref=item_ref, precision=precision)
                    modifier[item_input_id] = generated_value
                    node_group_attributes["attributes"][item_name] = generated_value
                    
                if item_type == "MATERIAL":
                    # look for a collection with the same name of the material input
                    material_collection = bpy.data.collections[item_name]
                    if material_collection:
                        selected_object = self.select_object_from_collection(collection=material_collection)
                        selected_material_name = selected_object.material_slots[0].name
                        selected_material = parent_attribute_value if parent_attribute_value else bpy.data.materials[selected_material_name]
                        if selected_material:
                            modifier[item_input_id] = selected_material
                            node_group_attributes["attributes"][item_name] = selected_material.id_data

                if item_type == "OBJECT":
                    object_collection = bpy.data.collections[item_name]
                    if object_collection:
                        selected_object = parent_attribute_value if parent_attribute_value else self.select_object_from_collection(collection=object_collection)
                        modifier[item_input_id] = selected_object
                        node_group_attributes["attributes"][item_name] = selected_object.id_data
                
                if item_type == "COLLECTION":
                    object_collection = bpy.data.collections[item_name]
                    if object_collection:
                        selected_object = parent_attribute_value if parent_attribute_value else self.select_collection_based_on_object(collection=object_collection)
                        modifier[item_input_id] = selected_object
                        node_group_attributes["attributes"][item_name] = selected_object.id_data
                        
        if not parent_attribute_value:
            self.collection.append(node_group_attributes)



    # @classmethod 
    # def poll(cls, context):
    #     ob = context.active_object
    #     return ob and ob.type == 'MESH'

    def format_value(self, item):
        if hasattr(item, "name"):
            return item.name
        if type(item) is float:
            return "{:.2f}".format(item)
        if type(item) is int:
            return "{}".format(item)
        else: 
            return item
    
    def set_attributes(self):
        for node_object in self.active_geometry_node_objects:

            collection_item = next((item for item in self.collection if item["object_name"] == node_object["object_name"]), None)
            if collection_item:
                attributes = collection_item["attributes"]
                for key in attributes:
                    value = self.format_value(attributes[key])
                    attribute_data = {
                        "trait_type": key,
                        "value": value
                    }
                    self.attributes.append(attribute_data)
        bpy.context.scene.shaderverse.generated_metadata = json.dumps(self.attributes)

    def get_active_geometry_node_objects(self, node_group):
        geometry_nodes_objects = []
        node_object_ref = node_group["object_ref"]
        geometry_nodes_objects += self.find_geometry_nodes(node_object_ref)

        collection_item = next(item for item in self.collection if item["object_name"] == node_group["object_name"])


        for data_path in collection_item["attributes"].values():
            if hasattr(data_path, "name"):
                if data_path.name in bpy.data.materials:
                    continue 
                elif data_path.name in bpy.data.objects:
                    geometry_nodes_objects += self.find_geometry_nodes(data_path)
                    for object_ref in data_path.children:
                        geometry_nodes_objects += self.find_geometry_nodes(object_ref) 
                elif data_path.name in bpy.data.collections:
                    for child_node in data_path.objects.items():
                        object_ref = child_node[1]
                        geometry_nodes_objects += self.find_geometry_nodes(object_ref)
            

        return geometry_nodes_objects
    
    def update_mesh(self, node_object):
        self.generate_metadata(node_object=node_object)
        object_name = node_object["object_name"]
        object_ref = bpy.data.objects[object_name]
        mesh_name = object_ref.data.name
        mesh = bpy.data.meshes[mesh_name]
        mesh.update()

    

    def set_parent_node(self):
        for node_object in self.geometry_node_objects:
            # update the parent nodes first
            if node_object["is_parent_node"]:
                self.parent_node = node_object
                bpy.context.scene.shaderverse.parent_node.modifier_name = node_object["modifier_name"]
                bpy.context.scene.shaderverse.parent_node.node_group = node_object["node_group"]
                object_name = node_object["object_name"]
                bpy.context.scene.shaderverse.parent_node.object = bpy.data.objects[object_name]
                

    def execute(self, context):
        self.geometry_node_objects = []
        self.collection = []
        self.attributes = []

        # run a custom script before generation
        if bpy.context.scene.shaderverse.pre_generation_script and bpy.context.scene.shaderverse.enable_pre_generation_script:
            exec(compile(bpy.context.scene.shaderverse.pre_generation_script.as_string(), 'textblock', 'exec'))

        for obj in self.all_objects:
            object_name = obj[0]
            object_ref = obj[1]
            self.geometry_node_objects += self.find_geometry_nodes(object_ref)

        self.set_parent_node()

        for node_object in self.geometry_node_objects:
            # update the parent nodes first
            if node_object["is_parent_node"]:
                self.update_mesh(node_object)

        for node_object in self.geometry_node_objects:
            if not node_object["is_parent_node"]:
                self.update_mesh(node_object)

        # if object_ref.shaderverse.parent_node save metadata for all children
        
        
        # print(self.collection)
        self.active_geometry_node_objects = []
        for node_object in self.geometry_node_objects:
            if node_object["is_parent_node"]: 
                self.active_geometry_node_objects += self.get_active_geometry_node_objects(node_object)
        
        self.set_attributes()

        print(self.attributes)

        # run a custom script after generation
        if bpy.context.scene.shaderverse.post_generation_script and bpy.context.scene.shaderverse.enable_post_generation_script:
            exec(compile(bpy.context.scene.shaderverse.post_generation_script.as_string(), 'textblock', 'exec'))


        return {'FINISHED'}


# class SHADERVERSE_PT_generate(bpy.types.Panel):
#     """Shaderverse generator button panel"""
#     bl_label = "Shaderverse"
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'WINDOW'
#     bl_category = "Tool" 

#     def draw(self, context):
#         layout = self.layout
#         row = layout.row()

#         shaderverse_generate = SHADERVERSE_OT_generate

#         row.operator(shaderverse_generate.bl_idname, text=shaderverse_generate.bl_label, icon_value=custom_icons["custom_icon"].icon_id)


# class SHADERVERSE_OT_start_server(bpy.types.Operator):
#     """Generate new metadata and NFT preview"""
#     bl_idname = "shaderverse.start_server"
#     bl_label = "Start Server"
#     bl_options = {'REGISTER', 'UNDO'}


#     def execute(self, context) -> typing.Set[str]:
#         server.Server.start_threads()
        
#         # print("Waiting for threads to finish...")

#         # for t in self.threads:
#         #     t.join()

#         return {'FINISHED'}


class SHADERVERSE_OT_live_preview(bpy.types.Operator):
    
    """ Live preview """
    bl_idname = "shaderverse.live_preview"
    bl_label = "Live Preview"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from . import server
        context = bpy.context
        server.start_live_preview()
        return {'FINISHED'}

class SHADERVERSE_OT_stop_generator(bpy.types.Operator):
    
    """ Stop the shaderverse generator """
    bl_idname = "shaderverse.stop_generator"
    bl_label = "Stop Server Generator"
    bl_options = {'REGISTER'}

    
    def execute(self, context):
        from . import server
        context = bpy.context
        print("stopping generator")
        server.kill_fastapi()
        return {'FINISHED'}



def handle_adding_sites_to_path():
    home_path =  pathlib.Path.home()
    # user_base = os.path.join(home_path, ".shaderverse", "python")
    # user_site =  os.path.join(user_base, "site-packages")
    user_base = os.path.realpath(site.USER_BASE)
    user_site = os.path.realpath(site.USER_SITE)

    sys.path.append(user_base)
    sys.path.append(user_site)




