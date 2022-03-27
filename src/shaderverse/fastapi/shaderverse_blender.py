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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

    parser.add_argument('--port', 
                        help='the port', 
                        default=8119)

    args, unknown = parser.parse_known_args()

    port = args.port

    uvicorn.run(app="shaderverse_blender:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=args.port)