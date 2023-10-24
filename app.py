from typing import Union

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import ipaddress
import json
import datetime

from models import Neighbor, Item, InnerItem

import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.exceptions as crypto_exceptions

NEIGHBOR_LIMIT = 5

app = FastAPI()
app.neighbors: dict[str, Neighbor] = {}

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

class NeighborLimitReached(Exception):
    def __init__(self, neighbor: list[Neighbor]):
        self.neighbor = neighbor

@app.exception_handler(NeighborLimitReached)
async def unicorn_exception_handler(request: Request, exc: NeighborLimitReached):
    return JSONResponse(
        status_code=429,
        content=exc.neighbor,
    )


@app.post("/attach")
def attach_neighbour(item: Item, request: Request):
    # Get their identity
    # Verify it's them
    # Add them to neighbors if I can
    # otherwise send 429 and neighbors
    contents = item.contents
    pub_key = serial.load_pem_public_key(item.contents.public_key.encode())
    if isinstance(pub_key,ec.EllipticCurvePublicKey):
        pass
        # print("It' public key")
    signature = bytes.fromhex(item.sign)
    # print(f"signature = {signature}")
    serial_contents = item.contents.model_dump_json().encode()
    # print(f"serial_contents = {serial_contents}")
    try:
        pub_key.verify(signature, serial_contents, ec.ECDSA(hashes.SHA256()))
    except crypto_exceptions.InvalidSignature as e:
        raise HTTPException(status_code=403,detail="Invalid Signature")
    client = request.client.host
    neighbor = Neighbor(ip=client, pub_key=contents.public_key, address=contents.their_address)
    ct = datetime.datetime.now()
    ts = int(ct.timestamp() * 1000.0)
    next_check = ts + 20 * 1000
    print(f"ts = {ts}")
    # print(neighbor)
    # print(item)
    # app.neighbors: 

    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
