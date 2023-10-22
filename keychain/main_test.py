from main import generate_seed, generate_pair, Seed
import hashlib
import cryptography as crypto
import  cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec_crypto

def test_generate_seed():

    seed = Seed().load("test_0.txt")
    print(seed)

    keys = generate_pair(seed,b'0')
    pub_key  = keys[0]
    priv_key = keys[1]
    print(pub_key,priv_key)

