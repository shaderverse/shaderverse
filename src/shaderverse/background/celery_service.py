import bpy
from .service import Service
from pathlib import Path

class CeleryService(Service):
    blender_binary_path = bpy.app.binary_path
    blend_file = bpy.data.filepath
    script_path = Path(__file__).parent.absolute()
    api_path = Path(Path(script_path).parent.absolute(), "api", "run_celery.py")

    def __init__(self, workers: int = 4):
        self.workers = workers
        self.cmd = [self.blender_binary_path, self.blend_file, "--background",  "--python", str(self.api_path), "--", "--concurrency", str(self.workers)]
        super().__init__(self.cmd)
        self.execute()