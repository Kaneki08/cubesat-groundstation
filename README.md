# CubeSat Groundstation UI

Beginner-friendly guide to run the website locally.

## Table of contents

- [What you need](#what-you-need)
- [Install the tools](#install-the-tools)
- [Get the project](#get-the-project)
- [Install the project dependencies](#install-the-project-dependencies)
- [Run the website](#run-the-website)
- [See your changes](#see-your-changes)
- [Common problems](#common-problems)

## What you need

You only need two things on your computer:

- **Node.js** (this also installs **npm**)
- **Git** (to download the project)

That’s it. You do **not** need to install React or Vite by hand — the project installs them for you.

## Install the tools

### macOS

1. Install Node.js (includes npm):
   - Go to https://nodejs.org
   - Download the **LTS** version and install it.
2. Install Git:
   - Open the **Terminal** app and run:
     - `git --version`
   - If it asks to install, accept the prompt.

### Windows

1. Install Node.js (includes npm):
   - Go to https://nodejs.org
   - Download the **LTS** version and install it.
2. Install Git:
   - Go to https://git-scm.com/downloads and install it.

### Linux

1. Install Node.js (includes npm):
   - Use your package manager or follow https://nodejs.org
2. Install Git:
   - `sudo apt install git` (Ubuntu/Debian)

## Get the project

1. Open **Terminal** (macOS/Linux) or **PowerShell** (Windows).
2. Go to where you keep your projects, then download this one:
   - `git clone https://github.com/Kaneki08/cubesat-groundstation.git`
3. Move into the project folder:
   - `cd cubesat-groundstation`
4. Move into the UI folder:
   - `cd ui`

## Install the project dependencies

Run this **once** from inside the `ui/` folder (it may take a minute):

- `npm install`

This downloads everything the project needs (React, Vite, Tailwind, etc.).

## Run the website

Make sure you're in the `ui/` folder, then start the development server:

- `npm run dev`

You should see a message like:

```
Local: http://localhost:5173/
```

Open that link in your browser.

## See your changes

- Leave the server running.
- Edit files in the `ui/src/` folder.
- Your browser updates automatically when you save.

## Common problems

**“command not found: npm”**
- Node.js is not installed. Install the LTS version from https://nodejs.org.

**Port already in use**
- Something else is using the port. Stop the other app or run:
  - `npm run dev -- --port 5174`

**Still stuck?**
- Ask in the team chat and share the exact error message.
