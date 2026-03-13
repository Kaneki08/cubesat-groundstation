# Overview
The transmission chain is simple:
`RTL-SDR -> GNU Radio Decoder -> Forwarding Program -> FastAPI -> Live Dashboard`

**GNU Radio:** decodes packets and outputs a packet containing bytes of data.

**ZMQ PUB socket** is a messasging pattern that will broadcast messages to subscribed listeners like our `forwarder.py` script.

**Forwarding Script** will subscribe to the ZMQ and convert the bytes to a format (JSON, hex, etc.) readable by FastAPI

**FastAPI** will save the values (database stack tbh) and will send data to live dashboard via a WebSocket connection

# Dependencies
GNU Radio doesn't support LoRa transmission by default but there is a 