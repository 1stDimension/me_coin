from pydantic import BaseModel,AnyUrl, HttpUrl
from dataclasses import dataclass


class Neighbor(BaseModel):
    ip: str
    pub_key: str
    address: str
    expiration: int

class InnerItem(BaseModel):
    public_key: str  # PEM
    their_address: bytes  # hex of PEM


class Item(BaseModel):
    contents: InnerItem
    sign: str

class Join(BaseModel):
    guard_node: HttpUrl

@dataclass
class AttachSuccess():
    expire: int
    neighbors: list[Neighbor]