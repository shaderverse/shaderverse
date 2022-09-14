import bpy
from shaderverse.nft import NFT
from typing import Generator

def get_nft() -> Generator:
    nft = NFT()
    yield nft