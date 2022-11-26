import bpy
import json
import random
import shaderverse

class NFT():
    # metadata = {}
    # directory = ""
    # id: int

    # def __init__(self):
    #     pass

    # def generate_metadata(self):
    #     pass

    # def load_metadata(self, filename: str):
    #     pass

    # def export_metadata(self):
    #     pass

    # def render_preview(self):
    #     pass

    # def render_glb(self):
    #     pass

    # def render_jpeg(self):
    #     pass



    all_objects =  None
    attributes = []

    geometry_node_objects = []
    parent_node = None
    node_group_attributes = {}
    

    def __init__(self):
        # run a custom script before intialization
        self.all_objects = bpy.data.objects.values()
        self.geometry_node_objects = []
        self.collection = []
        self.attributes = []

    def generate_random_range(self, item_ref: bpy.types.NodeSocketInterfaceFloat, precision):
        start = item_ref.min_value
        stop = item_ref.max_value
        start = round(start / precision)
        stop = round(stop / precision)
        generated_int = random.randint(start, stop)
        return generated_int * precision


    def find_geometry_nodes(self, object_ref: bpy.types.Object):

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

    def update_geonodes_from_metadata(self):
        """find all geonodes then update the node object based on the generated metadata"""

        # find all geonode objects
        for object_ref in self.all_objects:
            self.geometry_node_objects += self.find_geometry_nodes(object_ref)

        # update all geonodes with metadata
        for node_object in self.geometry_node_objects:
            self.update_mesh(node_object)

    

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

    def select_object_from_collection(self, collection: bpy.types.Collection):
        collection_object_names = []
        collection_object_weights = []
        active_geometry_node_objects = []
        
        for obj in collection.objects:
            shaderverse_properties: shaderverse.blender.SHADERVERSE_PG_main = obj.shaderverse 
            restrictions = shaderverse_properties.restrictions

            if (len(restrictions) < 1) or (self.is_item_restriction_found(restrictions)):
                collection_object_names.append(obj.name)
                collection_object_weights.append(shaderverse_properties.weight)

        try:    
            selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        except IndexError as error:
            raise Exception(f"{error}: Could not find at least one valid object in {collection.name}")
        return bpy.data.objects[selected_object_name]

    def get_metadata_object_from_collection(self, collection: bpy.types.Collection):
        """ Return the first object in a collection that has either a custom weight or restriction """
        for obj in collection.all_objects:
            shaderverse_properties: shaderverse.blender.SHADERVERSE_PG_main = obj.shaderverse 
            if shaderverse_properties.weight < 1 or (len (shaderverse_properties.restrictions) > 0):
                return obj
        return collection.all_objects[0]

    def select_collection_based_on_object(self, collection: bpy.types.Collection):
        collection_objects = []
        collection_object_weights = []
        
        for child_collection in collection.children:
            obj = self.get_metadata_object_from_collection(child_collection)
            shaderverse_properties: shaderverse.blender.SHADERVERSE_PG_main = obj.shaderverse 
            restrictions = shaderverse_properties.restrictions

            if (len(restrictions) < 1) or (self.is_item_restriction_found(restrictions)):

                collection_objects.append({"object_name": obj.name, "collection_name": child_collection.name})
                collection_object_weights.append(shaderverse_properties.weight)
        
        collection_object_names = [d['object_name'] for d in collection_objects]
        selected_object_name = random.choices(collection_object_names, weights=tuple(collection_object_weights), k=1)[0]
        selected_collection_name = next(item["collection_name"] for item in collection_objects if item["object_name"] == selected_object_name)
        return bpy.data.collections[selected_collection_name]

    def is_parent_node(self, current_node_object_name):
        return current_node_object_name == bpy.context.scene.shaderverse.main_geonodes_object.name

    def is_collection_none(self, collection):
        for obj in collection.all_objects.values():
            shaderverse_properties: shaderverse.blender.SHADERVERSE_PG_main = obj.shaderverse 
            if shaderverse_properties.metadata_is_none:
                return True
        return False

    def generate_metadata(self, node_object):
        modifier_name = node_object["modifier_name"]
        modifier = node_object["modifier_ref"]
        node_group: bpy.types.GeometryNodeTree = modifier.node_group
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
            shaderverse_properties: shaderverse.blender.SHADERVERSE_PG_main = obj.shaderverse 
            if shaderverse_properties.match_trait(trait_type, trait_value):
                matched_object = obj
                return matched_object
        return matched_object

    def match_collection_from_metadata(self, trait_type, trait_value):
        matched_collection = None
        collection = bpy.data.collections[trait_type]

        for collection in bpy.data.collections:
            if collection.name.strip().lower() == trait_value.strip().lower():
                matched_collection = collection
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

                if item_type == "STRING":
                    modifier[item_input_id] = str(trait_value)
            
                        

    def format_value(self, item: bpy.types.Object):
        if hasattr(item, "shaderverse"):
            #TODO handle prefix values for material names
            shaderverse_properties: shaderverse.blender.SHADERVERSE_PG_main = item.shaderverse 
            return shaderverse_properties.get_trait_value()
        if hasattr(item, "name"):
            return item.name
        if type(item) is float:
            return "{:.2f}".format(item)
        if type(item) is int:
            return "{}".format(item)
        else: 
            return item
    
    def set_attributes(self):
        print(self.collection)
        attributes = self.collection[0]["attributes"]
        for key in attributes:
            value = self.format_value(attributes[key])
            attribute_data = {
                "trait_type": key,
                "value": value
            }
            self.attributes.append(attribute_data)

        bpy.context.scene.shaderverse.generated_metadata = json.dumps(self.attributes)

    def run_metadata_generator(self):
        """find all geometry nodes and run metadata generator for those nodes """
        main_geonodes_object: bpy.types.Object =  bpy.context.scene.shaderverse.main_geonodes_object
        main_geonodes = self.find_geometry_nodes(main_geonodes_object)
        for node in main_geonodes:
            self.generate_metadata(node)

        self.set_attributes()


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
            

    def is_animated_collection(self, collection: bpy.types.Collection):
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
            
    def copy_to_animated_objects(self, other: bpy.types.Collection):
        collection = bpy.data.collections["Animated Objects"]
        collection.children.link(other.copy())

    def make_animated_objects_visible(self):
        for item in bpy.data.collections['Animated Objects'].all_objects:
            if hasattr(item, "shaderverse"):
                item.hide_set(False)   
        animated_objects_collection = bpy.context.scene.view_layers[0].layer_collection.children['Animated Objects']
        for collection in animated_objects_collection.children:
            collection.hide_viewport = False
    
    def run_pre_generation_script(self):
        """run a custom script before intialization if enabled"""
        if bpy.context.scene.shaderverse.pre_generation_script and bpy.context.scene.shaderverse.enable_pre_generation_script:
            exec(compile(bpy.context.scene.shaderverse.pre_generation_script.as_string(), 'textblock', 'exec'))
    
    def run_post_generation_script(self):
        """ run a custom script after generation if enabled """
        if bpy.context.scene.shaderverse.post_generation_script and bpy.context.scene.shaderverse.enable_post_generation_script:
            exec(compile(bpy.context.scene.shaderverse.post_generation_script.as_string(), 'textblock', 'exec'))