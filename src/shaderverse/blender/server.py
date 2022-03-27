import webbrowser
import bpy
from shaderverse.fastapi import controller
from shaderverse.blender.tunnel import Tunnel

tunnel: Tunnel

def init_fastapi():
    global tunnel
    print(bpy.app.version)
    controller.start(blender_binary_path=bpy.app.binary_path,blend_file=bpy.data.filepath )
    tunnel = Tunnel()
    preview_url = f"https://shaderverse.com/preview/{tunnel.subdomain}"
    bpy.context.scene.shaderverse.preview_url = preview_url
    try:
        webbrowser.open(preview_url)
    except:
        print(f"Unable to open {preview_url}")

def kill_fastapi():
    controller.proxy.process.kill()
    tunnel.kill()

if __name__ == "__main__":
    init_fastapi()