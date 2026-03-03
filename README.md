# CubeSat Ground Station

Real-time satellite telemetry dashboard with RF signal visualization.

This project displays live CubeSat data including power levels, orientation, radio link status, and an RF waterfall plot showing signal strength over frequency and time.

## Architecture Overview

The application consists of two primary components:

- **Backend**: FastAPI server that processes IQ signal files, performs FFT analysis for spectrum visualization, simulates telemetry data, and streams real-time updates via WebSocket
- **Frontend**: React + TypeScript dashboard built with Vite, featuring real-time telemetry cards and waterfall plots using modern UI components styled with Tailwind CSS

Both components run on a single port (8000) in production mode for simplified deployment.

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.8+** - Required for the FastAPI backend server
- **Node.js and npm** - Required for building and running the React frontend
- **Git** - For cloning the repository

To verify installations:

```bash
python3 --version  # or python --version on Windows
node --version
npm --version
```

The backend uses a Python virtual environment to isolate dependencies. The setup script will guide you through creating one if needed.

## Installing Prerequisites

If you need to install any of the prerequisites, follow the instructions for your operating system:

### Python 3.8+

**macOS/Linux**:

```bash
# Check if already installed
python3 --version

# macOS: Install via Homebrew
brew install python3

# Ubuntu/Debian Linux
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Windows**:

1. Download from https://www.python.org/downloads/
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify: `python --version`

### Node.js and npm

**All platforms**:

1. Visit https://nodejs.org
2. Download the **LTS version** (recommended)
3. Run the installer and follow the prompts
4. Verify installation:
   ```bash
   node --version
   npm --version
   ```

**macOS alternative** (via Homebrew):

```bash
brew install node
```

**Linux alternative** (Ubuntu/Debian):

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Git

**macOS**:

```bash
# Check if installed
git --version

# If not installed, macOS will prompt to install developer tools
# Or install via Homebrew
brew install git
```

**Windows**:
Download and install from https://git-scm.com/downloads

**Linux** (Ubuntu/Debian):

```bash
sudo apt install git
```

## Quick Start (Recommended)

Run the entire application with a single command:

```bash
chmod +x dev.sh  # Only needed once
./dev.sh
```

This script will:

1. Build the React UI for production
2. Start the FastAPI server on port 8000
3. Serve both the API and static UI files

Open your browser to http://127.0.0.1:8000

Press `Ctrl+C` to stop the server.

**First time setup**: If you encounter missing dependency errors, you'll need to set up the backend and frontend environments first. See [Running Backend and Frontend Separately](#running-backend-and-frontend-separately) for detailed setup instructions.

## Running Backend and Frontend Separately

For development or if you prefer to run components independently:

### Backend Server

The backend can be run standalone from the `server/` directory. This is useful for API development and testing.

**Complete setup and run instructions**: [server/README.md](server/README.md)

The backend README covers:

- Creating a Python virtual environment
- Installing dependencies (FastAPI, Uvicorn, NumPy, WebSockets)
- Running the FastAPI server independently

### Frontend UI

The frontend can be run in development mode from the `ui/` directory with hot-reload capabilities.

**Complete setup and run instructions**: [ui/README.md](ui/README.md)

The frontend README covers:

- Installing Node.js dependencies
- Running the Vite development server
- Building for production

**Note**: For full functionality, both backend (port 8000) and frontend (port 5173 in dev mode) must be running simultaneously when working in development mode.

## Project Structure

```
cubesat-groundstation-ui/
├── dev.sh               # One-command launcher script
├── server/              # Python backend
│   ├── app_fastapi.py   # FastAPI application entry point
│   ├── requirements.txt # Python dependencies
│   ├── *.iq             # Test IQ signal files
│   └── README.md        # Backend setup guide
├── ui/                  # React frontend
│   ├── src/             # React components and pages
│   ├── public/          # Static assets
│   ├── package.json     # Node.js dependencies
│   └── README.md        # Frontend setup guide
└── README.md            # This file
```

## Features

- Real-time telemetry dashboard with live data updates
- RF waterfall plot with FFT visualization of IQ signal data
- WebSocket streaming for continuous data flow
- Fully offline capable - runs entirely on your local machine
- Single-port deployment for simplified hosting
