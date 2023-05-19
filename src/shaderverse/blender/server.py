import webbrowser
import bpy
from ..background.celery_service import CeleryService
from ..background.fastapi_service import FastapiService
from shaderverse.blender.tunnel import Tunnel

celery_workers = 1
celery_service: CeleryService
fastapi_service: FastapiService
tunnel: Tunnel
is_initialized = False

def start_server(live_preview: bool = False):
    global is_initialized, fastapi_service, celery_service, tunnel
    if not is_initialized:
        celery_service = CeleryService(workers=celery_workers)
        fastapi_service = FastapiService()
        api_url = f"http://localhost:{fastapi_service.port}/docs"
        print(f"Starting API on port {fastapi_service.port}")
        print(f"Blend File: {fastapi_service.blend_file} ")
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