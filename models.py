from pydantic import BaseModel


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

