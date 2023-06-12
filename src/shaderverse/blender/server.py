import webbrowser
import bpy
from ..background.celery_service import CeleryService
from ..background.fastapi_service import FastapiService
from shaderverse.blender.tunnel import Tunnel
from pathlib import Path
# from tempfile import gettempdir
from shaderverse.api.utils import get_temporary_directory


celery_workers = 6
celery_service: CeleryService
fastapi_service: FastapiService
tunnel: Tunnel
is_initialized = False

def handle_server_keep_alive():
    """Check the status of the server every 30 seconds"""
    if is_initialized == False:
        print("Server shut down")
        return None
    print(f"fastapi_service: {fastapi_service.status}\n{fastapi_service.result}")
    print(f"celery_service: {celery_service.status}\n{celery_service.result}")
    # print(f"flower_service: {flower_service.status}\n{flower_service.result}")

    if fastapi_service.status == "completed" or celery_service.status == "completed":
        print("Restarting server")
        start_server()
    return 60.0

def delete_temp_db():
    """Delete the temp db file"""
    tempdir = get_temporary_directory()
    db_path = tempdir.joinpath("celerydb.sqlite")
    if db_path.exists():
        db_path.unlink()

def start_server(live_preview: bool = False):
    global is_initialized, fastapi_service, celery_service, tunnel
    if not is_initialized:
        delete_temp_db()
        celery_service = CeleryService(workers=celery_workers)
        fastapi_service = FastapiService()
        api_url = f"http://localhost:{fastapi_service.port}/docs"
        print(f"Starting API on port {fastapi_service.port}")
        print(f"Blend File: {fastapi_service.blend_file} ")
        bpy.app.timers.register(handle_server_keep_alive)
        if live_preview:
            tunnel = Tunnel()
            preview_url = f"https://shaderverse.com/preview/{tunnel.subdomain}"
            bpy.context.scene.shaderverse.preview_url = preview_url
            try:
                webbrowser.open(bpy.context.scene.shaderverse.preview_url)
            except:
                print(f"Unable to open preview url")
        else:
            try:
                webbrowser.open(api_url)
            except:
                print(f"Unable to open api url")
    is_initialized = True

def kill_fastapi():
    global is_initialized
    celery_service.kill()
    fastapi_service.kill()
    is_initialized = False
    
    
def kill_tunnel():
    global is_initialized
    tunnel.kill()
    is_initialized = False

if __name__ == "__main__":
    start_server()