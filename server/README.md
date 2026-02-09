# CubeSat Ground Station Server

Beginner-friendly guide to run the backend on your computer.

The server streams live CubeSat telemetry data to the website. You need to run this first before starting the UI.

## Table of contents

- [What you need](#what-you-need)
- [Create a virtual environment](#create-a-virtual-environment)
- [Install dependencies](#install-dependencies)
- [Run the server](#run-the-server)
- [Test it works](#test-it-works)
- [Common problems](#common-problems)

## What you need

You only need **Python 3.8 or newer**.

(You should have already downloaded the project and navigated to the `server/` folder from the root README.)

## Create a virtual environment

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

This downloads FastAPI and all the server needs.

## Run the server

Make sure you see `(venv)` in your terminal, then run:

```bash
fastapi run app_fastapi.py
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this running and open the UI in a new terminal** (follow the UI README).

## Test it works

Open a new terminal and run:

```bash
curl http://127.0.0.1:8000/health
```

You should see:

```json
{"status":"ok"}
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
