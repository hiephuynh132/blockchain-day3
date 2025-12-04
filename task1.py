import hashlib
import random
import time
import threading
import queue

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# ==============================
# PoW PARAMETERS
# ==============================
INITIAL_DIFFICULTY = 4
TARGET_BLOCK_TIME = 3.0
STOP_MINING = False


# ==============================
# MINER THREAD
# ==============================
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
            data = f"{self.block_data}{nonce}".encode()
            block_hash = hashlib.sha256(data).hexdigest()

            # Giả lập hash-rate (miner nhanh hơn sẽ vòng lặp ít delay hơn)
            for _ in range(int(self.hash_rate * 3000)):
                pass

            if block_hash.startswith(prefix):
                STOP_MINING = True
                self.winner = (nonce, block_hash, attempts, self.name)
                break


# ==============================
# DIFFICULTY ADJUSTMENT
# ==============================
def adjust_difficulty(difficulty, block_time):
    if block_time < TARGET_BLOCK_TIME:
        difficulty += 1
    elif block_time > TARGET_BLOCK_TIME * 2:
        difficulty = max(1, difficulty - 1)
    return difficulty


# ==============================
# POW SIMULATOR (producer)
#   -> gửi dữ liệu block qua queue
# ==============================
def pow_simulator_live(data_queue, num_blocks=15):
    global STOP_MINING

    miners_cfg = [
        ("Alice",   1.0),
        ("Bob",     1.7),
        ("Charlie", 0.8),
    ]

    difficulty = INITIAL_DIFFICULTY
    previous_hash = "0" * 64

    for height in range(1, num_blocks + 1):
        STOP_MINING = False
        block_data = f"height={height}|prev={previous_hash}"

        miners = [
            MinerThread(name, rate, block_data, difficulty)
            for name, rate in miners_cfg
        ]

        start = time.time()
        for m in miners:
            m.start()

        winner_thread = None
        while True:
            for m in miners:
                if m.winner is not None:
                    winner_thread = m
                    break
            if winner_thread:
                break
            time.sleep(0.001)

        block_time = time.time() - start
        nonce, block_hash, attempts, miner_name = winner_thread.winner

        previous_hash = block_hash
        new_difficulty = adjust_difficulty(difficulty, block_time)

        # Gửi thông tin block sang animation
        data_queue.put({
            "height": height,
            "miner": miner_name,
            "difficulty": difficulty,
            "block_time": block_time,
        })

        difficulty = new_difficulty

    data_queue.put("END")


# ==============================
# 3D BLOCK UTIL
# ==============================
def make_block_vertices(x, y, z, dx=0.8, dy=0.4, dz=0.8):
    """
    Tạo list các mặt của khối hộp (block) tại vị trí (x, y, z)
    """
    x0, x1 = x - dx / 2, x + dx / 2
    y0, y1 = y, y + dy
    z0, z1 = z - dz / 2, z + dz / 2

    verts = [
        # bottom
        [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        # top
        [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        # sides
        [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
        [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)],
        [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)],
    ]
    return verts


# ==============================
# RUN 3D ANIMATION
# ==============================
def run_3d_animation():
    data_queue = queue.Queue()

    # Thread PoW producer
    pow_thread = threading.Thread(
        target=pow_simulator_live,
        args=(data_queue,)
    )
    pow_thread.start()

    # Lưu block đang rơi
    # mỗi phần tử: {"height": h, "y": y_current, "color": c}
    falling_blocks = []
    ground_y = 0.0
    start_y = 4.0
    fall_speed = 0.05

    miner_colors = {
        "Alice": "tab:blue",
        "Bob": "tab:orange",
        "Charlie": "tab:green",
    }

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim(0, 16)   # x: block index
    ax.set_ylim(0, 5)    # y: height
    ax.set_zlim(-2, 2)   # z: just small depth
    ax.set_xlabel("Block Height")
    ax.set_ylabel("Animation Height")
    ax.set_zlabel("Depth")

    plt.title("3D Blockchain Animation – Blocks Falling into Chain")

    def update(frame):
        # 1) Nhận block mới từ queue (nếu có)
        while not data_queue.empty():
            msg = data_queue.get()
            if msg == "END":
                # Khi kết thúc → không thêm block mới nữa
                continue
            h = msg["height"]
            miner = msg["miner"]
            color = miner_colors.get(miner, "gray")

            falling_blocks.append({
                "height": h,
                "y": start_y,
                "color": color,
            })

        # 2) Cập nhật vị trí y (rơi xuống)
        for blk in falling_blocks:
            if blk["y"] > ground_y:
                blk["y"] -= fall_speed
                if blk["y"] < ground_y:
                    blk["y"] = ground_y

        # 3) Vẽ lại toàn bộ
        ax.cla()
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 5)
        ax.set_zlim(-2, 2)
        ax.set_xlabel("Block Height")
        ax.set_ylabel("Animation Height")
        ax.set_zlabel("Depth")
        ax.set_title("3D Blockchain Animation – Blocks Falling into Chain")

        # Vẽ từng block
        for blk in falling_blocks:
            x_pos = blk["height"]
            y_pos = blk["y"]
            verts = make_block_vertices(x_pos, y_pos, 0.0)
            poly = Poly3DCollection(verts, alpha=0.9)
            poly.set_facecolor(blk["color"])
            ax.add_collection3d(poly)

        # vẽ “ground chain” cho đẹp
        ax.plot3D(
            [0, 16],
            [ground_y, ground_y],
            [0, 0],
            color="black",
            linewidth=1,
        )

        return []

    ani = FuncAnimation(fig, update, interval=50)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_3d_animation()
