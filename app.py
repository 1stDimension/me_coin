from typing import Union

from pprint import pprint

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi import BackgroundTasks, Depends, FastAPI
from contextlib import asynccontextmanager

import requests
import uvicorn

import schedule
import copy

import random
import os

import ipaddress
import json
import datetime
import time

from utils import *
from keychain.main import Seed, Pair_id, generate_pair
from models import *

import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.exceptions as crypto_exceptions

NEIGHBOR_LIMIT = 5
SEED_FILE = os.environ.get("ME_COIN_SEED_FILE","seed_phrase.txt")
SEED = Seed.from_file(SEED_FILE)
KEY_ID= bytes(os.environ.get("ME_COIN_KEY_ID","0"),encoding="utf-8")
pair_id = Pair_id(KEY_ID)
keys = generate_pair(SEED, pair_id)
PRIVATE_KEY = keys[0]
PUBLIC_KEY = keys[1]

PORT = int(os.environ.get("ME_COIN_PORT",8000))
HOST = ipaddress.ip_address(os.environ.get("ME_COIN_HOST","127.0.0.1"))
PROTOCOL =os.environ.get("ME_COIN_PROTOCOL","http")

import multiprocessing

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print ("Before yield") 
    yield
    print ("After yield") 

app = FastAPI(lifespan=lifespan)
app.neighbors: dict[str, Neighbor] = {}

FLAG = True

@app.get("/")
def read_root(request: Request):
    client = request.client.host
    return {"Hello": "World"}


def start_mining(msg:str):
    print(f"Notification {msg}")
    
    c = 1
    while FLAG:
        print(f"I'm mining {c}")
        c += 1
        time.sleep(1)
        
def miner_process():
    pass
        

@app.get("/mine")
async def do_mining(q : BackgroundTasks):
    q.add_task(start_mining, do_mining.__name__)
    return {"I do mine"}

@app.get("/my_info")
def read_root():
    public_key = PUBLIC_KEY
    pem_pub_key = public_key.public_bytes(
        serial.Encoding.PEM, serial.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return {"my_url": get_my_url(),"public_key": pem_pub_key}

@app.get("/neighbors")
def read_neighbor() -> dict[str, Neighbor]:
    return app.neighbors


@app.post("/keep-alive")
def keep_alive():
    # Special request
    # if correct
    return {"H": "2O"}


class NeighborLimitReached(Exception):
    def __init__(self, neighbors: list[Neighbor], details: dict[str,Any]):
        self.neighbors = neighbors
        self.details = details


@app.exception_handler(NeighborLimitReached)
async def unicorn_exception_handler(request: Request, exc: NeighborLimitReached):
    return JSONResponse(
        status_code=429,
        content={
            "neighbors": exc.neighbors,
            "details": exc.details
        }
    )

def get_my_url():
    return f"{PROTOCOL}://{HOST}:{PORT}/"

@app.post("/attach")
def attach_neighbor(item: Item, request: Request, bg: BackgroundTasks) -> AttachSuccess:
    pub_key = PUBLIC_KEY
    priv_key = PRIVATE_KEY
    print("Attach started")
    # Get their identity
    # Verify it's them
    # Add them to neighbors if I can
    # otherwise send 429 and neighbors
    contents = item.contents
    verify(item.contents.public_key, item.sign, item.contents)
    my_info = create_attach_request(pub_key, priv_key,get_my_url())
    
    neighbors: dict[str, Neighbor] = app.neighbors
    if len(neighbors) >= NEIGHBOR_LIMIT:
        raise NeighborLimitReached(neighbors=app.neighbors,details=my_info)
    else:
        client = str(contents.their_url)
        # Add challenge
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
            raise HTTPException(409, f"IP address of {client} has a node registered")
        old_neighbors = copy.deepcopy(neighbors)
        neighbors[client] = neighbor

        return AttachSuccess(expire, list(old_neighbors.values()),details=my_info)


@app.post("/join")
def join_network(join: Join):
    pub_key = PUBLIC_KEY
    priv_key = PRIVATE_KEY
    guard_node = join.guard_node
    neighbors: dict[str, Neighbor] = app.neighbors

    my_url = get_my_url()
    
    attach_request_body = create_attach_request(pub_key, priv_key,my_url)
    attach_request_response = requests.post(
        url=f"{guard_node}attach/", json=attach_request_body
    )
    print(f"Request to attach send to {attach_request_response.url}")

    match attach_request_response.status_code:
        case 200:
            body: dict = attach_request_response.json()
            print("BEFORE ats")
            pprint(body)
            ats = AttachSuccess(**body)
            pprint(ats)
            try:
                verify(ats.details.contents.public_key,ats.details.sign,ats.details.contents)
            except HTTPException as e:
                raise HTTPException(502, "PANIC: SOME SHENANIGANS GOING ON AS RESPONS IS INVALID")
            neighbor = Neighbor(
                tcp_address=guard_node,
                pub_key=ats.details.contents.public_key,
                address=ats.details.contents.their_address,
                expiration=ats.expire,
            )
            print(f"Adding {neighbor}")
            if guard_node in neighbors:
                raise HTTPException(502,"Response from existing node")
            else:
                neighbors[guard_node] = neighbor
            pprint("ATS")
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
        case 409:
            b = attach_request_response.json()
            print("I tried to occupy the spot")
            pprint(b)
            raise HTTPException(409,"spot occupied")


    return {"result": "success", "guard_node": guard_node}

if __name__ == "__main__":
    uvicorn.run(app, host=str(HOST), port=PORT)  