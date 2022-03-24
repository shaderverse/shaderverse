from typing import Optional
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
app = FastAPI()

def start():
    uvicorn.run(app)

@app.post("/items/")
def create_item(item: Item):
    return item
if __name__ == "__main__":
    uvicorn.run(app)