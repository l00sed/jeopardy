# Random Jeopardy Board Generator

This feature allows you to generate random Jeopardy boards from the historical archive dataset with difficulty-based filtering.

## Quick Start

### Option 1: Generate Random Boards via Python Script (Recommended)

1. **Generate a board using the command line:**

```bash
python3 random_board_generator.py --difficulty medium
```

This will create a file `boards/board_random.json` that you can load in the game.

2. **Open the Jeopardy game** in your browser (open `index.html`)

3. **Click "Generate Random Board"** - The game will automatically load the board you just generated

### Option 2: Pre-generate Multiple Difficulty Boards

Generate all three difficulty levels at once:

```bash
# Generate easy board
python3 random_board_generator.py --difficulty easy --output boards/board_random_easy.json

# Generate medium board
python3 random_board_generator.py --difficulty medium --output boards/board_random_medium.json

# Generate hard board
python3 random_board_generator.py --difficulty hard --output boards/board_random_hard.json
```

Now when you click "Generate Random Board" in the game and select a difficulty, it will automatically load the corresponding pre-generated board.

## Command Line Options

```bash
python3 random_board_generator.py [OPTIONS]
```

### Available Options:

- `--difficulty {easy,medium,hard}` - Difficulty level (default: medium)
  - **Easy**: Questions valued at $100-$500 (early round questions)
  - **Medium**: Questions valued at $200-$1000 (standard difficulty)
  - **Hard**: Questions valued at $400-$2000 (late round questions)

- `--output FILENAME` - Output filename (default: `boards/board_random.json`)

- `--archive FILENAME` - Path to archive file (default: `jeopardy_questions_archive.json`)

### Examples:

```bash
# Generate an easy board
python3 random_board_generator.py --difficulty easy

# Generate a hard board with custom filename
python3 random_board_generator.py --difficulty hard --output boards/my_hard_board.json

# Use a different archive file
python3 random_board_generator.py --archive custom_archive.json --difficulty medium
```

## How It Works

### Board Generation Process:

1. **Loads the archive** - Reads from `jeopardy_questions_archive.json` (~217,000 questions)

2. **Organizes by category** - Groups all questions by their category and round

3. **Selects random categories** - Picks 6 random categories for Jeopardy round and 6 for Double Jeopardy

4. **Filters by difficulty** - For each category, selects 5 questions matching the difficulty level's value range

5. **Adds Daily Doubles** - Randomly places 1 Daily Double in Jeopardy round and 2 in Double Jeopardy round (avoiding first two rows)

6. **Selects Final Jeopardy** - Randomly picks a Final Jeopardy question from the archive

### Difficulty Mappings:

| Difficulty | Jeopardy Round Values | Double Jeopardy Values |
|-----------|----------------------|----------------------|
| Easy | $100, $200, $300, $400, $500 | $200, $400, $600, $800, $1000 |
| Medium | $200, $400, $600, $800, $1000 | $400, $800, $1200, $1600, $2000 |
| Hard | $400, $600, $800, $1000, $1200 | $800, $1200, $1600, $2000 |

## Using in the Game

### Method 1: Generate and Load Automatically

1. Generate a board: `python3 random_board_generator.py --difficulty easy`
2. Open the game in your browser
3. Select difficulty in the dropdown
4. Click "Generate Random Board"
5. The board loads automatically!

### Method 2: Generate and Load via File Picker

1. Generate a board: `python3 random_board_generator.py --difficulty medium --output boards/my_custom_board.json`
2. Open the game in your browser
3. Use the "Load Existing Board" file picker
4. Select your generated board file
5. Click "Load Game"

## Troubleshooting

### "No random board found!" Error

This means the board file doesn't exist yet. Generate it first:

```bash
python3 random_board_generator.py --difficulty medium
```

### "ModuleNotFoundError: No module named 'ftfy'"

The script will work without `ftfy`, but for better text formatting, install it:

```bash
pip install ftfy
```

### No Categories Selected

If you see "Only X categories available", the archive might not have enough variety for your difficulty. Try a different difficulty level.

## Tips for Best Results

1. **Generate fresh boards** before each game session for maximum variety
2. **Mix difficulty levels** - Start easy and generate harder boards as players warm up
3. **Pre-generate boards** before game night so loading is instant
4. **Keep the archive updated** - More questions = more variety in generated boards

## Technical Details

### Board Structure

Each generated board follows this JSON structure:

```json
{
    "jeopardy": [
        {
            "name": "CATEGORY NAME",
            "questions": [
                {
                    "value": 200,
                    "question": "THE QUESTION TEXT",
                    "answer": "The answer",
                    "daily-double": "true"  // Only on some questions
                }
            ]
        }
    ],
    "double-jeopardy": [ /* same structure */ ],
    "final-jeopardy": {
        "category": "FINAL CATEGORY",
        "question": "FINAL QUESTION",
        "answer": "Final answer"
    }
}
```

### Archive Format

The generator reads from `jeopardy_questions_archive.json`, which contains historical Jeopardy questions in this format:

```json
{
    "category": "CATEGORY NAME",
    "air_date": "2004-12-31",
    "question": "The question text",
    "value": "$200",
    "answer": "The answer",
    "round": "Jeopardy!",
    "show_number": "4680"
}
```

## Batch Generation Script

Want to generate multiple random boards at once? Create a bash script:

```bash
#!/bin/bash
# generate_multiple_boards.sh

for i in {1..5}; do
    python3 random_board_generator.py --difficulty easy --output "boards/board_random_easy_$i.json"
    python3 random_board_generator.py --difficulty medium --output "boards/board_random_medium_$i.json"
    python3 random_board_generator.py --difficulty hard --output "boards/board_random_hard_$i.json"
done

echo "Generated 15 random boards (5 of each difficulty)!"
```

Make it executable and run:

```bash
chmod +x generate_multiple_boards.sh
./generate_multiple_boards.sh
```

## Future Enhancements

Possible improvements for future versions:

- Category filtering (only science, history, etc.)
- Custom value ranges
- Guaranteed category diversity (no similar categories)
- Web-based generation (no Python required)
- Progressive difficulty within a single board
- Theme-based board generation (all 80s, all movies, etc.)

## Credits

- Archive dataset contains historical Jeopardy questions
- Generator script by Dan Tompkins
- Built for the HTML5 Jeopardy Game application

## License

GNU GPL v3 - Same as the main Jeopardy game application
