from typing import Union

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

import ipaddress
import json

import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.exceptions as crypto_exceptions


class Neighbor(BaseModel):
    ip: str
    pub_key: str
    address: str


app = FastAPI()
app.neighbors: dict[str, Neighbor] = {}


class InnerItem(BaseModel):
    public_key: str  # PEM
    their_address: bytes  # hex of PEM


class Item(BaseModel):
    contents: InnerItem
    sign: str


@app.get("/")
def read_root(request: Request):
    client = request.client.host
    return {"Hello": "World"}


@app.get("/neighbors")
def read_neighbor() -> dict[str, Neighbor]:
    return app.neighbors


@app.post("/keep-alive")
def keep_alive():
    return {"H": "2O"}


@app.post("/attach")
def attach_neighbour(item: Item, request: Request):
    # Get their identity
    # Verify it's them
    # Settl
    print("ITEM")
    contents = item.contents
    pub_key = serial.load_pem_public_key(item.contents.public_key)
    signature = item.sign
    serial_contents = item.contents.model_dump_json().encode()
    try:
        pub_key.verify(signature, serial_contents, ec.ECDSA(hashes.SHA256()))
    except crypto_exceptions.InvalidSignature as e:
        raise HTTPException(status_code=403,detail="Invalid Signature")
    client = request.client.host
    neighbor = Neighbor(client, contents.public_key, contents.their_address)
    # app.neighbor
    print(client)
    print(item)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
