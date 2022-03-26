

import argparse
import uvicorn
import os 
import sys
import json
import bpy
import shaderverse
from fastapi import FastAPI
from shaderverse.fastapi.model import File
from pydantic import Json

BPY_SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

app = FastAPI()
@app.post("/import_fbx")


async def import_fbx(file: File):
    # params: Json = await request.json() # request body may contain additional properties for the action, such as parametres for operators

    # params_dict = json.loads(params)
    filename = file.filename
    # Your code depended on bpy here ...
    # I'll leave it to you to figure out how to properly create the file and pass the file path in here....
    bpy.ops.import_scene.fbx("EXEC_DEFAULT", filepath=filename)
    return {"status": "ok"}


# @app.post("/read_homefile")
#     # ...

# @app.post("/create_cube")
#     # ...

# @app.post("/render")
#     # ...


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    # parser.add_argument('--app', 
    #                 help='the app')

    # parser.add_argument('--module', 
    #                     help='the module',
    #                     default="app")

    # parser.add_argument('--host', 
    #                     help='the ip addreess', 
    #                     default="0.0.0.0")

    parser.add_argument('--port', 
                        help='the port', 
                        default=8119)

    # parser.add_argument('--reload', 
    #                     help='whether we should reload',
    #                     action='store_false')

    # parser.add_argument('--debug', 
    #                     help='run in debug mode?',
    #                     action='store_false')

    # parser.add_argument('--workers', 
    #                     help='number of workers',
    #                     default=3)

    args = parser.parse_args()

    port = args.port

    uvicorn.run(app= "shaderverse_blender:app", host="0.0.0.0", port=args.port)