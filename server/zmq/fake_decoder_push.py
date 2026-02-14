import time
import random
import zmq

UPSTREAM_PUSH = "tcp://127.0.0.1:6000"  # must match ZMQ_PULL_PORT in zmq_pub_box.py env

def main():
    ctx = zmq.Context.instance()
    push = ctx.socket(zmq.PUSH)
    push.bind(UPSTREAM_PUSH)
    print(f"[FAKE DECODER PUSH] bound at {UPSTREAM_PUSH}")

    seq = 0
    while True:
        seq += 1
        msg_type = random.choice(["TELEM", "RF", "RAW"])
        if msg_type == "TELEM":
            payload = {
                "type": "TELEM",
                "seq": seq,
                "power": {"battery_voltage": round(random.uniform(7.0, 8.4), 2)},
                "orientation": {"roll_deg": round(random.uniform(-10, 10), 1)},
                "radio": {"rssi_dbm": random.randint(-120, -60)}
            }
        elif msg_type == "RF":
            payload = {"type": "RF", "seq": seq, "rssi": random.randint(-120, -60), "snr": round(random.uniform(-5, 15), 1)}
        else:
            payload = {"type": "RAW", "seq": seq, "bytes_hex": "deadbeef"}

        push.send_json(payload)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
