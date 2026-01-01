# Jeopardy Random Board Generator - Quick Start

## 🚨 IMPORTANT: You're seeing "Failed to generate random board" error?

**The server is not running!** You need to start it first.

## How to Fix (2 Steps):

### Step 1: Start the Server
Open Terminal and run:
```bash
cd /Users/dwtompkins/Downloads/jeopardy
./start_server.sh
```

Or:
```bash
python3 board_server.py
```

**Keep this terminal window open** while playing!

### Step 2: Open the Game
In your browser, go to:
```
http://localhost:8000
```

Or open `start.html` to check if the server is running.

## Why?

The "Generate Random Board" button calls a server API that creates fresh random boards every time. Without the server running, the button can't generate new boards.

**Before:** Loaded static files → same questions  
**After:** Server generates fresh boards → different questions every time!

## Full Instructions

See `GET_STARTED.txt` for complete instructions.
