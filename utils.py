import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.exceptions as crypto_exceptions

import hashlib
from pprint import pprint
import json
import random
from typing import Any

from models import Neighbor, AttachFailure, AttachSuccess

import requests

from pydantic import BaseModel
from fastapi import HTTPException


def verify(public_key: str, sign: str, data: BaseModel):
    pub_key = serial.load_pem_public_key(public_key.encode())
    if isinstance(pub_key, ec.EllipticCurvePublicKey):
        pass
        print("It' public key")
    signature = bytes.fromhex(sign)
    print(f"signature = {sign}")
    serial_contents = data.model_dump_json().encode()
    print(f"serial_contents = {serial_contents}")
    try:
        pub_key.verify(signature, serial_contents, ec.ECDSA(hashes.SHA256()))
    except crypto_exceptions.InvalidSignature as e:
        raise HTTPException(status_code=403, detail="Invalid Signature")

def sign(
    contents: dict[str,Any],
    private_key: ec.EllipticCurvePrivateKey,
    ):
    separators = (",", ":")
    print(contents)
    serialized_contents = json.dumps(
        contents, sort_keys=True, separators=separators
    ).encode()

    signed = private_key.sign(
        serialized_contents, ec.ECDSA(hashes.SHA256())
    ).hex()  # DER encoded
    print(f"serial_contents = {serialized_contents}")
    print(f"signature = {signed}")
    return signed

def create_attach_request(
    public_key: ec.EllipticCurvePublicKey,
    private_key: ec.EllipticCurvePrivateKey,
    my_url: str
):
    pem_pub_key = public_key.public_bytes(
        serial.Encoding.PEM, serial.PublicFormat.SubjectPublicKeyInfo
    )
    pem_pub_key_str = pem_pub_key.decode()
    my_address = hashlib.sha256(pem_pub_key).digest().hex()
    # client.post

    contents = {"public_key": pem_pub_key_str,
                "their_address": my_address,
                "their_url": my_url}
    signed = sign(contents,private_key)
    return {"contents": contents, "sign": signed}

CONNECT_LEAVES = 2

def handle_followup_attaches(
    n: list[Neighbor],
    pub_key: ec.EllipticCurvePublicKey,
    priv_key: ec.EllipticCurvePrivateKey,
    my_url: str
):
    pprint(n)
    match len(n):
        case 0:
            print("WARNING: No possible guard nodes in the network")
        case 1 | 2 :
            for i in n:
                handle_single_attach(pub_key, priv_key, i,my_url)
        case _:
            for i in random.choices(n,k=CONNECT_LEAVES):
                handle_single_attach(pub_key, priv_key, i,my_url)
                

def handle_single_attach(
    pub_key: ec.EllipticCurvePublicKey,
    priv_key: ec.EllipticCurvePrivateKey,
    i : Neighbor,
    my_url: str
    ):
    new_attach_request_body = create_attach_request(pub_key, priv_key,my_url)
    next_guard_node = i.http_address
    new_attach_request_response = requests.post(
                    url=f"{next_guard_node}attach/", json=new_attach_request_body
                )
    match new_attach_request_response.status_code:
        case 200:
            body: dict = new_attach_request_response.json()
            ats = AttachSuccess(**body)
            print(f"Successful connect {ats} to guard")
        case 429:
            body: dict = new_attach_request_response.json()
            atf = AttachFailure(**body)
            print(f"Failed to connect {atf} to guard")
        case _:
            print(f"Failed to connect at every step to guard")
            raise HTTPException(501, "Unimplemented handling of attach")
    
