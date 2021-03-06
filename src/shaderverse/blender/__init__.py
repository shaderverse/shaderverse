import bpy
import os
import random
import json
import site
import sys
import os
import pathlib
from ..nft import NFT

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

    
class SHADERVERSE_PG_scene(bpy.types.PropertyGroup):
    generated_metadata: bpy.props.StringProperty(name="Generated Meta Data")

    parent_node: bpy.props.PointerProperty(type=SHADERVERSE_PG_parent_node)

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
        obj.hide_set(False)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.duplicates_make_real()
        try:
            bpy.ops.object.convert(target='MESH')
        except:
            print(f"Could not convert mesh for {obj.name}")

        try:
            bpy.ops.geometry.attribute_convert(mode='UV_MAP')
        except:
            print(f"Could not convert UV MAP for {obj.name}")

    def execute(self, context):
        parent_node_object = context.scene.shaderverse.main_geonodes_object
        self.realize_object(parent_node_object)
        animated_objects = bpy.data.collections['Animated Objects'].all_objects
        for obj in animated_objects:
            self.realize_object(obj)

        return {'FINISHED'}


class SHADERVERSE_OT_generate(bpy.types.Operator):
    """Generate new metadata and NFT preview"""
    bl_idname = "shaderverse.generate"
    bl_label = "Generate NFT"
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
    node_group_attributes = {}

    def __init__(self):
        # run a custom script before intialization
        if bpy.context.scene.shaderverse.pre_generation_script and bpy.context.scene.shaderverse.enable_pre_generation_script:
            exec(compile(bpy.context.scene.shaderverse.pre_generation_script.as_string(), 'textblock', 'exec'))
        self.all_objects = bpy.data.objects.items()
        self.create_animated_objects_collection()
        self.reset_animated_objects()

    def find_geometry_nodes(self, object_ref):

        geometry_node_objects = []
        object_name = object_ref.name

        try:
            object_modifiers = object_ref.modifiers.items()
        except AttributeError as error:
            raise Exception(f"{error}: for {object_name}")

        for modifier in object_modifiers:
            modifier_name = modifier[0]
            modifier_ref = modifier[1]
            if hasattr(modifier_ref, "node_group"):
                node_group = modifier_ref.node_group

                try:
                    if node_group.type == "GEOMETRY":
                        node_object = {
                            "object_name": object_name,
                            "object_ref": object_ref,
                            "modifier_name": modifier_name,
                            "modifier_ref": modifier_ref, 
                            "node_group": node_group,
                            "is_parent_node": self.is_parent_node(current_node_object_name=object_name)
                        }
                        geometry_node_objects.append(node_object)
                except AttributeError as error:
                    raise Exception(f"{error}: Could not find a Node Group type in object: {object_name}. Did you add an empty geometry node modifier?")

        return geometry_node_objects



    collection = []

    def is_item_restriction_found(self, restrictions):
        attributes = self.node_group_attributes["attributes"]
        found = []
        for restriction in restrictions:
            found_restriction = False
            restriction_data = {
                    "trait": restriction.trait,
                    "value": restriction.get_active_field()
                }
            match restriction.get_active_condition():
                case '==':
                    if attributes[restriction_data["trait"]] == restriction_data["value"]:
                        found_restriction = True
                case '!=':
                    if attributes[restriction_data["trait"]] != restriction_data["value"]:
                        found_restriction = True
                case '>':
                    if attributes[restriction_data["trait"]] > restriction_data["value"]:
                        found_restriction = True
                case '<':
                    if attributes[restriction_data["trait"]] < restriction_data["value"]:
                        found_restriction = True
            
            found.append(found_restriction)
        for val in found:
            if val: 
                return True
        return False

    def select_object_from_collection(self, collection):
        collection_object_names = []
        collection_object_weights = []
        active_geometry_node_objects = []
        
        for obj in collection.objects:
            restrictions = obj.shaderverse.restrictions

            if (len(restrictions) < 1) or (self.is_item_restriction_found(restrictions)):
            
                collection_object_names.append(obj.name)
                collection_object_weights.append(obj.shaderverse.weight)

        try:    
            selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        except IndexError as error:
            raise Exception(f"{error}: Could not find at least one valid object in {collection.name}")
        return bpy.data.objects[selected_object_name]

    def get_metadata_object_from_collection(self, collection):
        """ Return the first object in a collection that has either a custom weight or restriction """
        for obj in collection.all_objects:
            if obj.shaderverse.weight < 1 or (len (obj.shaderverse.restrictions) > 0):
                return obj
        return collection.all_objects[0]

    def select_collection_based_on_object(self, collection):
        collection_objects = []
        collection_object_weights = []
        
        for child_collection in collection.children:
            obj = self.get_metadata_object_from_collection(child_collection)
            restrictions = obj.shaderverse.restrictions

            if (len(restrictions) < 1) or (self.is_item_restriction_found(restrictions)):

                collection_objects.append({"object_name": obj.name, "collection_name": child_collection.name})
                collection_object_weights.append(obj.shaderverse.weight)
        
        collection_object_names = [d['object_name'] for d in collection_objects]
        selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        selected_collection_name = next(item["collection_name"] for item in collection_objects if item["object_name"] == selected_object_name)
        return bpy.data.collections[selected_collection_name]

    def is_parent_node(self, current_node_object_name):
        return current_node_object_name == bpy.context.scene.shaderverse.main_geonodes_object.name

    def is_collection_none(self, collection):
        for obj in collection.all_objects.values():
            if obj.shaderverse.metadata_is_none:
                return True
        return False

    def generate_metadata(self, node_object):
        modifier_name = node_object["modifier_name"]
        modifier = node_object["modifier_ref"]
        node_group = modifier.node_group
        node_group_name = node_group.name
        object_name = node_object["object_name"]
        object_ref = bpy.data.objects[object_name]
    

        self.node_group_attributes = { 
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


            if item_type == "VALUE":
                precision = 0.01
                generated_value = self.generate_random_range(item_ref=item_ref, precision=precision)
                self.node_group_attributes["attributes"][item_name] = generated_value

            if item_type == "INT":
                precision = 1
                generated_value = self.generate_random_range(item_ref=item_ref, precision=precision)
                self.node_group_attributes["attributes"][item_name] = generated_value
                
            if item_type == "MATERIAL":
                # look for a collection with the same name of the material input
                try:
                    material_collection = bpy.data.collections[item_name]
                except KeyError as error:
                    raise Exception(f"{error}: Could not find a value for {item_name} in {object_name}. Is {item_name} added as an input in your root geometry node?")

                if material_collection:
                    selected_collection = self.select_object_from_collection(collection=material_collection)
                    selected_material_name = selected_collection.material_slots[0].name
                    selected_material = bpy.data.materials[selected_material_name]
                    if selected_material:
                        self.node_group_attributes["attributes"][item_name] = selected_material.id_data

            if item_type == "OBJECT":
                try:
                    object_collection = bpy.data.collections[item_name]
                except KeyError as error:
                    raise Exception(f"{error}: Could not find a value for {item_name} in {object_name}. Is {item_name} added as an input in your root geometry node?")

                if object_collection:
                    selected_collection = self.select_object_from_collection(collection=object_collection)
                    self.node_group_attributes["attributes"][item_name] = selected_collection.id_data
            
            if item_type == "COLLECTION":
                try:
                    object_collection = bpy.data.collections[item_name]
                except KeyError as error:
                    raise Exception(f"{error}: Could not find a value for {item_name} in {object_name}. Is {item_name} added as an input in your root geometry node?")

                if object_collection:
                    selected_collection = self.select_collection_based_on_object(collection=object_collection)
                    self.node_group_attributes["attributes"][item_name] = "None" if self.is_collection_none(selected_collection.id_data) else selected_collection.id_data
                    if self.is_animated_collection(selected_collection.id_data):
                        self.copy_to_animated_objects(selected_collection.id_data)

        self.collection.append(self.node_group_attributes)


    def match_object_from_metadata(self, trait_type, trait_value):
        matched_object = None
        collection = bpy.data.collections[trait_type]
        for obj in collection.all_objects.values():
            if obj.shaderverse.match_trait(trait_type, trait_value):
                matched_object = obj
                return matched_object
        return matched_object

    def match_collection_from_metadata(self, trait_type, trait_value):
        matched_collection = None
        collection = bpy.data.collections[trait_type]
        for obj in collection.all_objects.values():
            if obj.shaderverse.match_trait(trait_type, trait_value):
                matched_collection = obj.users_collection[0]
                return matched_collection
        return matched_collection


    def set_node_inputs_from_metadata(self, node_object):
        modifier_name = node_object["modifier_name"]
        modifier = node_object["modifier_ref"]
        node_group = modifier.node_group
        node_group_name = node_group.name
        object_name = node_object["object_name"]
        object_ref = bpy.data.objects[object_name]

        metadata = json.loads(bpy.context.scene.shaderverse.generated_metadata)

        for attribute in metadata:
            trait_type = attribute['trait_type']
            trait_value = attribute['value']

            # is this attribute in our node group?
            if trait_type in node_group.inputs.keys():

                item_ref = node_group.inputs[trait_type]

                item_type = item_ref.type
                item_input_id = item_ref.identifier 

                if item_type == "VALUE":
                    modifier[item_input_id] = trait_value

                if item_type == "INT":
                    modifier[item_input_id] = trait_value
                        
                if item_type == "MATERIAL":
                    modifier[item_input_id] = bpy.data.materials[trait_value]

                if item_type == "OBJECT":
                    object_ref = self.match_object_from_metadata(trait_type, trait_value)
                    modifier[item_input_id] = object_ref
                
                if item_type == "COLLECTION":
                    collection_ref = self.match_collection_from_metadata(trait_type, trait_value)
                    modifier[item_input_id] = collection_ref
                        

    def format_value(self, item):
        if hasattr(item, "shaderverse"):
            #TODO handle prefix values for material names
            return item.shaderverse.get_trait_value()
        if hasattr(item, "name"):
            return item.name
        if type(item) is float:
            return "{:.2f}".format(item)
        if type(item) is int:
            return "{}".format(item)
        else: 
            return item
    
    def set_attributes(self):
        attributes = self.collection[0]["attributes"]
        for key in attributes:
            value = self.format_value(attributes[key])
            attribute_data = {
                "trait_type": key,
                "value": value
            }
            self.attributes.append(attribute_data)

        bpy.context.scene.shaderverse.generated_metadata = json.dumps(self.attributes)


    def update_mesh(self, node_object):
        self.set_node_inputs_from_metadata(node_object)
        object_name = node_object["object_name"]
        object_ref = bpy.data.objects[object_name]
        mesh_name = object_ref.data.name
        mesh = bpy.data.meshes[mesh_name]
        mesh.update()

    
    def create_animated_objects_collection(self):
        is_animated_objects_created = bpy.data.collections.find("Animated Objects") >= 0
        if not is_animated_objects_created:
            collection = bpy.data.collections.new("Animated Objects")
            bpy.context.scene.collection.children.link(collection)
            

    def is_animated_collection(self, collection):
        found = False
        for obj in collection.objects:
            if obj.animation_data:
                found = True
                return found
            for child in obj.children_recursive:
                if child.animation_data:
                    found = True
                    return found
        return found
        
    def reset_animated_objects(self):
        animated_objects_collection = bpy.data.collections['Animated Objects']
        for collection in animated_objects_collection.children_recursive:
            animated_objects_collection.children.unlink(collection)
            bpy.data.collections.remove(collection)
            
    def copy_to_animated_objects(self, other):
        collection = bpy.data.collections["Animated Objects"]
        collection.children.link(other.copy())

    def make_animated_objects_visible(self):
        for item in bpy.data.collections['Animated Objects'].all_objects:
            if hasattr(item, "shaderverse"):
                item.hide_set(False)   
        animated_objects_collection = bpy.context.scene.view_layers[0].layer_collection.children['Animated Objects']
        for collection in animated_objects_collection.children:
            collection.hide_viewport = False

    def execute(self, context):
        self.geometry_node_objects = []
        self.collection = []
        self.attributes = []


        for obj in self.all_objects:
            object_name = obj[0]
            object_ref = obj[1]
            self.geometry_node_objects += self.find_geometry_nodes(object_ref)

        main_geonodes_object =  bpy.context.scene.shaderverse.main_geonodes_object

        main_geonodes = self.find_geometry_nodes(main_geonodes_object)
        for node in main_geonodes:
            self.generate_metadata(node)

        self.set_attributes()

        for node_object in self.geometry_node_objects:
            self.update_mesh(node_object)

        
        # run a custom script after generation
        if bpy.context.scene.shaderverse.post_generation_script and bpy.context.scene.shaderverse.enable_post_generation_script:
            exec(compile(bpy.context.scene.shaderverse.post_generation_script.as_string(), 'textblock', 'exec'))
        
        self.make_animated_objects_visible()

        return {'FINISHED'}


class SHADERVERSE_OT_live_preview(bpy.types.Operator):
    
    """ Live preview """
    bl_idname = "shaderverse.live_preview"
    bl_label = "Live Web Preview"
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




