# zmq_pub_box.py
from __future__ import annotations
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import zmq

from zmq_endpoints import ZmqEndpoints

TOPIC_TELEM = b"telem.decoded"
TOPIC_RF    = b"rf.metrics"
TOPIC_RAW   = b"raw.frame"
TOPIC_HB    = b"event.heartbeat"
TOPIC_STAT  = b"event.status"

def utc_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def make_envelope(kind: str, payload: Dict[str, Any], *, seq: Optional[int] = None, quality: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "v": 1,
        "id": str(uuid.uuid4()),
        "ts_ms": utc_ms(),
        "source": "gnuradio-decoder",
        "seq": seq,
        "kind": kind,
        "payload": payload,
        "quality": quality or {},
    }

def route_topic(payload: Dict[str, Any]) -> Tuple[bytes, str]:
    """
    Decide which topic to publish based on message content.
    Assumes upstream gives a dict with either:
      - payload["type"] in {"TELEM","RF","RAW"} or similar
      - OR payload already resembles telemetry and has keys power/orientation/radio
    """
    t = (payload.get("type") or payload.get("kind") or "").upper()

    if "power" in payload or "orientation" in payload or "radio" in payload:
        return TOPIC_TELEM, "telem.decoded"

    if t in ("TELEM", "TELEMETRY", "DECODED_TELEM"):
        return TOPIC_TELEM, "telem.decoded"

    if t in ("RF", "LINK", "RF_METRICS"):
        return TOPIC_RF, "rf.metrics"

    return TOPIC_RAW, "raw.frame"

def bind_first(sock: zmq.Socket, candidates: list[str], label: str) -> str:
    last_err = None
    for ep in candidates:
        try:
            sock.bind(ep)
            print(f"[{label}] bound -> {ep}")
            return ep
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed to bind {label} on any candidate endpoints: {candidates}") from last_err

def connect_first(sock: zmq.Socket, candidates: list[str], label: str) -> str:
    last_err = None
    for ep in candidates:
        try:
            sock.connect(ep)
            print(f"[{label}] connected -> {ep}")
            return ep
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed to connect {label} to any candidate endpoints: {candidates}") from last_err

def main():
    # Uncertainty knobs
    upstream_mode = os.getenv("UPSTREAM_MODE", "auto").strip().lower()
    # If upstream is SUB, you can optionally subscribe to specific prefixes
    upstream_sub_prefix = os.getenv("UPSTREAM_SUB_PREFIX", "").encode()  # empty = all topics

    endpoints = ZmqEndpoints.from_env()
    ctx = zmq.Context.instance()

    # ---- Downstream PUB (your box output) ----
    pub = ctx.socket(zmq.PUB)
    pub.setsockopt(zmq.SNDHWM, int(os.getenv("ZMQ_SNDHWM", "1000")))
    pub.setsockopt(zmq.LINGER, 0)
    pub_ep = bind_first(pub, endpoints.pub_bind_candidates(), "PUB")

    # ---- Upstream ingest (from GNU Radio decoder) ----
    # We support either PULL or SUB ingest; auto tries PULL first.
    pull = None
    sub = None

    if upstream_mode in ("pull", "auto"):
        pull = ctx.socket(zmq.PULL)
        pull.setsockopt(zmq.RCVHWM, int(os.getenv("ZMQ_RCVHWM", "1000")))
        # decoder might be binding or connecting. Most often decoder binds PUSH and we connect PULL.
        # If your decoder is instead connecting PUSH, flip to bind by setting UPSTREAM_PULL_BIND=1.
        if os.getenv("UPSTREAM_PULL_BIND", "0") == "1":
            bind_first(pull, endpoints.pull_bind_candidates(), "PULL")
        else:
            connect_first(pull, endpoints.pull_connect_candidates(), "PULL")

    if upstream_mode in ("sub", "auto"):
        sub = ctx.socket(zmq.SUB)
        sub.setsockopt(zmq.RCVHWM, int(os.getenv("ZMQ_RCVHWM", "1000")))
        # subscribe to everything (or prefix)
        sub.setsockopt(zmq.SUBSCRIBE, upstream_sub_prefix)
        # similar bind/connect uncertainty
        if os.getenv("UPSTREAM_SUB_BIND", "0") == "1":
            bind_first(sub, endpoints.pull_bind_candidates(), "SUB")   # reuse pull ports/socks if desired
        else:
            connect_first(sub, endpoints.pull_connect_candidates(), "SUB")

    poller = zmq.Poller()
    if pull is not None: poller.register(pull, zmq.POLLIN)
    if sub  is not None: poller.register(sub,  zmq.POLLIN)

    print(f"[ZMQ BOX] publishing downstream at {pub_ep}")
    pub.send_multipart([TOPIC_STAT, json.dumps(make_envelope("event.status", {"status": "started", "pub": pub_ep})).encode()])

    # slow-joiner mitigation: give downstream SUBs time to connect
    time.sleep(0.25)

    seq = 0
    last_hb = time.time()

    while True:
        # heartbeat
        now = time.time()
        if now - last_hb >= 1.0:
            hb = make_envelope("event.heartbeat", {"ok": True, "pub": pub_ep})
            pub.send_multipart([TOPIC_HB, json.dumps(hb).encode()])
            last_hb = now

        socks = dict(poller.poll(timeout=50))
        if not socks:
            continue

        # Receive from PULL (JSON dict expected)
        if pull is not None and pull in socks:
            try:
                payload = pull.recv_json(flags=0)
            except Exception as e:
                err = make_envelope("event.status", {"status": "pull_recv_error", "error": str(e)})
                pub.send_multipart([TOPIC_STAT, json.dumps(err).encode()])
                continue

            seq += 1
            topic, kind = route_topic(payload)
            env = make_envelope(kind, payload, seq=seq)

            pub.send_multipart([topic, json.dumps(env).encode()])

        # Receive from SUB (could be [topic, bytes] or a single frame; handle both)
        if sub is not None and sub in socks:
            try:
                parts = sub.recv_multipart(flags=0)
            except Exception as e:
                err = make_envelope("event.status", {"status": "sub_recv_error", "error": str(e)})
                pub.send_multipart([TOPIC_STAT, json.dumps(err).encode()])
                continue

            # If upstream includes its own topic, it will be parts[0]
            if len(parts) == 2 and parts[0].startswith(b""):
                upstream_topic = parts[0]
                body = parts[1]
            else:
                upstream_topic = b""
                body = parts[0]

            # Try JSON decode first; otherwise treat as raw bytes
            try:
                payload = json.loads(body.decode())
                seq += 1
                topic, kind = route_topic(payload)
                env = make_envelope(kind, payload, seq=seq)
                pub.send_multipart([topic, json.dumps(env).encode()])
            except Exception:
                seq += 1
                raw_payload = {
                    "upstream_topic": upstream_topic.decode(errors="ignore"),
                    "bytes_b64": body.hex(),  # hex is simple; swap to base64 if preferred
                }
                env = make_envelope("raw.frame", raw_payload, seq=seq)
                pub.send_multipart([TOPIC_RAW, json.dumps(env).encode()])

if __name__ == "__main__":
    main()
