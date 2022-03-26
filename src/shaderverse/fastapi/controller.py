from fastapi import FastAPI
import fastapi
from pydantic import UUID4, Json
import subprocess
import uuid
import requests
import json
import sys
import os
import uvicorn


SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
PYTHON_BIN = os.path.realpath(sys.executable)

# print(BPY_SCRIPT_PATH)
# SCRIPT_PATH = os.path.join(BPY_SCRIPT_PATH, "fastapi")
# os.chdir(SCRIPT_PATH)

# a global dictionary of sessions. for production, this should be replaced with a Redis instance or a similiar solution

sessions = {}
next_port = 8119
filename = "test.blend"


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
        self.port = str(generate_free_port(id))
        self.script_path = os.path.join(SCRIPT_PATH, "shaderverse_blender.py")
        self.process = subprocess.Popen([PYTHON_BIN, self.script_path, '--port', self.port], shell=True)

        # stdout=subprocess.PIPE,
        # stderr=subprocess.STDOUT, 

    def run(self, action, params):

        # I would recommend using aiohttp library to make this asynchronous
        response = requests.post(
            f'http://localhost:{self.port}/{action}', params)
        return response


class Proxy():
    def __init__(self):
        print("starting server")
        self.port = "8118"  # you don't need to generate this from ID or anything - just make sure the port is valid and unoccupied
        self.script_path = os.path.join(SCRIPT_PATH, "controller.py")
        # print(f"script path {self.script_path}")
        command = [PYTHON_BIN, self.script_path]
        print(command)
        self.process = subprocess.Popen(command, shell=True)


proxy = None


def start():
    global proxy
    proxy = Proxy()


app = FastAPI()


# create new session - generate uniqe ID and spawn new ray_blender process
@app.post("/new_session")
async def start_session():
    session_id = generate_new_session_id()
    sessions[session_id] = create_new_session(session_id)
    return {
        session_id: session_id  # we return the session ID to the client
    }


# client identifies itself with session ID, and specifies the action they want to preform. This will be useful for most of the actions,
@app.post("/perform_action/{action}/{session_id}")
async def perform_action(action: str, session_id: UUID4):
    # params: Json = await request.json() # request body may contain additional properties for the action, such as parametres for operators

    # params_dict = json.loads(params)
    params_dict = {}
    params_dict["filename"] = filename
    params_json = json.dumps(params_dict)

    # this should also be made async, see comment in the run method
    return sessions[session_id].run(action, params_json)


if __name__ == "__main__":
    uvicorn.run(app="controller:app", host="0.0.0.0", port=8118)
