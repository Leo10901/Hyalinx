import hashlib
import time
import json
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import TimeInForce, OrderSide
from dotenv import load_dotenv
load_dotenv()  # reads the .env file

trading_client = TradingClient(
    api_key=os.getenv("ALPACA_API_KEY"),
    secret_key=os.getenv("ALPACA_SECRET_KEY"),
    paper=True
)


#creating block class
class Block: 
#creating a constructor for block class 
    def __init__(self, data, prev_hash):
        self.data = data
        self.timestamp = time.time()
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()
#Method that calculates hash using SHA-256
    def calc_hash(self):
        sha = hashlib.sha256()
        sha.update(self.data.encode('utf-8'))
        return sha.hexdigest()
#Creating the Blockchain class
class Blockchain: 
#Create Constructor for Blockchain class
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    #Create a method that creates the first block in the blockchain known as Genesis block 
    def create_genesis_block(self):
        return Block("Genesis Block", "0")


    #Create a method that creates a new block and adds it to the block chain (aka the list)
    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(data, prev_block.hash)
        self.chain.append(new_block)



def save_blockchain(blockchain, filename="blockchain.json"):
    chain_data = []
    for block in blockchain.chain: 
        chain_data.append({
        "data": block.data, 
        "prev_hash": block.prev_hash,
        "timestamp": block.timestamp, 
        "hash": block.hash
        })
    with open(filename, "w") as f:
        json.dump(chain_data, f, indent=4)
    print(f"Blockchain saved to {filename}")

def load_blockchain(filename="blockchain.json"):
    if not os.path.exists(filename):
        return Blockchain()
    with open(filename, "r") as f:
        chain_data = json.load(f)
    blockchain = Blockchain()
    blockchain.chain = []
    for block_data in chain_data:
        block = Block(block_data["data"], block_data["prev_hash"])
        block.timestamp = block_data["timestamp"]
        block.hash = block_data["hash"]
        blockchain.chain.append(block)
    return blockchain

def order_to_block_data(order, notional):
    return json.dumps({
        "order_id": str(order.id),
        "symbol": "WEAT",
        "side": order.side.value.upper(),
        "notional": str(notional),
        "status": order.status.value, 
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")

    })




notional = float(input("Enter the notional amount ($USD)"))

side = input("Enter your side:").strip().upper()
if side == "BUY":
    side=OrderSide.BUY
elif side == "SELL":
    side=OrderSide.SELL
else:
    raise ValueError(f"Unsupported side: {side}")


blockchain = load_blockchain()

market_order = trading_client.submit_order(
    MarketOrderRequest(
        symbol = "WEAT", 
        notional= notional,
        side=side,
        time_in_force=TimeInForce.DAY  # expires end of day if not filled
    )
)
blockchain.add_block(order_to_block_data(market_order, notional))
save_blockchain(blockchain)


print(f"Order ID: {market_order.id}")
print(f"Status: {market_order.status}")

print('Blockchain:')


for i, block in enumerate(blockchain.chain):
    print(f"\n--- Block {i+1} ---")
    print(f"  Data:      {block.data}")
    print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))}")
    print(f"  Prev Hash: {block.prev_hash[:20]}...")
    print(f"  Hash:      {block.hash[:20]}...")