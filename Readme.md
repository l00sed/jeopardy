## Synopsis

A HTML5 version of Jeopardy using Javascript, JQuery, JSON, and Bootstrap.

Now includes a **Random Board Generator** that creates boards from historical Jeopardy questions with difficulty filtering!

"Merry Melodies" (Christmas Songs)
"Tab-pourri" (Tabi facts)

## Features

- ✅ Full Jeopardy game experience (Jeopardy, Double Jeopardy, Final Jeopardy)
- ✅ Daily Double support
- ✅ Three player scoring
- ✅ Sound effects and theme music
- ✅ **NEW: Random board generation with difficulty levels (Easy/Medium/Hard)**
- ✅ Load custom board files or generate random ones
- ✅ Built on 217,000+ historical Jeopardy questions

## Code Example

<!--![alt tag](https://pbs.twimg.com/media/CMypgi4WcAA1U7_.png)-->
![preview](./images/screenshot.png)

Use board.json for sample input. Use that format when loading the game.

## Motivation

At PAX East 2014, the PowerPoint version of Jeopardy used for Game Show night vomited all the answers, so I thought that there has to be a better HTML5 version of this so that it works.

## Installation

1. Clone or download this repository
2. Ensure you have the `jeopardy_questions_archive.json` file (contains historical questions)
3. Open `index.html` in a web browser

### For Random Board Generation:

1. Install Python 3 (if not already installed)
2. (Optional) Install ftfy for better text formatting: `pip install ftfy`
3. Generate boards using the script:
   ```bash
   python3 random_board_generator.py --difficulty medium
   ```
4. Or generate all difficulty levels at once:
   ```bash
   ./generate_all_boards.sh
   ```

See [RANDOM_BOARD_GENERATOR_README.md](RANDOM_BOARD_GENERATOR_README.md) for detailed instructions.

## Usage

### Loading a Board

**Option 1: Generate Random Board**
1. Run: `python3 random_board_generator.py --difficulty easy`
2. Open `index.html` in browser
3. Select difficulty from dropdown
4. Click "Generate Random Board"

**Option 2: Load Existing Board**
1. Open `index.html` in browser
2. Click "Choose File" and select a board JSON file
3. Click "Load Game"

### Board Format

Use `board.json` for sample input format. Custom boards should follow this structure:
- `jeopardy`: Array of 6 categories with 5 questions each
- `double-jeopardy`: Array of 6 categories with 5 questions each
- `final-jeopardy`: Single question object

## Random Board Generator

Generate fresh boards with different difficulty levels:

```bash
# Easy difficulty ($100-$500 questions)
python3 random_board_generator.py --difficulty easy

# Medium difficulty ($200-$1000 questions)
python3 random_board_generator.py --difficulty medium

# Hard difficulty ($400-$2000 questions)
python3 random_board_generator.py --difficulty hard
```

Each difficulty level filters questions based on their dollar value to ensure appropriate challenge levels.

For complete documentation, see [RANDOM_BOARD_GENERATOR_README.md](RANDOM_BOARD_GENERATOR_README.md).

## TODO

- Whatever Dan wants at this point.

## Contributors

Special thanks to Dan Amrich for giving the blessing to work on this project.

Thanks to Ryan McDevitt for posting a general framework to base improvements on.

## License

This software is GNU GPL v3. Feel free to contribute to the TODO projects or modify it to your needs.
