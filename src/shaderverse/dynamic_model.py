from shaderverse.mesh import Mesh, NodeInput
from pydantic import BaseModel, create_model, Field, validator
import logging
from shaderverse.model import Attribute
from typing import List

def create_input_attribute_model(model_schema: list[NodeInput]) -> BaseModel:
    """
    Creates a dynamic Pydantic model for an attribute based on the given model schema.
    """

    fields = {}

    for field_schema in model_schema:
        name = field_schema.trait_type

        if field_schema.value_type == "tuple":
            if field_schema.allowed_values:
                fields[name] = (str, Field(..., description=name, example=field_schema.allowed_values[0], enum=field_schema.allowed_values))
            else:
                fields[name] = (str, Field(..., description=name, example="example string"))

        elif field_schema.value_type == "int":
            example = field_schema.min_value if field_schema.min_value else 0
            fields[name] = (int, Field(..., description=name, example=example, ge=field_schema.min_value, le=field_schema.max_value))

        elif field_schema.value_type == "float":
            example = field_schema.min_value if field_schema.min_value else 0.0
            fields[name] = (float, Field(..., description=name, example=example, ge=field_schema.min_value, le=field_schema.max_value))

    return create_model("DynamicAttributeModel", **fields)

mesh = Mesh()
model_schema: list[NodeInput] = []
try:
    if mesh.get_main_node_group():
        model_schema = mesh.get_schema()
except Exception as e:
    logging.info(f"Could not get schema from mesh: {e}")   
AttributeModel = create_input_attribute_model(model_schema)

class Metadata(BaseModel):
    id: int = None
    filename: str = None
    attributes: AttributeModel = None
    json_attributes: list[Attribute] = None
    rendered_glb_url: str = None
    rendered_usdz_url: str = None
    rendered_file_url: str = None

    @validator("attributes")
    def validate_not_in_schema(cls, attributes: AttributeModel):
        for attribute in attributes.dict().keys():
            value = attributes.dict()[attribute]
            allowed_values = attributes.schema()["properties"][attribute]["enum"]
            if allowed_values and len(allowed_values) > 0:
                if value not in attributes.schema()["properties"][attribute]["enum"]:
                    raise ValueError(f"Value: {value} is not a valid option for {attribute}")
            
        return attributes


    def generate_json_attributes(self):

        attribute_list: list[Attribute] = []
        attributes_dict = self.attributes.dict()
        trait_types = list(attributes_dict.keys())
        trait_values = list(attributes_dict.values())

        for i in range(len(trait_types)):
            attribute = Attribute(trait_type= trait_types[i], value= trait_values[i])
            attribute_list.append(attribute)

        self.json_attributes = attribute_list
    
    def set_attributes_from_json(self):
        attributes = {}
        for attribute in self.json_attributes:
            attributes[attribute.trait_type] = attribute.value

        self.attributes = AttributeModel(**attributes)

class MetadataList(BaseModel):
    metadata_list: List[Metadata] = None
