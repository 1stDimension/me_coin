from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import ipaddress
import json

import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes

app = FastAPI()
app.neighbours = {}

class InnerItem(BaseModel):
    public_key: str # PEM
    their_address: bytes # hex of PEM

class Item(BaseModel):
    contents: InnerItem
    sign: str

@app.get("/")
def read_root():
    return {"Hello": "World"}



@app.post("/keep-alive")
def keep_alive():
    return {"H":"2O"}

@app.post("/attach")
def attach_neighbour(item: Item):
    # Get their identity
    # Verify it's them
    # Settl
    print("ITEM")
    # pub_key =  serial.load_pem_public_key(item.contents.public_key)
    # signature = item.sign
    # serial_contents = item.contents.model_dump_json().encode()
    # pub_key.verify(serial_contents)
     
    print(item)
    return {"Hello": "World"}




@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
