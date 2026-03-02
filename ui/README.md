# CubeSat Ground Station - UI Setup

**Guide to set up and run the frontend (React + TypeScript dashboard).**

If you want to run everything together with one command, see the main [README.md](../README.md) and use `./dev.sh`.

This guide is for running **only the UI** in development mode (useful when working on the frontend separately).

## What you need

- **Node.js** (includes npm) — Install from https://nodejs.org (LTS version)
- The backend server must be running on port 8000 for data to display

## Install dependencies

From the `ui/` folder, run once:

```bash
npm install
```

This installs React, TypeScript, Vite, Tailwind CSS, and all other dependencies.

## Run in development mode

Start the Vite dev server:

```bash
npm run dev
```

You should see:

```
Local: http://localhost:5173/
```

Open that URL in your browser.

**Note:** The dashboard will show "connecting" or "offline" unless the backend server is running on port 8000.

## Build for production

To create an optimized production build:

```bash
npm run build
```

Output goes to `ui/dist/` which the FastAPI server can serve.

## Common problems

**"command not found: npm"**

- Node.js is not installed. Get it from https://nodejs.org

**Port 5173 already in use**

- Run with a different port: `npm run dev -- --port 5174`

**Dashboard shows "offline"**

- Make sure the backend server is running on port 8000
- Check WebSocket URLs in `src/pages/Dashboard.tsx`

**Still stuck?**

- Check the main [README.md](../README.md) or ask in the team chat
