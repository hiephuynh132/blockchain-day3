# ============================================================
#  pow_simulator.py – Proof of Work Simulation
# ============================================================

import hashlib
import random
import time


class Block:
    def __init__(self, index, prev_hash, producer, difficulty, nonce, block_hash):
        self.index = index
        self.prev_hash = prev_hash
        self.producer = producer
        self.difficulty = difficulty
        self.nonce = nonce
        self.hash = block_hash
        self.timestamp = time.time()

    def __repr__(self):
        return f"Block(height={self.index}, miner={self.producer}, hash={self.hash[:10]}...)"


class Miner:
    def __init__(self, name, hash_power=1.0):
        self.name = name
        self.hash_power = hash_power


def mine_block_pow(miners, prev_hash, difficulty, target_block_time=3.0):
    prefix = "0" * difficulty
    nonce = 0
    attempts = 0

    names = [m.name for m in miners]
    weights = [m.hash_power for m in miners]

    start_time = time.time()

    while True:
        attempts += 1
        miner_name = random.choices(names, weights=weights, k=1)[0]

        msg = f"{prev_hash}|{nonce}|{miner_name}".encode()
        h = hashlib.sha256(msg).hexdigest()

        if h.startswith(prefix):
            elapsed = time.time() - start_time
            block = Block(
                index=None,
                prev_hash=prev_hash,
                producer=miner_name,
                difficulty=difficulty,
                nonce=nonce,
                block_hash=h
            )
            return block, elapsed, attempts

        nonce += 1


def adjust_difficulty(difficulty, block_time, target_block_time=3.0):
    if block_time < target_block_time * 0.5:
        difficulty += 1
        print(f"   ➤ Increase difficulty → {difficulty}")
    elif block_time > target_block_time * 2:
        difficulty = max(1, difficulty - 1)
        print(f"   ➤ Decrease difficulty → {difficulty}")
    else:
        print(f"   ➤ Difficulty stable ({difficulty})")
    return difficulty


def pow_simulator(num_blocks=5):
    print("\n===============================")
    print("   PROOF OF WORK SIMULATOR")
    print("===============================")

    miners = [
        Miner("Alice", 1.0),
        Miner("Bob", 1.5),
        Miner("Carol", 0.7),
    ]

    difficulty = 4
    target_block_time = 3.0
    blockchain = []

    prev_hash = "0" * 64

    for height in range(1, num_blocks + 1):
        print(f"\n⛏️  Mining Block #{height} (difficulty={difficulty})")

        block, elapsed, attempts = mine_block_pow(
            miners, prev_hash, difficulty, target_block_time
        )
        block.index = height
        blockchain.append(block)

        print(f"   🏆 Winner Miner: {block.producer}")
        print(f"   ⏱️ Time: {elapsed:.3f}s")
        print(f"   🧮 Attempts: {attempts}")
        print(f"   🔒 Hash: {block.hash[:32]}...")

        prev_hash = block.hash
        difficulty = adjust_difficulty(difficulty, elapsed, target_block_time)

    print("\n⛓️ Final PoW Blockchain:")
    for b in blockchain:
        print("  ", b)

    return blockchain


if __name__ == "__main__":
    pow_simulator(5)
