from pydantic import BaseModel, Json
from typing import Optional, List, Set

class Attribute(BaseModel):
    trait_type: str
    value: str

class Metadata(BaseModel):
    id: int = None
    filename: str = None
    attributes: List[Attribute] = None
    rendered_file_url: str = None

class RenderedResults(BaseModel):
    metadata: Metadata
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