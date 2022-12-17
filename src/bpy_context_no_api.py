import os
import uvicorn
from fastapi import Depends, FastAPI
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
# from shaderverse.api.blender_wrapper import Blender
import bpy



app = FastAPI()


# @app.on_event("startup")
# async def startup_event():
#     BLEND_FILE = "C:\\Users\\goldm\\Downloads\\chibies-mixamo-1.4.0.1.blend"
#     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)


# @app.on_event("startup")
# async def startup_event():

#     print(dir(bpy.context))

@app.post("/active")
async def active():
    print("starting active")

    print(dir(bpy.context))
    # bpy.ops.wm.window_new()
    # print(bpy.context.screen.areas.values())  
    # areas = bpy.data.window_managers[0].windows[0].screen.areas.values()

    # override = bpy.context.copy()
    # override["active_object"] = bpy.data.objects[0]
    # with bpy.context.temp_override(**override):
    #     print(bpy.context.active_object.name)
    print(bpy.context.active_object)


    # print(bpy.context.screen)


    # print(bpy.context.window_manager.windows.values())
    return {"status": "completed"}


if __name__ == "__main__":

    uvicorn.run(app="bpy_context_no_api:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=8080)
    

