import mnemonic as mmn
import hashlib
import pprint as pprint
import cryptography.hazmat.primitives.asymmetric.ec as ec_crypto
import  cryptography.hazmat.primitives.serialization as serial
import cryptography.hazmat.primitives.asymmetric.ec as ec_crypto
import secrets as sec
from typing import Self, Tuple
import os


mnemo = mmn.Mnemonic("english")
# words = mnemo.generate(strength=256)
# seed = mnemo.to_seed(words, passphrase="")


## Have the keys be stored here or be discovered from SEEd
## other modules can only reference keys from here
# They can say please sign this using this private key
# Or you can 
# Please verify this

## what is my identity? Sha256 in hex of one of my public keys


# pprint.pprint(words)
class Seed(bytes):
    default_name = "seed_phrase.txt"
    def to_mnemonic(self) -> str:
        return mnemo.to_mnemonic(self)

    def save(self, name=None):
        text = self.to_mnemonic()
        if name is None:
            name = Seed.default_name
        with open(name, 'w') as f:
            f.write(text)

    @staticmethod
    def load(name=None) -> Self:
        if name is None:
            name = Seed.default_name
        with open(name, "r") as f:
            text = f.read()
        return bytes(mnemo.to_entropy(text))

    @staticmethod
    def from_file(name=None) -> Self:
        if name is None:
            name = Seed.default_name
        with open(name, "r") as f:
            text = f.read()
        return bytes(mnemo.to_entropy(text))


class Pair_id(bytes):
    pass


def generate_seed() -> Seed:
    rng = sec.token_bytes(32)
    return Seed(rng)


def generate_pair(
    master_seed: Seed, pair_id: Pair_id
) -> Tuple[ec_crypto.EllipticCurvePrivateKey, ec_crypto.EllipticCurvePublicKey]:
    new_seed = master_seed + pair_id
    hash = hashlib.sha256(new_seed).digest()
    i = int.from_bytes(hash)
    curve = ec_crypto.SECP256K1()
    priv_key = ec_crypto.derive_private_key(i, curve)
    pub_key = priv_key.public_key()
    
    return priv_key, pub_key
