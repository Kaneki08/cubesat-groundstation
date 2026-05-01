import struct

import pytest
import zmq
import time
from unittest.mock import Mock
from listener import receive_once, decode_header, decode_content, HEADER_SIZE, HeartbeatMonitor, PacketType

packet = (
    bytes([0x01]) +
    bytes([0x02]) +
    (1).to_bytes(2, 'big') +
    (42).to_bytes(4, 'big') +
    b'$' +
    bytes([10]) +
    b'HelloWorld'
)

short_packet = (
    bytes([0x01]) +
    bytes([0x02]) +
    (1).to_bytes(2, 'big') +
    (42).to_bytes(4, 'big')
)

def test_decodeHeader_valid():
    header = packet[:HEADER_SIZE]
    result = decode_header(header)

    assert result['sat_id'] == 1
    assert result['packet_type'] == 2
    assert result['sequence'] == 1
    assert result['timestamp'] == 42
    assert result['payload_len'] == 10


def test_decodeHeader_short_invalid():
    with pytest.raises(ValueError):
        decode_header(short_packet)

def test_decodeContent_valid():
    content = decode_content(packet)

    assert content == b'HelloWorld'

def test_decodeContent_short_valid():
    newPacket = (
        bytes([0x01]) +
        bytes([0x02]) +
        (1).to_bytes(2, 'big') +
        (42).to_bytes(4, 'big') +
        b'$' +
        bytes([5]) +    # payload length = 5
        b'Hello'
    )

    content = decode_content(newPacket)

    assert content == b'Hello'

def test_receive_timeout():
    mock_socket = Mock()
    mock_socket.recv.side_effect = zmq.Again()

    result = receive_once(mock_socket)

    assert result is None

def make_heartbeat(seq: int) -> bytes:
    return (
        bytes([0xFF]) +  # sat_id for heartbeat
        bytes([0xAA]) +  # packet_type for heartbeat
        seq.to_bytes(2, 'big') +
        (0).to_bytes(4, 'big') +  # timestamp can be 0 for heartbeat
        b'$' +
        bytes([10])  # payload length = min for valid packet (10 bytes)
    )

def test_multiple_heartbeats():
    for seq in range(5):
        packet = make_heartbeat(seq)
        header = decode_header(packet)

        assert header['sat_id'] == 0xFF
        assert header['packet_type'] == 0xAA
        assert header['sequence'] == seq
        assert header['timestamp'] == 0
        assert header['payload_len'] == 10

def test_heartbeat_identification():
    packet = make_heartbeat(1)
    monitor = HeartbeatMonitor()

    assert monitor.process_heartbeat_packet(packet) == True

def test_full_pipeline():
    ctx = zmq.Context()

    pub = ctx.socket(zmq.PUB)
    sub = ctx.socket(zmq.SUB)

    endpoint = "tcp://127.0.0.1:6001"
    pub.bind(endpoint)
    sub.connect(endpoint)
    sub.setsockopt(zmq.SUBSCRIBE, b"")

    # Allow subscription to propagate
    time.sleep(0.1)

    packet = (
        bytes([0x01]) +
        bytes([0x02]) +
        (1).to_bytes(2, 'big') +
        (42).to_bytes(4, 'big') +
        b'$' +
        bytes([10]) +
        b'HelloWorld'
    )

    pub.send(packet)

    received_packet = sub.recv()

    header = decode_header(received_packet[:HEADER_SIZE])
    content = decode_content(received_packet)

    assert header['sequence'] == 1
    assert content == b'HelloWorld'

    pub.close()
    sub.close()
    ctx.term()

def test_full_pipeline_imu():
    ctx = zmq.Context()

    pub = ctx.socket(zmq.PUB)
    sub = ctx.socket(zmq.SUB)

    port = pub.bind_to_random_port("tcp://127.0.0.1")
    endpoint = f"tcp://127.0.0.1:{port}"
    sub.connect(endpoint)

    sub.setsockopt(zmq.SUBSCRIBE, b"")

    time.sleep(0.1)

    # Create IMU payload values
    imu_values = (
        9, 1, 1,  # gx, gy, gz
        1, 1, 1,  # ax, ay, az
        1, 6, 1, 7  # qi, qj, qk, qr
    )

    # Pack into bytes (little-endian, signed int16)
    imu_payload = struct.pack("<10h", *imu_values)

    # Build packet
    packet = (
            bytes([0x01]) +  # sat_id
            bytes([PacketType.PACKET_IMU]) +  # packet_type
            (1).to_bytes(2, 'little') +  # sequence
            (42).to_bytes(4, 'little') +  # timestamp
            b'$' +
            (20).to_bytes(1, 'little') + #payload length
            imu_payload
    )

    pub.send(packet)

    received_packet = sub.recv()

    header = decode_header(received_packet[:HEADER_SIZE])
    content = decode_content(received_packet[HEADER_SIZE:], header["packet_type"])

    assert header['packet_type'] == PacketType.PACKET_IMU
    assert header['payload_len'] == 20

    # Validate decoded IMU values
    assert content["gx_dps"] == 9
    assert content["gy_dps"] == 1
    assert content["gz_dps"] == 1

    assert content["ax_mg"] == 1
    assert content["ay_mg"] == 1
    assert content["az_mg"] == 1

    assert content["qi"] == 1
    assert content["qj"] == 6
    assert content["qk"] == 1
    assert content["qr"] == 7

    pub.close()
    sub.close()
    ctx.term()

def main():
    test_full_pipeline_imu()


if __name__ == "__main__":
    main()