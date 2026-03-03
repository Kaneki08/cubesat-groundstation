'''
DESCRIPTION: GNU Radio files will broadcast output as a ZMQ message. This
script will serve as the listerner that will suibscribe to this ZMQ message
and pull data to the server.
'''

import zmq
import numpy as np

def main():
    ctx = zmq.Context()

    # Create a SUB (subscriber) socket
    sub = ctx.socket(zmq.SUB)

    # Connect to GNU Radio PUB (publisher) socket; Make sure port # matches what's in loraRX.py
    sub.connect("tcp://127.0.0.1:6001")

    # IMPORTANT: Subscribe to all topics
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    print("Listening on port 6001...")

    # Listerner is set to interperet raw IQ values. This might change upon further testing
    while True:
        data = sub.recv()
        iq = np.frombuffer(data, dtype=np.complex64)
        print("Received", len(iq), "samples")

if __name__ == "__main__":
    main()