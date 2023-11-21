from pydantic import BaseModel,AnyUrl, HttpUrl
from dataclasses import dataclass


class Neighbor(BaseModel):
    tcp_address: HttpUrl
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
    details: Item

    def __post_init__(self):
        self.details = Item(**self.details)
        self.neighbors = list(map(
            lambda x: Neighbor(**x),
            self.neighbors
        ))

@dataclass
class AttachFailure():
    neighbors: list[Neighbor]
    details: Item

    def __post_init__(self):
        self.details = Item(**self.details)
