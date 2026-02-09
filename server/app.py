"""
CubeSat Groundstation Backend (Telemetry Simulator)

=== WHAT ARE WEBSOCKETS? ===
WebSockets are a way for a server and client to have a LIVE, TWO-WAY conversation.
Unlike regular HTTP (where you request a page and get a response), WebSockets keep
a connection OPEN so the server can push data to the client ANYTIME without the
client asking for it first.

Think of it like:
- HTTP = Sending letters back and forth (request → response, done)
- WebSocket = A phone call (connection stays open, anyone can talk anytime)

This is perfect for real-time data like:
- Live telemetry from satellites
- Chat applications
- Stock market tickers
- Multiplayer games

=== WHAT THIS FILE DOES ===
This file starts a WebSocket server that:
1. Listens for connections from clients (like our React dashboard)
2. Sends fake telemetry data (satellite health info) every second
3. Keeps sending until the client disconnects

Run this file with:
  python app.py

Your frontend will connect to:
  ws://<SERVER_IP>:8765
  (Example: ws://localhost:8765 or ws://192.168.1.100:8765)
"""

# === IMPORTS ===
# These are Python libraries we need. Install websockets with: pip install websockets

import asyncio               # Handles asynchronous programming (doing multiple things "at once")
                            # Lets us run a loop that sleeps/sends data without blocking

import json                  # Convert Python dictionaries → JSON strings
                            # JSON is a text format that JavaScript/React can easily read

import random                # Generate random numbers for fake telemetry values
                            # (In real life, this would come from actual satellite sensors)

import time                  # Get current timestamps (seconds since Jan 1, 1970)

import websockets            # The WebSocket server library
                            # Install with: pip install websockets


# === SERVER CONFIGURATION ===
# These settings control WHERE the server listens for connections

# HOST: Which network interface to listen on
# - "0.0.0.0" = Listen on ALL network interfaces
#   This means:
#   * localhost/127.0.0.1 works (same computer)
#   * Your local IP works (192.168.x.x - other devices on same Wi-Fi)
# - "127.0.0.1" = Only listen locally (can't connect from other devices)
# - "192.168.1.100" = Only listen on that specific IP address
HOST = "0.0.0.0"

# PORT: Which port number to use
# - Must be between 1-65535
# - Ports below 1024 usually need admin/root privileges
# - 8765 is arbitrary but common for WebSocket demos
# - Make sure your firewall allows this port!
# - Your frontend MUST connect to this same port number
PORT = 8765


def make_fake_telemetry() -> dict:
    """
    Generate a fake telemetry packet with random satellite data.

    === WHAT IS TELEMETRY? ===
    Telemetry = data sent FROM the satellite TO ground station
    It tells us the satellite's health: battery level, temperature, signal strength, etc.

    === PARAMETERS ===
    None - this function doesn't take any inputs

    === RETURNS ===
    dict (dictionary): A Python dictionary containing telemetry data
                       This will be converted to JSON before sending to clients

    === TELEMETRY FIELDS EXPLAINED ===
    - type: Identifies this as a "telemetry" message (vs commands, logs, etc.)
    - timestamp: Unix time (seconds since Jan 1, 1970)
    - battery_voltage: Voltage of satellite battery (typical range: 7-8.4V)
    - solar_current: Current from solar panels in Amps (0-2.5A)
    - battery_temp_c: Battery temperature in Celsius (15-35°C is healthy)
    - rssi_dbm: Signal strength in dBm (closer to 0 = stronger, -120 is very weak)
    - snr_db: Signal-to-Noise Ratio in dB (higher = clearer signal)
    - mode: What the radio is doing ("downlink" = sending data to ground)
    - ground_station: Which ground station is receiving ("UCI" = UC Irvine)
    """
    return {
        "type": "telemetry",
        "timestamp": int(time.time()),
        "power": {
            "battery_voltage": round(random.uniform(7.2, 8.4), 2),
            "solar_current": round(random.uniform(0.0, 2.5), 2),
            "battery_temp_c": round(random.uniform(15.0, 35.0), 1),
        },
        "orientation": {
            "roll_deg": round(random.uniform(-10.0, 10.0), 1),
            "pitch_deg": round(random.uniform(-10.0, 10.0), 1),
            "yaw_deg": round(random.uniform(-180.0, 180.0), 1),
        },
        "radio": {
            "frequency_mhz": round(random.uniform(437.0, 437.5), 1),
            "rssi_dbm": random.randint(-120, -60),
            "snr_db": round(random.uniform(-5.0, 15.0), 1),
        },
        "mode": "downlink",
        "ground_station": "UCI",
    }


async def telemetry_stream(websocket):
    """
    Handle a single WebSocket client connection and stream telemetry data.

    === WHAT IS A COROUTINE? ===
    A coroutine is an async function (defined with 'async def').
    It can "pause" with 'await' to let other code run, making it efficient.
    Think of it like multitasking - you can handle many clients without threading.

    === WHAT IS 'async/await'? ===
    - 'async def' = This function can pause and resume
    - 'await' = Pause here until this operation completes, let other code run meanwhile
    Example: 'await asyncio.sleep(1)' pauses THIS client's handler but OTHER clients keep running

    === PARAMETERS ===
    websocket: A WebSocket connection object representing ONE connected client
               - Has methods like: .send() .recv() .close()
               - Automatically provided by the websockets library
               - Each client gets their own websocket object

    === RETURN VALUE ===
    None - This function runs until the client disconnects, then ends

    === WHAT HAPPENS ===
    1. Client connects → this function starts running
    2. Loop forever: create packet → send to client → wait 1 second
    3. Client disconnects → exception raised → function ends
    """
    # Log to console when someone connects (helpful for debugging)
    print("Client connected")

    try:
        # Infinite loop - keep sending data until client disconnects
        while True:
            # STEP 1: Create a fake telemetry packet (Python dictionary)
            packet = make_fake_telemetry()

            # STEP 2: Convert Python dict → JSON string
            # Why? WebSockets send TEXT, not Python objects
            # json.dumps() turns {"key": "value"} into the string '{"key": "value"}'
            message = json.dumps(packet)

            # STEP 3: Send the JSON string to THIS specific client
            # 'await' means "pause here until the send completes, let other clients continue"
            # If this client is slow, it won't block other clients!
            await websocket.send(message)

            # STEP 4: Wait 1 second before sending the next packet
            # 'await asyncio.sleep(1)' means "pause for 1 second but let other code run"
            # This is NON-BLOCKING - other clients keep getting their data!
            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed:
        # This exception is raised when:
        # - Client closes the browser tab
        # - Client navigates away from the page
        # - Network connection drops
        # - Client calls websocket.close() in their code
        print("Client disconnected")
        # Function ends here, Python cleans up the connection automatically


async def main():
    """
    Start the WebSocket server and keep it running forever.

    === PARAMETERS ===
    None

    === RETURNS ===
    Never returns - runs until you press Ctrl+C to stop the program

    === WHAT HAPPENS ===
    1. Creates a WebSocket server listening on HOST:PORT
    2. For each client that connects, runs telemetry_stream() in parallel
    3. Keeps running forever (until program is killed)
    """
    # Print where the server is running (helpful for debugging)
    # f-string lets us insert variables: f"text {variable}" → "text value"
    print(f"Starting WebSocket server on ws://{HOST}:{PORT}")

    # === CREATE THE WEBSOCKET SERVER ===
    # websockets.serve() creates a server that:
    # - Listens on HOST:PORT for WebSocket connections
    # - Calls telemetry_stream(websocket) for EACH new client (in parallel!)
    # - 'async with' ensures the server closes properly if program ends
    #
    # Parameters:
    #   telemetry_stream: Function to call for each client (the "handler")
    #   HOST: IP address to listen on ("0.0.0.0" = all interfaces)
    #   PORT: Port number to listen on (8765)
    async with websockets.serve(telemetry_stream, HOST, PORT):
        # Keep the server alive forever
        # 'await asyncio.Future()' creates a Future that NEVER completes
        # This is a common pattern to keep async programs running
        # Press Ctrl+C to stop the server
        await asyncio.Future()  # Wait forever (until Ctrl+C)


# === MAIN ENTRY POINT ===
# This block only runs if you execute this file directly: python app.py
# It won't run if you import this file into another Python script
if __name__ == "__main__":
    # asyncio.run() does three things:
    # 1. Creates an "event loop" (the engine that runs async code)
    # 2. Runs main() until it completes (which is never, until Ctrl+C)
    # 3. Cleans up and closes the event loop when done
    #
    # === WHAT IS AN EVENT LOOP? ===
    # The event loop is like a task manager that:
    # - Keeps track of all running async functions (coroutines)
    # - Switches between them when they 'await' something
    # - Lets one server handle many clients efficiently without threads
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
