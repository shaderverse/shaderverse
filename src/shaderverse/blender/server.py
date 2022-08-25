import webbrowser
import bpy
from shaderverse.api.controller import Proxy
from shaderverse.blender.tunnel import Tunnel
import psutil

proxy: Proxy
tunnel: Tunnel
initialized = False


def start_server(live_preview: bool = False):
    global initialized, proxy, tunnel
    if not initialized:
        proxy = Proxy(blender_binary_path=bpy.app.binary_path, 
                        blend_file=bpy.data.filepath)
        if live_preview:
            tunnel = Tunnel()
            preview_url = f"https://shaderverse.com/preview/{tunnel.subdomain}"
            bpy.context.scene.shaderverse.preview_url = preview_url
            try:
                webbrowser.open(bpy.context.scene.shaderverse.preview_url)
            except:
                print(f"Unable to open preview url")
    initialized = True

def kill_process_recursively(process):
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def kill_fastapi():
    global initialized
    process = psutil.Process(proxy.process.pid)
    kill_process_recursively(process)

    # kill any instantiated blender sessions
    # for key in sessions:
    #     proccess_id = sessions[key].process.pid 
    #     blender_process = psutil.Process(proccess_id)
    #     kill_process_recursively(blender_process)
    #     sessions.pop(key, None)

    initialized = False
    
    
def kill_tunnel():
    global initialized
    tunnel.kill()
    initialized = False

if __name__ == "__main__":
    start_server()