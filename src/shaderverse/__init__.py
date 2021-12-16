import bpy
import bpy.utils.previews
import os
import random


bl_info = {
    "name": "Shaderverse",
    "description": "Create parametricly driven NFTs using Geometry Nodes",
    "author": "Michael Gold",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "Object > Modifier",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "Shaderverse",
    "tracker_url": "https://github.com/shaderverse/shaderverse",
    "support": "COMMUNITY",
    "category": "NFT",
}


custom_icons = None

class DependencyListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    # name: bpy.props.StringProperty(
    #        name="Name",
    #        description="A name for this item",
    #        default="Untitled")

    dependency: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        description="Only make this object available for selection if one of the objects in this list have been selected"
    )

    # random_prop: bpy.props.StringProperty(
    #        name="Any other property you want",
    #        description="",
    #        default="")


class MY_UL_List(bpy.types.UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.dependency.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)


class LIST_OT_NewItem(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "shaderverse_dependency_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.object.shaderverse.dependency_list.add()

        return{'FINISHED'}


class LIST_OT_DeleteItem(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "shaderverse_dependency_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.object.shaderverse.dependency_list

    def execute(self, context):
        dependency_list = context.object.shaderverse.dependency_list
        index = context.object.shaderverse.dependency_list_index

        dependency_list.remove(index)
        context.object.shaderverse.dependency_list_index = min(max(0, index - 1), len(dependency_list) - 1)

        return{'FINISHED'}


class LIST_OT_MoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "shaderverse_dependency_list.move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.object.shaderverse.dependency_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.object.shaderverse.dependency_list_index
        list_length = len(bpy.context.object.shaderverse.dependency_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.object.shaderverse.dependency_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        dependency_list = context.object.shaderverse.dependency_list
        index = context.object.shaderverse.dependency_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        dependency_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}




class OBJECT_PG_shaderverse(bpy.types.PropertyGroup):
    #NOTE: read documentation about 'props' to see them and their keyword arguments
    #builtin float (variable)property that blender understands
    weight: bpy.props.FloatProperty(name='float value', soft_min=0, soft_max=1)

    dependency_list: bpy.props.CollectionProperty(type=DependencyListItem)
    
    dependency_list_index: bpy.props.IntProperty(name = "Index for shaderverse.dependency_list", default = 0)


    #builtin integer (variable)property
    int_slider: bpy.props.IntProperty(name='int value', soft_min=0, soft_max=10)
    #builting boolean (variable)property
    bool_toggle: bpy.props.BoolProperty(name='bool toggle')
    #builting string (variable)property
    string_field: bpy.props.StringProperty(name='string field')
    


class OBJECT_PT_shaderverse(bpy.types.Panel):
    bl_label = "Shaderverse"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 
    bl_context = "object"


    def draw(self, context):
        pass
        # You can set the property values that should be used when the user
        # presses the button in the UI.


        #add a new row with multiple elements in a column
        # subrow = layout.row(align=True)
        # #add a toggle
        # subrow.prop(context.object.shaderverse, 'bool_toggle')
        # #add an int slider
        # subrow.prop(context.object.shaderverse, 'int_slider')
        # #add a custom text field in the usual layout
        # layout.prop(context.object.shaderverse, 'string_field')
        #NOTE: for more layout things see the types.UILayout in the documentation
    
        
        
        # mat = context.material
        # ob = context.object
        # slot = context.material_slot
        # space = context.space_data
        # split = layout.split()
        
        # if ob:
        #     is_sortable = len(ob.material_slots) > 1
        #     rows = 3
        #     if (is_sortable):
        #         rows = 4

        #     row = layout.row()

        #     row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

        #     col = row.column(align=True)
        #     col.operator("object.material_slot_add", icon='ADD', text="")
        #     col.operator("object.material_slot_remove", icon='REMOVE', text="")
        #     col.separator()
        #     col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        #     if is_sortable:
        #         col.separator()

        #         col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
        #         col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        #     if ob.mode == 'EDIT':
        #         row = layout.row(align=True)
        #         row.operator("object.material_slot_assign", text="Assign")
        #         row.operator("object.material_slot_select", text="Select")
        #         row.operator("object.material_slot_deselect", text="Deselect")

        # row = layout.row()

        # if ob:
        #     row.template_ID(ob, "active_material", new="material.new")

        #     if slot:
        #         icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
        #         row.prop(slot, "link", text="", icon=icon_link, icon_only=True)

        # elif mat:
        #     split.template_ID(space, "pin_id")
        #     split.separator()


class OBJECT_PT_shaderverse_weights(bpy.types.Panel):
    bl_parent_id = "OBJECT_PT_shaderverse"
    bl_label = "Weight"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 
    bl_context = "object"


    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 

        subrow = layout.row(align=True)
        this_context = context.object
        #add a label to the UI
        # layout.label(text="Weighted chance of choosing this attribute")
        subrow.prop(this_context.shaderverse, 'weight', text="Weight Amount")

        #add a new row with multiple elements in a column
        # subrow = layout.row(align=True)
        # #add a toggle
        # subrow.prop(context.object.shaderverse, 'bool_toggle')
        # #add an int slider
        # subrow.prop(context.object.shaderverse, 'int_slider')
        # #add a custom text field in the usual layout
        # layout.prop(context.object.shaderverse, 'string_field')
        #NOTE: for more layout things see the types.UILayout in the documentation
        
        

class OBJECT_PT_shaderverse_dependency_list(bpy.types.Panel):
    bl_parent_id = "OBJECT_PT_shaderverse"
    bl_label = "Limit to these objects"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 
    bl_context = "object"


    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        this_context = context.object


        #add a new row with multiple elements in a column
        # subrow = layout.row(align=True)
        # #add a toggle
        # subrow.prop(context.object.shaderverse, 'bool_toggle')
        # #add an int slider
        # subrow.prop(context.object.shaderverse, 'int_slider')
        # #add a custom text field in the usual layout
        # layout.prop(context.object.shaderverse, 'string_field')
        #NOTE: for more layout things see the types.UILayout in the documentation
        
        
        row = layout.row()
        row.template_list("MY_UL_List", "The_List", this_context.shaderverse,
                          "dependency_list", this_context.shaderverse, "dependency_list_index")

        row = layout.row()
        row.operator('shaderverse_dependency_list.new_item', text='NEW')
        row.operator('shaderverse_dependency_list.delete_item', text='REMOVE')
        row.operator('shaderverse_dependency_list.move_item', text='UP').direction = 'UP'
        row.operator('shaderverse_dependency_list.move_item', text='DOWN').direction = 'DOWN'

        if this_context.shaderverse.dependency_list_index >= 0 and this_context.shaderverse.dependency_list:
            item = this_context.shaderverse.dependency_list[this_context.shaderverse.dependency_list_index]

            row = layout.row()
            row.prop(item, "dependency")
            # row.prop(item, "random_prop")


class ShaderverseNodeTreeInterfacePanel:
    def draw_attributes (self, context, in_out, sockets_propname, active_socket_propname):
        layout = self.layout

        snode = context.space_data
        tree = snode.edit_tree
        sockets = getattr(tree, sockets_propname)
        active_socket_index = getattr(tree, active_socket_propname)
        active_socket = sockets[active_socket_index] if active_socket_index >= 0 else None

        split = layout.row()

        split.template_list("NODE_UL_interface_sockets", in_out, tree, sockets_propname, tree, active_socket_propname)

        ops_col = split.column()

        add_remove_col = ops_col.column(align=True)
        props = add_remove_col.operator("node.tree_socket_add", icon='ADD', text="")
        props.in_out = in_out
        props = add_remove_col.operator("node.tree_socket_remove", icon='REMOVE', text="")
        props.in_out = in_out

        ops_col.separator()

        bpy.data.objects["Cube"].modifiers["GeometryNodes"]["Input_3"]

        # up_down_col = ops_col.column(align=True)
        # props = up_down_col.operator("node.tree_socket_move", icon='TRIA_UP', text="")
        # props.in_out = in_out
        # props.direction = 'UP'
        # props = up_down_col.operator("node.tree_socket_move", icon='TRIA_DOWN', text="")
        # props.in_out = in_out
        # props.direction = 'DOWN'

        if active_socket is not None:
            # Mimicking property split.
            layout.use_property_split = False
            layout.use_property_decorate = False
            layout_row = layout.row(align=True)
            layout_split = layout_row.split(factor=0.4, align=True)

            label_column = layout_split.column(align=True)
            label_column.alignment = 'RIGHT'
            # Menu to change the socket type.
            label_column.label(text="Type")

            property_row = layout_split.row(align=True)
            props = property_row.operator_menu_enum(
                "node.tree_socket_change_type",
                "socket_type",
                text=active_socket.bl_label if active_socket.bl_label else active_socket.bl_idname
                )
            props.in_out = in_out

            layout.use_property_split = True
            layout.use_property_decorate = False

            layout.prop(active_socket, "name")
            # Display descriptions only for Geometry Nodes, since it's only used in the modifier panel.
            if tree.type == 'GEOMETRY':
                layout.prop(active_socket, "description")
                field_socket_prefixes = {
                    "NodeSocketInt", "NodeSocketColor", "NodeSocketVector", "NodeSocketBool", "NodeSocketFloat"}
                is_field_type = any(active_socket.bl_socket_idname.startswith(prefix) for prefix in field_socket_prefixes)
                if in_out == "OUT" and is_field_type:
                    layout.prop(active_socket, "attribute_domain")
            active_socket.draw(context, layout)


class NODE_PT_node_tree_interface_inputs(ShaderverseNodeTreeInterfacePanel, bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Group"
    bl_label = "Inputs"

    @classmethod
    def poll(cls, context):
        snode = context.space_data
        return snode.edit_tree is not None

    def draw(self, context):
        self.draw_socket_list(context, "IN", "inputs", "active_input")



class OBJECT_OT_shaderverse_generate(bpy.types.Operator):
    """Generate new metadata and NFT preview"""
    bl_idname = "shaderverse.generate"
    bl_label = "Generate NFT"
    bl_options = {'REGISTER', 'UNDO'}

    def generate_random_range(self, start, stop, precision):
        start = round(start / precision)
        stop = round(stop / precision)
        generated_int = random.randrange(start, stop)
        return generated_int * precision

    # mesh = bpy.data.meshes['Plane']

    # modifier = bpy.context.object.modifiers["GeometryNodes"]
    # node_group = modifier.node_group


    all_objects =  None

    geometry_node_objects = []

    def __init__(self):
        self.all_objects = bpy.data.objects.items()

    def find_geometry_nodes(self):

        for obj in self.all_objects:
            object_name = obj[0]
            object_ref = obj[1]
            object_modifiers = object_ref.modifiers.items()

            for modifier in object_modifiers:
                modifier_name = modifier[0]
                modifier_ref = modifier[1]
                if hasattr(modifier_ref, "node_group"):
                    node_group = modifier_ref.node_group
                
                    if node_group.type == "GEOMETRY":
                        node_object = {
                            "mesh_name": object_name,
                            "mesh_ref": object_ref,
                            "modifier_name": modifier_name,
                            "modifier_ref": modifier_ref, 
                        }
                        self.geometry_node_objects.append(node_object)



    collection = []

    def select_object_from_collection(self, collection):
        collection_object_names = []
        collection_object_weights = []
        
        for obj in collection.objects:
            collection_object_names.append(obj.name)
            collection_object_weights.append(obj.shaderverse.weight)
        selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        return bpy.data.objects[selected_object_name]


    def generate_metadata(self, node_object):
        modifier_name = node_object["modifier_name"]
        modifier = node_object["modifier_ref"]
        node_group = modifier.node_group
        node_group_name = node_group.name

        node_group_attributes = { 
            "node_group_name": node_group_name,
            "attributes": {}
        }


        for item in node_group.inputs.items():
            item_name = item[0]
            item_ref = item[1]
            
            item_type = item_ref.type
            item_input_id = item_ref.identifier 
        
            
            if item_type == "VALUE":
                item_min = item_ref.min_value
                item_max = item_ref.max_value
                precision = 0.01
                generated_value = self.generate_random_range(start=item_min, stop=item_max, precision=precision)
                # print("{} = {}".format(item_name, generated_value))
                modifier[item_input_id] = generated_value
                node_group_attributes["attributes"][item_name] = generated_value
                

            if item_type == "MATERIAL":
                # look for a collection with the same name of the material input
                material_collection = bpy.data.collections[item_name]
                if material_collection:
                    selected_object = self.select_object_from_collection(collection=material_collection)
                    selected_material_name = selected_object.material_slots[0].name
                    selected_material = bpy.data.materials[selected_material_name]
                    if selected_material:
                        modifier[item_input_id] = selected_material
                        node_group_attributes["attributes"][item_name] = selected_material.id_data

            if item_type == "OBJECT":
                object_collection = bpy.data.collections[item_name]
                if object_collection:
                    selected_object = self.select_object_from_collection(collection=object_collection)
                    modifier[item_input_id] = selected_object
                    node_group_attributes["attributes"][item_name] = selected_object.id_data
                

        self.collection.append(node_group_attributes)



    @classmethod 
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type == 'MESH'

    def execute(self, context):
        self.find_geometry_nodes()

        for node_object in self.geometry_node_objects:
            self.generate_metadata(node_object=node_object)
            mesh_name = node_object["mesh_name"]
            mesh = bpy.data.meshes[mesh_name]
            mesh.update()


        return {'FINISHED'}


class OBJECT_PT_shaderverse_generate(bpy.types.Panel):
    """Shaderverse generator button panel"""
    bl_label = "Shaderverse"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tool" 

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()

        # here is your operator
        shaderverse_generate = OBJECT_OT_shaderverse_generate

        row.operator(shaderverse_generate.bl_idname, text= shaderverse_generate.bl_label, icon_value=custom_icons["custom_icon"].icon_id)

        


classes = [
    DependencyListItem,
    OBJECT_PT_shaderverse,
    OBJECT_PT_shaderverse_weights,
    OBJECT_PT_shaderverse_dependency_list,

    OBJECT_PG_shaderverse,
    MY_UL_List,
    LIST_OT_NewItem,
    LIST_OT_DeleteItem,
    LIST_OT_MoveItem,
    OBJECT_OT_shaderverse_generate,
    OBJECT_PT_shaderverse_generate
]


def register():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    addon_path =  os.path.dirname(__file__)
    icons_dir = os.path.join(addon_path, "icons")
    
    custom_icons.load("custom_icon", os.path.join(icons_dir, "icon.png"), 'IMAGE')
   

    for this_class in classes:
        bpy.utils.register_class(this_class)

    #adds the property group class to the object context (instantiates it)
    bpy.types.Object.shaderverse = bpy.props.PointerProperty(type=OBJECT_PG_shaderverse)


#same as register but backwards, deleting references
def unregister():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    #delete the custom property pointer
    #NOTE: this is different from its accessor, as that is a read/write only
    #to delete this we have to delete its pointer, just like how we added it
    del bpy.types.Object.shaderverse 

    for this_class in classes:
        bpy.utils.unregister_class(this_class)  

#a quick line to autorun the script from the text editor when we hit 'run script'
if __name__ == '__main__':
    register()


