import requests
import json
import hashlib
import time
import psutil

POOL_URL = "stratum+tcp://pool.supportxmr.com:3333"
WALLET_ADDRESS = "46GaeZ4L2pzLntXCLmq34o7Yh7BVp2AQ76Q27X4VbYyeFtqvA2w7HYM69yi4CPbNWsM2iET9VsTCMBnkLKtxcYi4TekTE56"

def get_best_difficulty():
    cpu_freq = psutil.cpu_freq().max
    cpu_cores = psutil.cpu_count(logical=True)
    if cpu_freq >= 3000 and cpu_cores >= 8:
        return 100000
    elif cpu_freq >= 2000 and cpu_cores >= 4:
        return 50000
    else:
        return 10000

DIFFICULTY = get_best_difficulty()

def get_work():
    response = requests.get(f"{POOL_URL}/getwork")
    return response.json()

def mine():
    while True:
        work = get_work()
        nonce = 0
        while True:
            data = f"{work['data']}{nonce}".encode()
            hash_result = hashlib.sha256(data).hexdigest()
            if hash_result.startswith("0" * (DIFFICULTY // 10000)):
                print(f"Valid hash found: {hash_result}")
                requests.post(f"{POOL_URL}/submitwork", json={"nonce": nonce, "hash": hash_result})
                break
            nonce += 1
        time.sleep(1)

if __name__ == "__main__":
    print(f"Mining with difficulty: {DIFFICULTY}")
    mine()