#!/usr/bin/env python3
import sys, signal
from gnuradio import gr, soapy, zeromq

class iq_pub(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "RTLSDR IQ → ZMQ PUB", catch_exceptions=True)

        samp_rate = 1_000_000
        center_freq = 433e6

        # RTL-SDR source (complex float32 stream)
        dev = "driver=rtlsdr"
        stream_args = "bufflen=16384"
        tune_args = [""]
        settings = [""]

        self.src = soapy.source(dev, "fc32", 1, "", stream_args, tune_args, settings)
        self.src.set_sample_rate(0, samp_rate)
        self.src.set_frequency(0, center_freq)
        self.src.set_gain_mode(0, False)
        self.src.set_gain(0, "TUNER", 20)

        # ZMQ PUB stream sink (publishes raw stream bytes)
        # itemsize for complex64 samples:
        self.zmq_pub = zeromq.pub_sink(
            gr.sizeof_gr_complex,   # itemsize (8 bytes for complex64)
            1,                      # vlen (vector length)
            "tcp://127.0.0.1:6001",
            100,                    # timeout
            False,                  # pass_tags
            -1,                     # hwm
            "",                     # key
            True,                   # drop_on_hwm
            True                    # bind
        )
        self.connect(self.src, self.zmq_pub)

def main():
    tb = iq_pub()

    def sig_handler(sig=None, frame=None):
        tb.stop(); tb.wait(); sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    try:
        input("Publishing IQ on tcp://0.0.0.0:6001 (PUB stream). Press Enter to quit...\n")
    except EOFError:
        pass
    tb.stop(); tb.wait()

if __name__ == "__main__":
    main()