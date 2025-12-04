# ============================================================
#  fork_resolution.py – Fork + Longest Chain Rule
# ============================================================

import random


class ForkBlock:
    def __init__(self, block_id, parent_id):
        self.block_id = block_id
        self.parent_id = parent_id


def compute_chain_length(blocks, tip):
    length = 0
    cur = tip
    while cur is not None:
        length += 1
        parent = blocks[cur].parent_id
        if parent is None:
            break
        cur = parent
    return length


def get_chain_path(blocks, tip):
    path = []
    cur = tip
    while cur is not None:
        path.append(cur)
        parent = blocks[cur].parent_id
        if parent is None:
            break
        cur = parent
    return list(reversed(path))


def fork_resolution_sim():
    print("\n===============================")
    print("     FORK RESOLUTION SIM")
    print("===============================")

    blocks = {}
    blocks["GEN"] = ForkBlock("GEN", None)

    # Two blocks A1, B1 created at same height
    blocks["A1"] = ForkBlock("A1", "GEN")
    blocks["B1"] = ForkBlock("B1", "GEN")

    nodes = ["Node1", "Node2", "Node3", "Node4", "Node5"]
    node_tip = {}

    print("\n🌐 Simulating network latency:")
    for n in nodes:
        latA = random.uniform(0, 1)
        latB = random.uniform(0, 1)

        if latA < latB:
            node_tip[n] = "A1"
        else:
            node_tip[n] = "B1"

        print(f"  {n}: latency(A1)={latA:.3f}, latency(B1)={latB:.3f} → picks {node_tip[n]}")

    countA = sum(1 for n in nodes if node_tip[n] == "A1")
    countB = len(nodes) - countA

    print("\n📊 Fork State:")
    print(f"  - A1 supporters: {countA}")
    print(f"  - B1 supporters: {countB}")

    # New block C2 mined, attaches probabilistically
    parent_for_C2 = random.choices(
        ["A1", "B1"], weights=[countA, countB], k=1
    )[0]

    blocks["C2"] = ForkBlock("C2", parent_for_C2)

    print(f"\n⛏️ Block C2 appended to {parent_for_C2}")

    tip_A = "C2" if parent_for_C2 == "A1" else "A1"
    tip_B = "C2" if parent_for_C2 == "B1" else "B1"

    lenA = compute_chain_length(blocks, tip_A)
    lenB = compute_chain_length(blocks, tip_B)

    print("\n📏 Chain Length:")
    print(f"  - Chain A tip={tip_A}, length={lenA}")
    print(f"  - Chain B tip={tip_B}, length={lenB}")

    if lenA > lenB:
        canonical = get_chain_path(blocks, tip_A)
    elif lenB > lenA:
        canonical = get_chain_path(blocks, tip_B)
    else:
        canonical = get_chain_path(blocks, random.choice([tip_A, tip_B]))

    print("\n✅ Canonical Chain (Longest Chain Rule):")
    print("  ", " → ".join(canonical))

    return blocks, canonical


if __name__ == "__main__":
    fork_resolution_sim()
