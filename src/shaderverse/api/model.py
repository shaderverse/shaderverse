
from pydantic import UUID4, BaseModel

class BlenderData(BaseModel):
    blend_file: str = None
    blender_binary_path: str = None
    next_port: int 

class Session(BaseModel):
    id: UUID4
    port: int 
    blend_file: str = None