from pydantic import BaseModel, Json
from typing import Optional, List, Set

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class File(BaseModel):
    filename: str

class Trait(BaseModel):
    trait_type: str
    value: str

class Metadata(BaseModel):
    filename: str = None
    traits: List[Trait] = None




# class Request(BaseModel):
#     hooks: Optional[str]
#     method: Optional[str]
#     url: Optional[str]
#     headers: Optional[str]
#     files: Optional[str]
#     data: Optional[str]
#     json: Optional[Json]
#     params: Optional[str]
#     auth: Optional[str]
#     cookies: Optional[str]