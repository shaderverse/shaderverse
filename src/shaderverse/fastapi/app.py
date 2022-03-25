from multiprocessing import Process
import sys

ORIG_SYS_PATH = list(sys.path) # Make a new instance of sys.path


import bpy # Here, the sys.path is severely messed with, screws up the import 
           # in the new process that is created in multiprocessing.Pool()

BPY_SYS_PATH = list(sys.path) # Make instance of `bpy`'s modified sys.path

from typing import Optional
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


@app.post("/items/")
def create_item(item: Item):
    return item

@app.get("/")
async def root():
    items = bpy.data.objects.items()
    return {"message": "Hello World",
            "items": items}

def run_server():
    uvicorn.run(app, host ="127.0.0.1", port=8118, log_level = "info")

class Server():
    """ multiprocess fastAPI server """

    def __init__(self):
        self.process = Process(target=run_server, args=(), daemon=True)
    
    def start(self):
        """ start the fastAPI server """
        print("starting fastAPI server")
        self.process.start() 
        
    
    def kill(self):
        """ kill the fastAPI server """
        print("killing fastAPI server")
        self.process.kill() 

server = None

def run():
    " create the fastapi server "
    sys.path = ORIG_SYS_PATH
    global server
    server = Server()
    server.start()

if __name__ == "__main__":
    run()
