from fastapi import FastAPI
from fastapi.testclient import TestClient
import hashlib
import cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec
import cryptography.hazmat.primitives.hashes as hashes
from app import app
import base64
import json
import pprint

import cryptography as crypto

from keychain.main import Seed, generate_pair, Pair_id

client = TestClient(app)


def test_main():
    # get public key
    seed = Seed.from_file("seed_phrase.txt")
    pair_id = Pair_id(b"0")
    keys = generate_pair(seed, pair_id)
    print(keys)
    priv_key = keys[0]
    pub_key = keys[1]
    pem_pub_key = pub_key.public_bytes(
        serial.Encoding.PEM, serial.PublicFormat.SubjectPublicKeyInfo
    )
    pem_pub_key_str = pem_pub_key.decode()
    my_address = hashlib.sha256(pem_pub_key).digest().hex()
    print(pem_pub_key)
    print(my_address)
    # client.post
    
    contents = {"public_key": pem_pub_key_str, "their_address": my_address}
    separators=(',', ':')
    serialised_contents = json.dumps(contents,sort_keys=True,separators=separators).encode()

    print("Sign")
    sign = priv_key.sign(serialised_contents,ec.ECDSA(hashes.SHA256())).hex() # DER encoded
    print(f"serial_content = {serialised_contents}")
    j = {"contents": contents, "sign": sign}
    pprint.pprint(j)
    response = client.post("/attach/", json=j)
    assert response.status_code == 200
