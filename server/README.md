# CubeSat Ground Station - Server Setup

**Guide to set up and run the backend (FastAPI + Python server).**

If you want to run everything together with one command, see the main [README.md](../README.md) and use `./dev.sh`.

This guide is for setting up **only the backend server**.

## Table of contents

- [What you need](#what-you-need)
- [Set up virtual environment](#set-up-virtual-environment)
- [Install dependencies](#install-dependencies)
- [Run the server](#run-the-server)
- [Test it works](#test-it-works)
- [Common problems](#common-problems)

## What you need

- **Python 3.8 or newer** — Check: `python3 --version`
- Install from https://www.python.org/downloads/ if needed

## Set up virtual environment

A virtual environment keeps the server's Python packages separate from other projects.

Make sure you're in the `server/` folder, then run this once:

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

If it worked, you should see `(venv)` at the start of your terminal line.

## Install dependencies

With `(venv)` showing in your terminal, run:

```bash
pip install -r requirements.txt
```

This downloads:

- **FastAPI** — web framework for the server
- **Uvicorn** — runs the server
- **NumPy** — processes IQ signal data
- **WebSockets** — real-time communication with the UI

## Run the server

### Easiest way: Run everything together

From the **project root** (not the server folder), run:

```bash
chmod +x dev.sh  # Only needed once
./dev.sh
```

Make sure `(venv)` is activeon http://127.0.0.1:8000

````

## Test it works

Open your browser and go to:

**http://127.0.0.1:8000**

You should see the CubeSat dashboard with telemetry and waterfall plot.

To test the API endpoint, open a new terminal and run:

```bash
curl http://127.0.0.1:8000/health
````

You should see:

```json
{ "status": "ok" }
```

## Common problems

**"command not found: python3"**

- Python is not installed. Get it from https://www.python.org/downloads/

**"No module named 'fastapi'"**

- Did you activate the virtual environment? Look for `(venv)` at the start of your terminal
- Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
- Then run `pip install -r requirements.txt` again

**"Address already in use"**

- The port 8000 is taken by something else
- Stop this server and try:
  ```bash
  fastapi run app_fastapi.py --port 8001
  ```

**"Connection refused" errors**

- Make sure the server is running. You should see the "Uvicorn running" message

**Still stuck?**

- Ask in the team chat with the exact error message
