from pydantic import BaseModel, validator 
import os
# from typing import Optional, List, Literal, Set

import logging
#class Attribute(BaseModel):
    # trait_type: str
    # value: str

class Attribute(BaseModel):
    trait_type: str
    value: str  

class GenRange(BaseModel):
    """ Generated range for renders"""
    start: int
    end: int


class Parameters2d(BaseModel):
    resolution_x: int = 720
    resolution_y: int = 720
    samples: int = 64
    quality: int = 90
    fps: int = 30

class BinaryLocations(BaseModel):
    windows: str = ""
    macosx64: str = ""
    macossilicon: str = ""
    linux: str = ""

class Binary(BaseModel):
    binary_name: str
    base_dir: str = os.path.join(os.path.expanduser("~"), ".shaderverse") 
    urls: BinaryLocations = None
    files: BinaryLocations = None