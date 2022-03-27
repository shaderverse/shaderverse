import argparse
import uvicorn
import os 
import json
import bpy
from fastapi import FastAPI
from shaderverse.fastapi.model import Metadata, Trait
from typing import List

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))

app = FastAPI()

@app.post("/generate", response_model=Metadata)
async def generate():
    run_generate_operator = bpy.ops.shaderverse.generate()

    generated_metadata: List[Trait] = json.loads(bpy.context.scene.shaderverse.generated_metadata)

    metadata = Metadata(
        filename=bpy.data.filepath,traits=generated_metadata)

    print(metadata)
    return metadata


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

    args, unknown = parser.parse_known_args()

    port = args.port

    # uvicorn.run(app="shaderverse_blender:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=args.port)

    uvicorn.run(app="shaderverse_blender:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=args.port)