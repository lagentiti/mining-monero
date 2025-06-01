import socket
import json
import hashlib
import time
import psutil

POOL_URL = "pool.supportxmr.com"
PORT = 3333
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

def connect_to_pool():
    try:
        print("[INFO] Connexion au pool...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((POOL_URL, PORT))
        print("[SUCCESS] Connexion réussie!")
        return s
    except Exception as e:
        print(f"[ERROR] Échec de connexion au pool: {e}")
        return None

def send_login_request(sock):
    login_data = {
        "method": "login",
        "params": {
            "login": WALLET_ADDRESS
        },
        "id": 1
    }
    try:
        print("[INFO] Envoi de la demande de connexion au pool...")
        sock.sendall(json.dumps(login_data).encode() + b"\n")
        response = sock.recv(4096).decode()
        print("[SUCCESS] Connexion réussie, réponse reçue!")
        return json.loads(response)
    except Exception as e:
        print(f"[ERROR] Échec de connexion au pool: {e}")
        return None

def mine(sock):
    while True:
        print("[INFO] Tentative d'obtention d'une tâche de minage...")
        response = send_login_request(sock)
        if response is None or "result" not in response or "job" not in response["result"]:
            print("[ERROR] Aucune tâche reçue. Tentative de reconnexion...")
            sock.close()
            time.sleep(5)
            sock = connect_to_pool()
            continue

        job = response["result"]["job"]
        print(f"[INFO] Tâche reçue! Job ID: {job['job_id']}")

        nonce = 0
        while True:
            data = f"{job['blob']}{nonce}".encode()
            hash_result = hashlib.sha256(data).hexdigest()

            if hash_result.startswith("0" * (DIFFICULTY // 10000)):
                print(f"[SUCCESS] Hash valide trouvé! {hash_result}")
                submit_data = {
                    "method": "submit",
                    "params": {
                        "id": response["result"]["id"],
                        "job_id": job["job_id"],
                        "nonce": nonce,
                        "result": hash_result
                    }
                }
                print("[INFO] Envoi du résultat au pool...")
                sock.sendall(json.dumps(submit_data).encode() + b"\n")
                break
            
            if nonce % 1000 == 0:
                print(f"[INFO] Nonce en cours: {nonce}, pas de hash valide trouvé.")

            nonce += 1
        time.sleep(1)

if __name__ == "__main__":
    print(f"[INFO] Minage avec difficulté: {DIFFICULTY}")
    sock = connect_to_pool()
    if sock:
        mine(sock)
