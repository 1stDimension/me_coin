from typing import Union

from pprint import pprint

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import requests
import uvicorn

import random
import os

import ipaddress
import json
import datetime

from utils import *
from keychain.main import Seed, Pair_id, generate_pair
from models import *

import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.exceptions as crypto_exceptions

NEIGHBOR_LIMIT = 5
SEED_FILE = "seed_phrase.txt"
SEED = Seed.from_file(SEED_FILE)
pair_id = Pair_id(b"0")
keys = generate_pair(SEED, pair_id)
PRIVATE_KEY = keys[0]
PUBLIC_KEY = keys[1]

PORT = int(os.environ.get("ME_COIN_PORT",8000))
HOST = ipaddress.ip_address(os.environ.get("ME_COIN_HOST","127.0.0.1"))
PROTOCOL =os.environ.get("ME_COIN_PROTOCOL","http")


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
    # Special request
    # if correct
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
def attach_neighbor(item: Item, request: Request) -> AttachSuccess:
    print("Attach started")
    # Get their identity
    # Verify it's them
    # Add them to neighbors if I can
    # otherwise send 429 and neighbors
    contents = item.contents
    verify(item.contents.public_key, item.sign, item.contents)
    neighbors: dict[str, Neighbor] = app.neighbors
    if len(neighbors) >= NEIGHBOR_LIMIT:
        raise NeighborLimitReached(neighbor=app.neighbors)
    else:
        client = request.client.host
        ct = datetime.datetime.now()
        ts = int(ct.timestamp() * 1000.0)
        expire = ts + 20 * 1000
        neighbor = Neighbor(
            tcp_address=contents.their_url,
            pub_key=contents.public_key,
            address=contents.their_address,
            expiration=expire,
        )

        pprint(neighbor)
        pprint(neighbors)

        print(f"ts = {ts}")
        # print(neighbor)
        # print(item)
        if client in neighbors:
            raise HTTPException(403, f"IP address of {client} has a node registered")
        neighbors[client] = neighbor

        return AttachSuccess(expire, list(neighbors.values()))


@app.post("/join")
def join_network(join: Join):
    pub_key = PUBLIC_KEY
    priv_key = PRIVATE_KEY
    guard_node = join.guard_node

    my_url = f"{PROTOCOL}://{HOST}:{PORT}/"

    attach_request_body = create_attach_request(pub_key, priv_key,my_url)
    attach_request_response = requests.post(
        url=f"{guard_node}attach/", json=attach_request_body
    )
    print(f"Request to attach send to {attach_request_response.url}")

    match attach_request_response.status_code:
        case 200:
            body: dict = attach_request_response.json()
            ats = AttachSuccess(**body)
            pprint(ats)
            print(f"Successful connect {ats} -> find 2 more guard nodes guard")
            handle_followup_attaches(ats.neighbors,pub_key,priv_key, my_url)
                
        case 429:
            body: dict = attach_request_response.json()
            atf = AttachFailure(**body)
            print("Too much neighbors connected -> falling back to reported neighbors")
            handle_followup_attaches(atf.neighbors,pub_key,priv_key, my_url)
        case 403:
            msg = "PANIC I SEND INVALID MESSAGE"
            b = attach_request_response.json()
            print(msg)
            pprint(b)
            raise HTTPException(502,msg)


    return {"result": "success", "guard_node": guard_node}

if __name__ == "__main__":
    uvicorn.run(app, host=str(HOST), port=PORT)  