from hashlib import sha256
from datetime import datetime

class Block:
    def __init__(self, index, hash, previous_hash, timestamp, data):
        self.index = index
        self.hash = hash
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data

class BlockChain:
    def __init__(self):
        self.fixed_date = datetime(2023, 1, 1, 12, 30, 45) # Used for creating a genesis block 
        self.genesis_hash = "2eb9e0d013ad3ce15c93a8435b729b6dcd193dec985880f9c080ab4bac7bbdc6"
        self.chain = [Block(0,self.genesis_hash,None,self.fixed_date,None)]

    def add_block(self, block):
        self.chain.append(block)

    def get_latest_block(self):
        return self.chain[-1]
     

    def calculate_hash_from_values(self,index, previous_hash, timestamp, data):
        data_str = f"{index}{previous_hash}{timestamp}{data}"
        hashed_data = sha256(data_str.encode()).hexdigest()
        return hashed_data

    def calculate_hash_for_block(self,block):
        data_str=f"{block.index}{block.previous_hash}{block.timestamp}{block.data}"
        hashed_data = sha256(data_str.encode()).hexdigest()
        return hashed_data

    def generate_next_block(self,block_data):
        previous_block = self.get_latest_block()
        next_index = previous_block.index + 1
        next_timestamp = datetime.now()
        next_hash = self.calculate_hash_from_values(next_index, previous_block.hash, next_timestamp, block_data)
        new_block = Block(next_index, next_hash, previous_block.hash, next_timestamp, block_data)
        return new_block
    
    def is_valid_new_block(self,new_block, previous_block):
        if previous_block.index + 1 != new_block.index:
            print('Invalid index')
            return False
        elif previous_block.hash != new_block.previous_hash:
            print('Invalid previous hash')
            return False
        elif self.calculate_hash_for_block(new_block) != new_block.hash:
            print('Invalid hash:', self.calculate_hash_for_block(new_block), new_block.hash)
            return False
        return True
    
    def is_valid_chain(self,blockchain_to_validate):
        
        #Verify if genesis valid
        if blockchain_to_validate.chain[0].index != 0:
            return False
        elif blockchain_to_validate.chain[0].hash != self.genesis_hash:
            return False
        
        #Verify the rest of blocks
        for i in range(1, len(blockchain_to_validate.chain)):
            if not self.is_valid_new_block(blockchain_to_validate.chain[i], blockchain_to_validate.chain[i - 1]):
                return False
        
        #If all the verifications passed return true
        return True
    
    def find_longer_chain(self,chain_to_check )-> None:
        if self.is_valid_chain(chain_to_check) and len(self.chain)<len(chain_to_check):
            self.chain = chain_to_check
    

#TESTY
if __name__ == "__main__":
    B1 = BlockChain()
    new_block = B1.generate_next_block("")
    B1.add_block(new_block)
    print(B1.is_valid_new_block(B1.chain[1],B1.chain[0]))


    B2 = BlockChain()
    new_block = B2.generate_next_block("FASAFAS")
    B2.add_block(new_block)
    print(B2.is_valid_chain(B1))
        
