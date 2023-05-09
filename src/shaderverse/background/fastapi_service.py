import bpy
from .service import Service
from pathlib import Path


class FastapiService(Service):
    port = "8118"  # you don't need to generate this from ID or anything - just make sure the port is valid and unoccupied
    blender_binary_path = bpy.app.binary_path
    blend_file = bpy.data.filepath
    script_path = Path(__file__).parent.absolute()
    api_path = Path(Path(script_path).parent.absolute(), "api", "main.py")

    def __init__(self):
        self.cmd = [self.blender_binary_path, self.blend_file, "--background",  "--python", str(self.api_path), "--", "--port", self.port]
        super().__init__(self.cmd)
        self.execute()