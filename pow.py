import hashlib
import random
import time
import threading

INITIAL_DIFFICULTY = 4
TARGET_BLOCK_TIME = 3.0
STOP_MINING = False


class MinerThread(threading.Thread):
    def __init__(self, name, hash_rate, block_data, difficulty):
        super().__init__()
        self.name = name
        self.hash_rate = hash_rate
        self.block_data = block_data
        self.difficulty = difficulty
        self.winner = None

    def run(self):
        global STOP_MINING
        prefix = "0" * self.difficulty
        attempts = 0

        while not STOP_MINING:
            attempts += 1
            nonce = random.randint(0, 10**18)

            h = hashlib.sha256(f"{self.block_data}{nonce}".encode()).hexdigest()

            # hash-rate simulation
            for _ in range(int(self.hash_rate * 2000)):
                pass

            if h.startswith(prefix):
                STOP_MINING = True
                self.winner = (nonce, h, attempts, self.name)
                break


def adjust_difficulty(diff, block_time):
    if block_time < TARGET_BLOCK_TIME:
        return diff + 1
    if block_time > TARGET_BLOCK_TIME * 2:
        return max(1, diff - 1)
    return diff


def pow_simulator_live(data_queue, num_blocks=20):
    global STOP_MINING

    miners_cfg = [
        ("Alice", 1.0),
        ("Bob", 1.7),
        ("Charlie", 0.8)
    ]

    difficulty = INITIAL_DIFFICULTY
    prev_hash = "0" * 64

    for height in range(1, num_blocks + 1):
        STOP_MINING = False
        block_data = f"height={height}|prev={prev_hash}"

        miners = [
            MinerThread(name, rate, block_data, difficulty)
            for name, rate in miners_cfg
        ]

        start_time = time.time()

        for m in miners:
            m.start()

        winner = None
        while True:
            for m in miners:
                if m.winner is not None:
                    winner = m
                    break
            if winner:
                break
            time.sleep(0.001)

        block_time = time.time() - start_time
        nonce, block_hash, attempts, miner_name = winner.winner

        data_queue.put({
            "height": height,
            "miner": miner_name,
            "difficulty": difficulty,
            "blockTime": round(block_time, 3)
        })

        prev_hash = block_hash
        difficulty = adjust_difficulty(difficulty, block_time)

    data_queue.put("END")
