# sub_debug.py
import json
import zmq
from zmq_endpoints import ZmqEndpoints

def main():
    endpoints = ZmqEndpoints.from_env()
    ctx = zmq.Context.instance()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.RCVHWM, 1000)

    # Subscribe to everything for debugging
    sub.setsockopt(zmq.SUBSCRIBE, b"")
    ep = None
    for c in endpoints.pub_connect_candidates():
        try:
            sub.connect(c)
            ep = c
            break
        except Exception:
            pass
    if not ep:
        raise RuntimeError("could not connect to any PUB endpoint candidates")

    print(f"[SUB DEBUG] connected to {ep}")

    while True:
        topic_b, msg_b = sub.recv_multipart()
        topic = topic_b.decode()
        env = json.loads(msg_b.decode())
        print(topic, env.get("kind"), env.get("seq"))

if __name__ == "__main__":
    main()
