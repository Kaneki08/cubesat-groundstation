import pytest
from listener import decodeHeader, decodeContent, HEADER_SIZE

packet = (
    bytes([0x01]) +
    bytes([0x02]) +
    (1).to_bytes(2, 'big') +
    (42).to_bytes(4, 'big') +
    b'$' +
    bytes([10]) +
    b'HelloWorld'
)

def test_decodeHeader_valid():
    header = packet[:HEADER_SIZE]
    result = decodeHeader(header)

    assert result['sat_id'] == 1
    assert result['packet_type'] == 2
    assert result['sequence'] == 1
    assert result['timestamp'] == 42
    assert result['payload_len'] == 10


def test_decodeHeader_short_invalid():
    short_packet = (
        bytes([0x01]) +
        bytes([0x02]) +
        (1).to_bytes(2, 'big') +
        (42).to_bytes(4, 'big')
    )

    with pytest.raises(ValueError):
        decodeHeader(short_packet)

def test_decodeContent_valid():
    content = decodeContent(packet)

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

    content = decodeContent(newPacket)

    assert content == b'Hello'
