# ============================================================
#  pos_simulator.py – Proof of Stake Simulation
# ============================================================

import hashlib
import random
from collections import defaultdict
import time


class Block:
    def __init__(self, index, prev_hash, producer, block_hash):
        self.index = index
        self.prev_hash = prev_hash
        self.producer = producer
        self.hash = block_hash
        self.timestamp = time.time()

    def __repr__(self):
        return f"Block(height={self.index}, validator={self.producer}, hash={self.hash[:10]}...)"


class Validator:
    def __init__(self, name, stake):
        self.name = name
        self.stake = stake


def pos_simulator(num_slots=20):
    print("\n===============================")
    print("    PROOF OF STAKE SIMULATOR")
    print("===============================")

    validators = [
        Validator("Val_A", 10),
        Validator("Val_B", 30),
        Validator("Val_C", 60),
    ]

    names = [v.name for v in validators]
    weights = [v.stake for v in validators]

    selection_count = defaultdict(int)
    chain = []

    prev_hash = "0" * 64

    for height in range(1, num_slots + 1):
        chosen = random.choices(names, weights=weights, k=1)[0]
        selection_count[chosen] += 1

        h = hashlib.sha256(f"{prev_hash}|{chosen}|{height}".encode()).hexdigest()
        blk = Block(height, prev_hash, chosen, h)
        chain.append(blk)

        prev_hash = h

    print("\n📊 Validator Selection Statistics:")
    total = sum(selection_count.values())
    for v in validators:
        count = selection_count[v.name]
        pct = (count / total) * 100 if total > 0 else 0
        print(f"  - {v.name}: stake={v.stake}, selected={count} times ({pct:.1f}%)")

    print("\n⛓️ PoS Chain:")
    for b in chain:
        print("  ", b)

    return chain, validators, selection_count


if __name__ == "__main__":
    pos_simulator(30)
