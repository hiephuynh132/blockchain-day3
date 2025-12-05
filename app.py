from flask import Flask, render_template, jsonify, request
import hashlib
import random
import time
import threading

app = Flask(__name__)

# ======================= DATA STRUCTURES =======================

# PoW
class Block:
    def __init__(self, index, prev_hash, producer, difficulty, nonce, block_hash, elapsed, attempts):
        self.index = index
        self.prev_hash = prev_hash
        self.producer = producer
        self.difficulty = difficulty
        self.nonce = nonce
        self.hash = block_hash
        self.elapsed = elapsed
        self.attempts = attempts
        self.timestamp = time.strftime("%H:%M:%S")

class Miner:
    def __init__(self, name, hash_power):
        self.name = name
        self.hash_power = hash_power
        self.status = "Idle"
        self.attempts = 0

# PoS
class PosBlock:
    def __init__(self, index, prev_hash, producer, block_hash):
        self.index = index
        self.prev_hash = prev_hash
        self.producer = producer
        self.hash = block_hash
        self.timestamp = time.strftime("%H:%M:%S")

class Validator:
    def __init__(self, name, stake):
        self.name = name
        self.stake = stake
        self.selected = 0

# Fork
class ForkBlock:
    def __init__(self, block_id, parent_id):
        self.block_id = block_id
        self.parent_id = parent_id

# ======================= GLOBAL STATE - POW =======================

miners = [
    Miner("Alice", 1.0),
    Miner("Bob", 1.5),
    Miner("Carol", 0.7),
    Miner("Tom", 2.0),
    Miner("Harry", 1.3),
    Miner("Jessica", 0.5)
]

pow_blockchain = []
pow_difficulty = 4
target_time = 3.0
pow_prev_hash = "0" * 64
mining_flag = False
lock = threading.Lock()

# ======================= GLOBAL STATE - POS =======================

validators = [
    Validator("Val_A", 10),
    Validator("Val_B", 30),
    Validator("Val_C", 60),
]

pos_chain = []
pos_prev_hash = "0" * 64

# ======================= GLOBAL STATE - FORK =======================

fork_blocks = {}
fork_nodes = ["Node1", "Node2", "Node3", "Node4", "Node5"]
node_tip = {}
canonical_chain = []

# ======================= POW CORE =======================

def mine_worker(miner: Miner, event_stop, result_holder):
    global pow_difficulty, pow_prev_hash

    prefix = "0" * pow_difficulty
    nonce = 0
    start_time = time.time()

    miner.status = "Mining"
    miner.attempts = 0

    while not event_stop.is_set():
        miner.attempts += 1

        msg = f"{pow_prev_hash}|{nonce}|{miner.name}".encode()
        h = hashlib.sha256(msg).hexdigest()

        if h.startswith(prefix):
            elapsed = time.time() - start_time
            with lock:
                if not event_stop.is_set():
                    result_holder["winner"] = (miner.name, h, nonce, elapsed, miner.attempts)
                    event_stop.set()
                    return
        nonce += random.randint(1, 3)

    miner.status = "Stopped"

def adjust_difficulty(difficulty, block_time):
    if block_time < target_time * 0.5:
        return difficulty + 1, "Increase"
    elif block_time > target_time * 2:
        return max(1, difficulty - 1), "Decrease"
    return difficulty, "Stable"

def auto_mine():
    global mining_flag, pow_prev_hash, pow_difficulty

    while mining_flag:
        threads = []
        stop_event = threading.Event()
        result_holder = {}

        for m in miners:
            t = threading.Thread(target=mine_worker, args=(m, stop_event, result_holder))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if "winner" not in result_holder:
            continue

        miner_name, block_hash, nonce, elapsed, attempts = result_holder["winner"]

        with lock:
            height = len(pow_blockchain) + 1

            block = Block(
                index=height,
                prev_hash=pow_prev_hash,
                producer=miner_name,
                difficulty=pow_difficulty,
                nonce=nonce,
                block_hash=block_hash,
                elapsed=elapsed,
                attempts=attempts
            )

            pow_blockchain.append(block)
            pow_prev_hash = block_hash

            pow_difficulty, _ = adjust_difficulty(pow_difficulty, elapsed)

        time.sleep(1)

# ======================= POS CORE =======================

def select_validator():
    names = [v.name for v in validators]
    weights = [v.stake for v in validators]
    return random.choices(names, weights=weights, k=1)[0]

def create_pos_block(height):
    global pos_prev_hash

    chosen = select_validator()

    for v in validators:
        if v.name == chosen:
            v.selected += 1

    h = hashlib.sha256(f"{pos_prev_hash}|{chosen}|{height}".encode()).hexdigest()
    blk = PosBlock(height, pos_prev_hash, chosen, h)

    pos_chain.append(blk)
    pos_prev_hash = h

    return blk

# ======================= FORK CORE =======================

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

def simulate_fork():
    global fork_blocks, node_tip, canonical_chain

    fork_blocks = {}
    node_tip = {}
    canonical_chain = []

    fork_blocks["GEN"] = ForkBlock("GEN", None)

    fork_blocks["A1"] = ForkBlock("A1", "GEN")
    fork_blocks["B1"] = ForkBlock("B1", "GEN")

    for n in fork_nodes:
        latA = random.uniform(0, 1)
        latB = random.uniform(0, 1)

        if latA < latB:
            node_tip[n] = {
                "picked": "A1",
                "latA": latA,
                "latB": latB
            }
        else:
            node_tip[n] = {
                "picked": "B1",
                "latA": latA,
                "latB": latB
            }

    countA = sum(1 for n in fork_nodes if node_tip[n]["picked"] == "A1")
    countB = len(fork_nodes) - countA

    parent_for_C2 = random.choices(
        ["A1", "B1"], weights=[countA, countB], k=1
    )[0]

    fork_blocks["C2"] = ForkBlock("C2", parent_for_C2)

    tip_A = "C2" if parent_for_C2 == "A1" else "A1"
    tip_B = "C2" if parent_for_C2 == "B1" else "B1"

    lenA = compute_chain_length(fork_blocks, tip_A)
    lenB = compute_chain_length(fork_blocks, tip_B)

    if lenA > lenB:
        canonical_chain = get_chain_path(fork_blocks, tip_A)
    elif lenB > lenA:
        canonical_chain = get_chain_path(fork_blocks, tip_B)
    else:
        canonical_chain = get_chain_path(fork_blocks, random.choice([tip_A, tip_B]))

    return {
        "nodes": node_tip,
        "countA": countA,
        "countB": countB,
        "C2_parent": parent_for_C2,
        "chainA_tip": tip_A,
        "chainB_tip": tip_B,
        "lenA": lenA,
        "lenB": lenB,
        "canonical_chain": canonical_chain
    }

# ======================= ROUTES - MAIN =======================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pow")
def pow_page():
    return render_template("pow.html")

@app.route("/pos")
def pos_page():
    return render_template("pos.html")

@app.route("/fork")
def fork_page():
    return render_template("fork.html")

# ======================= ROUTES - POW =======================

@app.route("/pow/start")
def pow_start():
    global mining_flag
    if not mining_flag:
        mining_flag = True
        threading.Thread(target=auto_mine, daemon=True).start()
    return jsonify({"status": "started"})

@app.route("/pow/stop")
def pow_stop():
    global mining_flag
    mining_flag = False
    return jsonify({"status": "stopped"})

@app.route("/pow/status")
def pow_status():
    return jsonify({
        "miners": [
            {"name": m.name, "status": m.status, "attempts": m.attempts}
            for m in miners
        ],
        "blockchain": [
            {
                "height": b.index,
                "miner": b.producer,
                "difficulty": b.difficulty,
                "nonce": b.nonce,
                "attempts": b.attempts,
                "time": round(b.elapsed, 3),
                "hash": b.hash,
                "timestamp": b.timestamp
            } for b in pow_blockchain
        ],
        "difficulty": pow_difficulty
    })

@app.route("/pow/reset")
def pow_reset():
    global pow_blockchain, pow_difficulty, pow_prev_hash, mining_flag
    mining_flag = False
    pow_blockchain = []
    pow_difficulty = 4
    pow_prev_hash = "0" * 64
    for m in miners:
        m.status = "Idle"
        m.attempts = 0
    return jsonify({"status": "reset OK"})

# ======================= ROUTES - POS =======================

@app.route("/pos/step", methods=["POST"])
def pos_step():
    height = len(pos_chain) + 1
    blk = create_pos_block(height)

    return jsonify({
        "height": blk.index,
        "validator": blk.producer,
        "hash": blk.hash,
        "timestamp": blk.timestamp
    })

@app.route("/pos/status")
def pos_status():
    total = sum(v.selected for v in validators)

    return jsonify({
        "validators": [
            {
                "name": v.name,
                "stake": v.stake,
                "selected": v.selected,
                "percentage": round((v.selected / total) * 100, 2) if total > 0 else 0
            }
            for v in validators
        ],
        "blockchain": [
            {
                "height": b.index,
                "validator": b.producer,
                "hash": b.hash,
                "timestamp": b.timestamp
            }
            for b in pos_chain
        ]
    })

@app.route("/pos/auto", methods=["POST"])
def pos_auto_run():
    slots = int(request.json.get("slots", 10))

    for _ in range(slots):
        height = len(pos_chain) + 1
        create_pos_block(height)

    return jsonify({"status": "auto completed", "slots": slots})

@app.route("/pos/auto100", methods=["POST"])
def pos_auto_100():
    for _ in range(100):
        height = len(pos_chain) + 1
        create_pos_block(height)

    return jsonify({"status": "auto completed", "slots": 100})

@app.route("/pos/reset")
def pos_reset():
    global pos_chain, pos_prev_hash
    pos_chain = []
    pos_prev_hash = "0" * 64

    for v in validators:
        v.selected = 0

    return jsonify({"status": "reset OK"})

# ======================= ROUTES - FORK =======================

@app.route("/fork/simulate", methods=["POST"])
def fork_simulate():
    result = simulate_fork()
    return jsonify(result)

@app.route("/fork/reset")
def fork_reset():
    global fork_blocks, node_tip, canonical_chain
    fork_blocks = {}
    node_tip = {}
    canonical_chain = []
    return jsonify({"status": "reset OK"})

# ======================= RUN =======================

if __name__ == "__main__":
    app.run(port=8888, threaded=True)