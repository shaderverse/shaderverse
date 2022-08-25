from pydantic import BaseModel, Json
from typing import Optional, List, Set

class Trait(BaseModel):
    trait_type: str
    value: str

class Metadata(BaseModel):
    filename: str = None
    traits: List[Trait] = None

class GlbFile(BaseModel):
    buffer: bytes = None



class GenRange(BaseModel):
    """ Generated range for renders"""
    start: int
    end: int


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