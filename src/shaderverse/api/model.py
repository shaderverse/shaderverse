
from pydantic import UUID4, BaseModel
from enum import Enum, IntEnum
class BlenderData(BaseModel):
    blend_file: str = None
    blender_binary_path: str = None
    next_port: int 

class Session(BaseModel):
    id: UUID4
    port: int 
    blend_file: str = None

class SessionStatus(str, Enum):
    ready = 'ready'
    running = 'running'
    finished = 'finished'

class Action(str, Enum):
    render_glb = 'render_glb'


class SessionData(BaseModel):
    status: SessionStatus = "ready"
    total_count: int = 0
    current_count: int = 0
    current_id: int = 0