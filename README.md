# CubeSat Ground Station

**Real-time satellite telemetry dashboard with RF signal visualization.**

This project displays live CubeSat data: power levels, orientation, radio link status, and an RF waterfall plot showing signal strength over time.

## Project structure

```
cubesat-groundstation-ui/
├── dev.sh               (one-command launcher script)
├── server/              (Python backend with FastAPI)
│   ├── app_fastapi.py   (main server code)
│   ├── requirements.txt (Python packages)
│   ├── *.iq             (test IQ signal files)
│   └── README.md        (backend setup guide)
│
├── ui/                  (React + TypeScript frontend)
│   ├── src/             (source code)
│   ├── public/          (static assets)
│   ├── package.json     (JavaScript packages)
│   └── README.md        (frontend setup guide)
│
└── README.md            (this file — start here!)
```

## What this system does

- **Telemetry Dashboard** — View power, orientation, and radio status in real-time
- **RF Waterfall Plot** — Live FFT visualization of IQ signal data
- **WebSocket Streaming** — Data updates continuously without page refresh
- **Single Port** — UI and backend run together on port 8000 for simplicity
- **Offline capable** — Works entirely on your local machine, no internet needed

## What you need to install

Before running the project, you need three things on your computer:

1. **Python 3.8+** (for the backend server)
2. **Node.js** (includes npm — for the frontend UI)
3. **Git** (to download the project)

**If you already have these installed, skip to [Quick Start](#quick-start-recommended).**

If you need to install them, follow the detailed guides in the sections below:

- [Step 1: Install Python](#step-1-install-python)
- [Step 2: Install Node.js](#step-2-install-nodejs)
- [Step 3: Install Git](#step-3-install-git)

## Quick start (recommended)

### Run with one command

From the project root, run:

```bash or seeing errors?

If you see an error about missing dependencies, follow the complete setup guide below starting with [Step 1: Install Python](#step-1-install-python).

## Complete setup guide

Follow these steps if this is your first time or if the quick start didn't work
```

**What this does:**

1. Builds the React UI for production
2. Starts FastAPI server on port 8000
3. Serves both backend API and frontend UI together

Open your browser to: **http://127.0.0.1:8000**

Press `Ctrl+C` to stop.

### First time? Follow the setup guide below

If Step 1: Install Python](#step-1-install-python)

- [Step 2: Install Node.js](#step-2-install-nodejs)
- [Step 3: Install Git](#step-3-install-git)
- [Step 4: Get the project](#step-4-get-the-project)
- [Step 5: Set up the backend](#step-5-set-up-the-backend)
- [Step 6: Set up the frontend](#step-6-set-up-the-frontend)
- [Step 7: Run everything](#step-7-run-everything)
- [Alternative: Run components separately](#alternative-run-components-separately)
- [Common problems](#common-problems)

2. **Node.js** (includes npm — for the frontend UI)
3. **Git** (to download the project)

Follow the guides below for your operating system.

## Step 1: Install Python

The backend server runs on Python.

### macOS

Open Terminal and run:

```bash
python3 --version
```

If you see a version number (like `Python 3.11.0`), you're good!

If not, download from: **https://www.python.org/downloads/**

### Windows

Open PowerShell and run:

```bash
python --version
```

If you see a version, you're good!

If not, download from: **https://www.python.org/downloads/**  
During install, **check "Add Python to PATH"**

### Linux

```bash
python3 --version
```

If not installed:

```bash
sudo apt install python3 python3-pip python3-venv  # Ubuntu/Debian
```

## Step 2: Install Node.js

The frontend UI needs Node.js to build and run.

### All platforms

1. Go to **https://nodejs.org**
2. Download the **LTS** version (recommended for most users)
3. Run the installer and follow the prompts

Verify installation by opening a new terminal and running:

```bash
node --version
npm --version
```

You should see version numbers for both.

## Step 3: Install Git

Git lets you download the project from GitHub.

### macOS

Open Terminal and run:

```bash
git --version
```

If it's not installed, macOS will ask if you want to install developer tools — click "Install" and follow the prompts.

### Windows

Download and install from: **https://git-scm.com/downloads**

### Linux

```bash
sudo apt install git  # Ubuntu/Debian
```

## Step 4: Get the project

Now download the project code.

1. Open Terminal (macOS/Linux) or PowerShell (Windows)

2. Navigate to where you keep projects:

```bash
cd ~/projects  # or wherever you want
```

3. Clone the project:

```bash
git clone https://github.com/Kaneki08/cubesat-groundstation.git
cd cubesat-groundstation
```

You now have all the code!

## Step 5: Set up the backend

### Create Python virtual environment

From the project root, go to the server folder:

```bash
cd server
```

Create a virtual environment:

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal line.

### Install Python packages

With the virtual environment active, run:

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, NumPy, and WebSockets.

**Full backend guide:** See [server/README.md](server/README.md)

## Step 6: Set up the frontend

### Install JavaScript packages

From the server folder, go back and into the UI folder:

```bash
cd ../ui
```

Install all dependencies:

```bash
npm install
```

This installs React, TypeScript, Vite, Tailwind, and other UI dependencies.

**Full frontend guide:** See [ui/README.md](ui/README.md)

## Step 7: Run everything

Now that everything is installed, go back to the project root:

```bash
cd ..
```

Make the launcher script executable (only needed once):

```bash
chmod +x dev.sh
```

Run the project:

```bash
./dev.sh
```

This will:

1. Build the UI for production
2. Start the server on port 8000

Open your browser to: **http://127.0.0.1:8000**

You should see the CubeSat dashboard!

Press `Ctrl+C` to stop the server.

## Alternative: Run components separately

If you want to work on the backend or frontend independently:

### Backend only

Follow the [server/README.md](server/README.md) guide.

Run from the `server/` folder:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
fastapi run app_fastapi.py
```

### Frontend only (development mode)

Follow the [ui/README.md](ui/README.md) guide.

Run from the `ui/` folder:

```bash
npm run dev
```

This runs the UI with hot-reload on port 5173.

**Note:** For full functionality, both backend and frontend need to be running.

## Common problems

**"command not found: ./dev.sh"**

- Make sure you're in the project root directory
- Run: `chmod +x dev.sh` then `./dev.sh`

**"Missing FastAPI CLI in server venv"**

- Go back to Step 5 and make sure you activated the virtual environment
- Run: `pip install -r requirements.txt` again

**"command not found: python3" or "command not found: npm"**

- Go back to Step 1 or Step 2 and install Python or Node.js

**"Port 8000 already in use"**

- Another program is using port 8000
- Find and stop it, or edit `dev.sh` to use `--port 8001`

**Dashboard shows "offline" or "connecting"**

- Make sure the server is running (you should see "Uvicorn running" in terminal)
- Check that you're accessing `http://127.0.0.1:8000` not a different port

**Still stuck?**

- Check the detailed guides: [server/README.md](server/README.md) or [ui/README.md](ui/README.md)
- Ask in the team chat with your specific error message

## How it works

1. **Backend** reads IQ signal files (`.iq` format) and runs FFT to generate spectrum data
2. **Backend** simulates telemetry packets (power, orientation, radio stats)
3. **Backend** streams data to the frontend via WebSocket connections
4. **Frontend** displays telemetry in real-time cards and plots waterfall visualization
5. **Everything runs locally** — no internet or external services needed!
