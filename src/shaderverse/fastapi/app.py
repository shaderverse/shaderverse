# from multiprocessing import Process, current_process
import sys
from . import controller
import json
from pydantic import UUID4, Json
from fastapi import FastAPI
import uvicorn

ORIG_SYS_PATH = list(sys.path) # Make a new instance of sys.path

from shaderverse import BPY_SYS_PATH

bpy_data = None


app = FastAPI()



# create new session - generate uniqe ID and spawn new ray_blender process 
@app.post("/new_session")
async def start_session():
    session_id = controller.generate_new_session_id()
    controller.sessions[session_id] = controller.create_new_session(session_id)
    return {
        session_id: session_id # we return the session ID to the client
    }


# client identifies itself with session ID, and specifies the action they want to preform. This will be useful for most of the actions, 
@app.post("/perform_action/{action}/{session_id}")
async def perform_action(action: str, session_id: UUID4):
    # params: Json = await request.json() # request body may contain additional properties for the action, such as parametres for operators

    # params_dict = json.loads(params)
    params_dict = {}
    params_dict["filename"] = controller.filename
    params_json = json.dumps(params_dict)

    return controller.sessions[session_id].run(action, params_json) #this should also be made async, see comment in the run method


# if __name__ == "__main__":
#     uvicorn.run(app= "app:app", host="0.0.0.0", port=8118, reload=F, debug=args.debug, workers=args.workers)




# if current_process().name == 'MainProcess':
#     sys.path = BPY_SYS_PATH
#     import bpy # Here, the sys.path is severely messed with, screws up the import 
#             # in the new process that is created in multiprocessing.Pool()
#     bpy_data = bpy.data


# from typing import Optional
# import uvicorn
# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()
# class Item(BaseModel):
#     name: str
#     description: Optional[str] = None
#     price: float


# @app.post("/items/")
# def create_item(item: Item):
#     return item

# @app.get("/")
# async def root():
#     sys.path = BPY_SYS_PATH
#     import bpy
    
#     # items = bpy.data.objects.items()
#     # return {"message": "Hello World",
#     #         "items": items}
#     return {"message": "Hello World"}

# def run_server():
#     uvicorn.run(app, host ="127.0.0.1", port=8118, log_level = "info")

# class Server():
#     """ multiprocess fastAPI server """

#     def __init__(self):
#         self.process = Process(target=run_server, args=(), daemon=True)
    
#     def start(self):
#         """ start the fastAPI server """
#         print("starting fastAPI server")
#         self.process.start() 
#         self.process.join()
         
#     def kill(self):
#         """ kill the fastAPI server """
#         print("killing fastAPI server")
#         self.process.kill() 

# server = None

# def run():
#     " create the fastapi server "
#     sys.path = ORIG_SYS_PATH
#     global server
#     server = Server()
#     server.start()

# if __name__ == "__main__":
#     run()
