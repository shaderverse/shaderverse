import webbrowser
import bpy
from shaderverse.api.controller import Proxy
from shaderverse.blender.tunnel import Tunnel
import psutil

proxy: Proxy
tunnel: Tunnel
is_initialized = False


def start_server(live_preview: bool = False):
    global is_initialized, proxy, tunnel
    if not is_initialized:
        proxy = Proxy(blender_binary_path=bpy.app.binary_path, 
                        blend_file=bpy.data.filepath)
        api_url = f"http://localhost:{proxy.port}/docs"
        print(f"Starting API on port {proxy.port}")
        print(f"Blend File: {proxy.blend_file} ")
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

def kill_process_recursively(process):
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def kill_fastapi():
    global is_initialized
    process = psutil.Process(proxy.process.pid)
    kill_process_recursively(process)

    # kill any instantiated blender sessions
    # for key in sessions:
    #     proccess_id = sessions[key].process.pid 
    #     blender_process = psutil.Process(proccess_id)
    #     kill_process_recursively(blender_process)
    #     sessions.pop(key, None)

    is_initialized = False
    
    
def kill_tunnel():
    global is_initialized
    tunnel.kill()
    is_initialized = False

if __name__ == "__main__":
    start_server()