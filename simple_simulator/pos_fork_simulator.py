# ============================================================
#  pos_fork_simulator.py – PoS Fork + Fork-Choice by Stake
# ============================================================

import random
from collections import defaultdict


class Validator:
    def __init__(self, name, stake):
        self.name = name
        self.stake = stake


class PosForkBlock:
    def __init__(self, block_id, parent_id):
        self.block_id = block_id
        self.parent_id = parent_id

    def __repr__(self):
        return f"{self.block_id}(parent={self.parent_id})"


def get_chain_path(blocks, tip_id):
    path = []
    cur = tip_id
    while cur is not None:
        path.append(cur)
        parent = blocks[cur].parent_id
        if parent is None:
            break
        cur = parent
    return list(reversed(path))


def pos_fork_sim():
    print("\n=======================================")
    print("   PoS FORK SIMULATOR – STAKE VOTING")
    print("=======================================")

    # -----------------------------
    # 1. Khởi tạo validators (khác stake)
    # -----------------------------
    validators = [
        Validator("Val_A", 10),
        Validator("Val_B", 20),
        Validator("Val_C", 40),
        Validator("Val_D", 15),
        Validator("Val_E", 15),
    ]

    total_stake = sum(v.stake for v in validators)
    print(f"\nTổng stake toàn mạng: {total_stake}")
    for v in validators:
        print(f"  - {v.name}: stake={v.stake}")

    # -----------------------------
    # 2. Genesis + fork A1, B1
    # -----------------------------
    blocks = {}
    blocks["GEN"] = PosForkBlock("GEN", None)
    blocks["A1"] = PosForkBlock("A1", "GEN")
    blocks["B1"] = PosForkBlock("B1", "GEN")

    print("\nTạo fork tại height 1: A1 và B1 cùng là con của GEN.")
    print("GEN → A1")
    print("GEN → B1")

    # -----------------------------
    # 3. Mỗi validator "nhìn" A1/B1 với latency khác nhau
    #    rồi quyết định vote cho nhánh nào
    # -----------------------------
    print("\n🌐 Mô phỏng độ trễ mạng và lựa chọn nhánh của validators:")

    validator_choice = {}
    stake_on_A = 0
    stake_on_B = 0

    for v in validators:
        latA = random.uniform(0, 1)
        latB = random.uniform(0, 1)

        # Validator vote cho block mà nó nhận nhanh hơn
        if latA < latB:
            choice = "A1"
            stake_on_A += v.stake
        else:
            choice = "B1"
            stake_on_B += v.stake

        validator_choice[v.name] = choice

        print(f"  {v.name}: latency(A1)={latA:.3f}, latency(B1)={latB:.3f} "
              f"→ vote cho nhánh {choice} (stake={v.stake})")

    # -----------------------------
    # 4. Tổng hợp stake ủng hộ từng nhánh
    # -----------------------------
    print("\n📊 Tổng hợp stake ủng hộ mỗi nhánh:")
    print(f"  - Stake theo nhánh A1: {stake_on_A}")
    print(f"  - Stake theo nhánh B1: {stake_on_B}")

    if stake_on_A > stake_on_B:
        canonical_tip = "A1"
        loser_tip = "B1"
    elif stake_on_B > stake_on_A:
        canonical_tip = "B1"
        loser_tip = "A1"
    else:
        # Nếu bằng nhau thì random pick (trong thực tế
        # giao thức PoS sẽ dùng thêm rule khác, ở đây đơn giản hoá)
        canonical_tip = random.choice(["A1", "B1"])
        loser_tip = "B1" if canonical_tip == "A1" else "A1"

    canonical_chain = get_chain_path(blocks, canonical_tip)

    print("\n✅ Kết quả fork-choice theo STAKE:")
    print(f"  → Chuỗi chính (canonical branch) là: {' → '.join(canonical_chain)}")
    print(f"  → Nhánh còn lại ({loser_tip}) trở thành fork phụ (không phải canonical).")

    # -----------------------------
    # 5. (Tuỳ chọn) Sinh thêm 1 block C2 dựa trên canonical branch
    #    C2 sẽ do validator được chọn theo stake tạo ra.
    # -----------------------------
    print("\n⛏️ Sinh thêm block C2 trên nhánh canonical bằng PoS:")

    # Chuẩn bị weighted random theo stake
    names = [v.name for v in validators]
    stakes = [v.stake for v in validators]

    chosen_validator = random.choices(names, weights=stakes, k=1)[0]
    blocks["C2"] = PosForkBlock("C2", canonical_tip)
    final_chain = get_chain_path(blocks, "C2")

    print(f"  - Validator được chọn: {chosen_validator}")
    print(f"  - C2 nối vào {canonical_tip}")
    print("\n⛓️ Chuỗi chính sau khi thêm C2:")
    print(f"  {' → '.join(final_chain)}")

    return blocks, canonical_chain, final_chain


if __name__ == "__main__":
    pos_fork_sim()
