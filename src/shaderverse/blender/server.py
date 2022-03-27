import webbrowser
import bpy
from shaderverse.fastapi.controller import Proxy
from shaderverse.blender.tunnel import Tunnel

proxy: Proxy
tunnel: Tunnel
initialized = False

def init_fastapi():
    global initialized, proxy, tunnel
    if not initialized:
        proxy = Proxy(blender_binary_path=bpy.app.binary_path, 
                        blend_file=bpy.data.filepath)
        tunnel = Tunnel()
        preview_url = f"https://shaderverse.com/preview/{tunnel.subdomain}"
        bpy.context.scene.shaderverse.preview_url = preview_url
        initialized = True
    try:
        webbrowser.open(bpy.context.scene.shaderverse.preview_url)
    except:
        print(f"Unable to open preview url")

def kill_fastapi():
    proxy.process.kill()
    tunnel.kill()

if __name__ == "__main__":
    init_fastapi()