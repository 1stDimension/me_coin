from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import ipaddress

app = FastAPI()
app.neighbours = {}

class InnerItem(BaseModel):
    public_key: bytes
    their_address: bytes

class Item(BaseModel):
    contents: InnerItem
    sign: bytes

@app.get("/")
def read_root():
    return {"Hello": "World"}



@app.post("/keep-alive")
def keep_alive():
    return {"H":"2O"}

@app.post("/attach")
def attach_neighbour():
    # Get their identity
    # Verify it's them
    # Settl
    return {"Hello": "World"}




@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
