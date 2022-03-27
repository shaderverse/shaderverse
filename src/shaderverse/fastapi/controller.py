from fastapi import FastAPI, Request
from pydantic import UUID4, Json
from shaderverse.fastapi.model import Metadata, Trait, GlbFile
import subprocess
import uuid
import requests
import json
import sys
import os
import uvicorn
import argparse
import shaderverse


SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
BLENDER_DATA_PATH = os.path.join(SCRIPT_PATH, "data", "blender_data.json")

def save_proxy_session(blender_data: dict):
    with open(BLENDER_DATA_PATH, 'w') as outfile:
        json.dump(blender_data, outfile)

def load_proxy_session()-> dict:
    with open(BLENDER_DATA_PATH) as json_file:
        return json.load(json_file)

# print(BPY_SCRIPT_PATH)
# SCRIPT_PATH = os.path.join(BPY_SCRIPT_PATH, "fastapi")
# os.chdir(SCRIPT_PATH)

# a global dictionary of sessions. for production, this should be replaced with a Redis instance or a similiar solution

sessions = {}
next_port = 8119
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
        self.script_path = os.path.join(SCRIPT_PATH, "controller.py")


        # try:
        #     python_command = [sys.executable, self.script_path]
        #     print(python_command)
        #     self.process = subprocess.Popen(python_command, shell=True)
        #     if self.process.returncode:
        #         raise Exception(f"process returned {self.process.returncode}")


        command = [self.blender_binary_path, "--factory-startup", "--background", "--addons", "shaderverse", "--python", self.script_path]
        self.process = subprocess.Popen(command, shell=True)

    

def set_filename(f):
    global filename
    filename = f


def create_new_session(session_id):
    return BlenderInstance(session_id)


def generate_free_port(id):
    global next_port
    assigned_port = next_port
    new_port = next_port + 1
    next_port = new_port
    return assigned_port


def generate_new_session_id():
    session_id = uuid.uuid4()
    return session_id


class BlenderInstance():
    def __init__(self, id):
        self.id = id
        # you don't need to generate this from ID or anything - just make sure the port is valid and unoccupied
        blender_data = load_proxy_session()
        self.blender_binary_path = blender_data["blender_binary_path"]
        self.blend_file = blender_data["blend_file"]
        self.port = str(generate_free_port(id))
        self.script_path = os.path.join(SCRIPT_PATH, "shaderverse_blender.py")
        # self.process = subprocess.Popen([PYTHON_BIN, self.script_path, '--port', self.port], shell=True)

        # stdout=subprocess.PIPE,
        # stderr=subprocess.STDOUT, 
        command = [self.blender_binary_path, self.blend_file, "--background", "--addons", "shaderverse", "--python", self.script_path, "--", "--port", self.port]
        self.process = subprocess.Popen(command, shell=True)

    def run(self, action):

        # I would recommend using aiohttp library to make this asynchronous
        response = requests.post(
            f'http://localhost:{self.port}/{action}')
        return response



def start(blender_binary_path: str, blend_file: str,):
    global proxy
    proxy = Proxy(blend_file=blend_file, blender_binary_path=blender_binary_path)
    blender_data = {"blend_file": blend_file, 
                   "blender_binary_path": blender_binary_path}
    save_proxy_session(blender_data=blender_data)


app = FastAPI()


# create new session - generate uniqe ID and spawn new ray_blender process
@app.post("/new_session")
async def start_session():
    session_id = generate_new_session_id()
    sessions[session_id] = create_new_session(session_id)
    return {
        "session_id": session_id  # we return the session ID to the client
    }


# client identifies itself with session ID, and specifies the action they want to preform. This will be useful for most of the actions,
@app.post("/perform_action/{action}/{session_id}")
async def perform_action(action: str, session_id: UUID4):
    # params: Json = await request.json() # request body may contain additional properties for the action, such as parametres for operators
    print(f"session_id: {session_id}")
    print(sessions[session_id])
    # params_dict = json.loads(params)
    # params_dict = {}
    # params_dict["filename"] = filename
    # params_json = json.dumps(params_dict)
    response = sessions[session_id].run(action)
    response_dict = response.json()

    match action:
        case "generate":
            result = Metadata(**response_dict)
        case "glb":
            result = GlbFile(**response_dict)
        case _:
            result = {
                "status": "action not found"  # we return the session ID to the client
            }
    return result

    # this should also be made async, see comment in the run method
    return 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')
    parser.add_argument('--port', 
                        help='the port', 
                        default=8118)

    args, unknown = parser.parse_known_args()

    uvicorn.run(app="controller:app", app_dir=SCRIPT_PATH, host="0.0.0.0", port=8118)
