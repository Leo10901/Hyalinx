# Hyalinx
A Python blockchain that records stock market orders as 
cryptographically linked blocks using SHA-256 hashing.

Each trade executed through Alpaca's paper trading API is 
stored as a block containing the order details, timestamp, 
and a SHA-256 hash of the previous block. This creates a 
tamper-evident chain where altering any record breaks every 
subsequent hash.
