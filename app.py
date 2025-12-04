from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import queue
from pow import pow_simulator_live

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Queue để nhận dữ liệu từ thread mining
data_queue = queue.Queue()

@app.route("/")
def index():
    return render_template("index.html")


def background_listener():
    """Lấy dữ liệu mining từ queue và emit sang frontend"""
    while True:
        msg = data_queue.get()
        if msg == "END":
            socketio.emit("end", {"msg": "Mining finished"})
            break

        socketio.emit("new_block", msg)


def start_pow():
    pow_simulator_live(data_queue, num_blocks=30)


if __name__ == "__main__":
    # Thread nghe queue → đẩy ra socket
    t1 = threading.Thread(target=background_listener, daemon=True)
    t1.start()

    # Thread mining
    t2 = threading.Thread(target=start_pow, daemon=True)
    t2.start()

    socketio.run(app, host="0.0.0.0", port=5000)
