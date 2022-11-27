from typing import Dict, List
from urllib import response
from fastapi import FastAPI, Request
from pydantic import UUID4, BaseModel, Json
from shaderverse.model import Metadata, Attributes, RenderedResults
import subprocess
import uuid
import requests
import json
import sys
import os
import uvicorn
import argparse
import shaderverse
from shaderverse.api.model import BlenderData, Session, SessionData, Action
import bpy

SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
BLENDER_DATA_PATH = os.path.join(SCRIPT_PATH, "data", "blender_data.json")


def save_proxy_session(blender_data: BlenderData):
    with open(BLENDER_DATA_PATH, 'w') as outfile:
        json.dump(blender_data.dict(), outfile)

def load_proxy_session()-> BlenderData:
    with open(BLENDER_DATA_PATH) as json_file:
        json_results = json.load(json_file)
        blender_data: BlenderData = BlenderData(**json_results)
        return blender_data

# print(BPY_SCRIPT_PATH)
# SCRIPT_PATH = os.path.join(BPY_SCRIPT_PATH, "fastapi")
# os.chdir(SCRIPT_PATH)

# a global dictionary of sessions. for production, this should be replaced with a Redis instance or a similiar solution


proxy = None


class Proxy():
    def __init__(self, blender_binary_path: str, blend_file: str, )-> None:
        """ 
        Initializes the server 
        """
        print("starting server")
        self.blender_binary_path = blender_binary_path
        self.blend_file = blend_file
        self.port = "8118"  # you don't need to generate this from ID or anything - just make sure the port is valid and unoccupied
        self.script_path = os.path.join(SCRIPT_PATH, "blender_service.py")
        blender_data: BlenderData = BlenderData(blend_file=self.blend_file, blender_binary_path = self.blender_binary_path, next_port = int(self.port)+1)
        save_proxy_session(blender_data=blender_data)

        # try:
        #     python_command = [sys.executable, self.script_path]
        #     print(python_command)
        #     self.process = subprocess.Popen(python_command, shell=True)
        #     if self.process.returncode:
        #         raise Exception(f"process returned {self.process.returncode}")


        command = [self.blender_binary_path, self.blend_file, "--factory-startup", "--background", "--addons", "shaderverse", "--python", self.script_path]
        self.process = subprocess.Popen(command, shell=True)

    

def set_filename(f):
    global filename
    filename = f


def create_new_session(session_id):
    return BlenderInstance(session_id)


def generate_new_session_id():
    session_id = uuid.uuid4()
    return session_id


class BlenderInstance():
    def __init__(self, id):
        self.id = id
        # you don't need to generate this from ID or anything - just make sure the port is valid and unoccupied
        blender_data = load_proxy_session()
        self.blender_binary_path = blender_data.blender_binary_path
        self.blend_file = blender_data.blend_file
        self.port = str(blender_data.next_port)
        blender_data.next_port += 1
        
        self.script_path = os.path.join(SCRIPT_PATH, "shaderverse_blender.py")
        # self.process = subprocess.Popen([PYTHON_BIN, self.script_path, '--port', self.port], shell=True)

        # stdout=subprocess.PIPE,
        # stderr=subprocess.STDOUT, 
        command = [self.blender_binary_path, self.blend_file, "--background", "--addons", "shaderverse", "--log-level", "0", "--python", self.script_path, "--", "--port", self.port]
        self.process = subprocess.Popen(command, shell=True)
        save_proxy_session(blender_data=blender_data)

    def run(self, action, params: List[Metadata] | None):

        # I would recommend using aiohttp library to make this asynchronous
        response = requests.post(
            f'http://localhost:{self.port}/{action}', params=params)
        return response

sessions: Dict[UUID4, BlenderInstance] = {}

def start(blender_binary_path: str, blend_file: str,):
    global proxy
    proxy = Proxy(blend_file=blend_file, blender_binary_path=blender_binary_path)
    
    


app = FastAPI()


# create new session - generate uniqe ID and spawn new ray_blender process
@app.post("/new_session", response_model=Session)
async def start_session():
    global sessions
    session_id = generate_new_session_id()
    blender_session: BlenderInstance = create_new_session(session_id)
    port = blender_session.port
    blend_file = blender_session.blend_file

    sessions[session_id]= blender_session

    session: Session = Session(id=session_id, port=int(port), blend_file=blend_file)

    return session

@app.post("/active")
def active():
    return {"object": bpy.context.active_object.name}


# @app.get("/")
# async def list_sessions():
#     global sessions
#     session_ids = []
#     for session in sessions:
#         session_ids.append(session["session_id"])
#     return {
#         "sessions": session_ids
#     }


# client identifies itself with session ID, and specifies the action they want to preform. This will be useful for most of the actions,
# @app.post("/perform_action/{action}/{session_id}")
# async def perform_action(action: str, session_id: UUID4):
#     global sessions
#     # params: Json = await request.json() # request body may contain additional properties for the action, such as parametres for operators
#     print(f"session_id: {session_id}")
#     print(sessions[session_id])
#     # params_dict = json.loads(params)
#     # params_dict = {}
#     # params_dict["filename"] = filename
#     # params_json = json.dumps(params_dict)
#     response = sessions[session_id].run(action)
#     response_dict = response.json()

#     match action:
#         case "generate":
#             result = Metadata(**response_dict)
#         case "glb":
#             result = GlbFile(**response_dict)
#         case "session":
#             result = SessionData(**response_dict)
#         case _:
#             result = {
#                 "status": "action not found"  # we return the session ID to the client
#             }
#     return result

#     # this should also be made async, see comment in the run method
#     return 


async def perform_action(action: Action, session_id: UUID4, params: List[Metadata] | None):
    response = sessions[session_id].run("render_glb")
    response_dict = response.json()
    return response_dict


@app.post("/render_glb/{session_id}")
async def render_glb(session_id: UUID4, batch: List[Metadata]):
    action = Action.render_glb
    response_dict = perform_action(action=action, session_id=session_id, params= batch)
    result = RenderedResults(**response_dict)
    return result
    
  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')
    parser.add_argument('--port', 
                        help='the port', 
                        default=8118)

    args, unknown = parser.parse_known_args()

    uvicorn.run(app="controller:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=8118)
