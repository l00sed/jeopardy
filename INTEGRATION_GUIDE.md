# Integration with Your Existing Node.js Server (Port 3000)

Since you're already running a Node.js server on port 3000, here's how to add the random board generation endpoint to it.

## Option 1: Add to Your Existing Server (Recommended)

If you're using Express, add this to your server file:

```javascript
const boardGenerator = require('./server.js');

// Add this route
app.get('/api/generate-board', boardGenerator.handleGenerateBoard);
```

If you're using vanilla Node http server:

```javascript
const boardGenerator = require('./server.js');

// In your request handler
if (req.url.startsWith('/api/generate-board')) {
    boardGenerator.handleGenerateBoard(req, res);
    return;
}
```

## Option 2: Run on Different Port

If modifying your existing server is complicated, you can run the board generator on a different port:

1. Edit `server.js` and change line 333:
   ```javascript
   const PORT = 3001; // Changed from 3000
   ```

2. Edit `js/jeopardy.js` and change the URL:
   ```javascript
   url: 'http://localhost:3001/api/generate-board?difficulty=' + difficulty,
   ```

3. Run the board generator server:
   ```bash
   node server.js
   ```

## Option 3: Simpler Workaround - Use Python Server on Different Port

Easiest option if you don't want to modify your Node server:

1. Edit `board_server.py` line 75:
   ```python
   PORT = 8000  # Use different port
   ```

2. Edit `js/jeopardy.js`:
   ```javascript
   url: 'http://localhost:8000/api/generate-board?difficulty=' + difficulty,
   ```

3. Run Python server:
   ```bash
   python3 board_server.py
   ```

## Current Status

- Your Node server: Running on port 3000
- Board generator API needed: `/api/generate-board?difficulty=easy|medium|hard`
- Current error: "Cannot GET /api/generate-board" - endpoint doesn't exist yet

## What to Do

Choose one of the options above. I recommend **Option 3** (Python on port 8000) as it requires no changes to your existing Node server.
