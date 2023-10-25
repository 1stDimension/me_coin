from pydantic import BaseModel,AnyUrl, HttpUrl
from dataclasses import dataclass


class Neighbor(BaseModel):
    tcp_address: str
    pub_key: str
    address: str
    expiration: int

class InnerItem(BaseModel):
    public_key: str  # PEM
    their_address: bytes  # hex of PEM
    their_url: HttpUrl


class Item(BaseModel):
    contents: InnerItem
    sign: str

class Join(BaseModel):
    guard_node: HttpUrl

@dataclass
class AttachSuccess():
    expire: int
    neighbors: list[Neighbor]

@dataclass
class AttachFailure():
    neighbors: list[Neighbor]