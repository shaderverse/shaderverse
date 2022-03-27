import bpy
from shaderverse.fastapi import controller
from shaderverse.blender.tunnel import Tunnel

tunnel: Tunnel

def init_fastapi():
    print(bpy.app.version)
    controller.start(blender_binary_path=bpy.app.binary_path,blend_file=bpy.data.filepath )
    tunnel = Tunnel()
    preview_url = f"https://shaderverse.com/preview/{tunnel.subdomain}"
    # TODO write preview url to scene
    # TODO open preview url

def kill_fastapi():
    controller.proxy.process.kill()
    tunnel.kill()

if __name__ == "__main__":
    init_fastapi()