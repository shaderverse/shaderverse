import os
import uvicorn
from fastapi import Depends, FastAPI
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
import bpy

app = FastAPI()

def get_bpy():
    import bpy
    yield bpy

# @app.on_event("startup")
# async def startup_event():
#     BLEND_FILE = "C:\\Users\\goldm\\Downloads\\chibies-mixamo-1.4.0.1.blend"
#     bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)


@app.post("/active")

def active():
    print("starting active")
    # bpy.ops.wm.window_new()
    # print(bpy.context.screen.areas.values())  
    # areas = bpy.data.window_managers[0].windows[0].screen.areas.values()

    # override = bpy.context.copy()
    # override["active_object"] = bpy.data.objects[0]
    # with bpy.context.temp_override(**override):
    #     print(bpy.context.active_object.name)

    bpy.context["active_object"] = bpy.data.objects[0]
    print(bpy.context.active_object.name)

    # print(bpy.context.screen)


    # print(bpy.context.window_manager.windows.values())
    return {"status": "completed"}


if __name__ == "__main__":

    uvicorn.run(app="bpy_context:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=8080)

