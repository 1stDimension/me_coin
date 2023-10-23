from fastapi import FastAPI
from fastapi.testclient import TestClient
from app import app

from keychain.main import Seed, generate_pair, Pair_id

client = TestClient(app)

def test_main():
    # get public key
    seed = Seed.from_file("seed_phrase.txt")
    pair_id = Pair_id(b'0')
    keys = generate_pair(seed,pair_id)
    print(keys)
    client.post
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
