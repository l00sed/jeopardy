/**
 * Node.js API endpoint for generating random Jeopardy boards
 * 
 * Add this to your existing Node.js server (Express/etc)
 * or run standalone with: node server.js
 */

const fs = require('fs');
const path = require('path');

// Cache the archive data in memory (load once)
let archiveData = null;

// Difficulty ranges
const DIFFICULTY_RANGES = {
    'easy': {
        'jeopardy': [100, 200, 300, 400, 500],
        'double-jeopardy': [200, 400, 600, 800, 1000]
    },
    'medium': {
        'jeopardy': [200, 400, 600, 800, 1000],
        'double-jeopardy': [400, 800, 1200, 1600, 2000]
    },
    'hard': {
        'jeopardy': [400, 600, 800, 1000, 1200],
        'double-jeopardy': [800, 1200, 1600, 2000]
    }
};

/**
 * Load the questions archive (cached)
 */
function loadArchive() {
    if (archiveData === null) {
        console.log('Loading Jeopardy questions archive...');
        const archivePath = path.join(__dirname, 'jeopardy_questions_archive.json');
        const rawData = fs.readFileSync(archivePath, 'utf8');
        archiveData = JSON.parse(rawData);
        console.log(`Loaded ${archiveData.length} questions`);
    }
    return archiveData;
}

/**
 * Get numeric value from string like "$200"
 */
function getValueFromString(valueStr) {
    try {
        return parseInt(valueStr.replace(/[$,]/g, ''));
    } catch (e) {
        return 0;
    }
}

/**
 * Organize questions by category and round
 */
function organizeByCategory(archive) {
    const byCategory = {};
    
    for (const question of archive) {
        if (!question.category || !question.round || !question.value || 
            !question.question || !question.answer) {
            continue;
        }
        
        const category = question.category;
        const round = question.round;
        
        // Skip Final Jeopardy (handle separately)
        if (round.includes('Final')) continue;
        
        if (!byCategory[category]) {
            byCategory[category] = {};
        }
        if (!byCategory[category][round]) {
            byCategory[category][round] = [];
        }
        
        byCategory[category][round].push(question);
    }
    
    return byCategory;
}

/**
 * Select unique questions for a category
 */
function selectUniqueQuestions(questions, targetValues) {
    const selected = [];
    const usedQuestions = new Set();
    
    for (const targetValue of targetValues) {
        // Find matching unused questions
        const matching = questions.filter(q => 
            getValueFromString(q.value) === targetValue && 
            !usedQuestions.has(q.question)
        );
        
        if (matching.length > 0) {
            const chosen = matching[Math.floor(Math.random() * matching.length)];
            selected.push(chosen);
            usedQuestions.add(chosen.question);
        } else {
            // Find closest unused value
            const unused = questions.filter(q => !usedQuestions.has(q.question));
            if (unused.length > 0) {
                const closest = unused.reduce((prev, curr) => {
                    const prevDiff = Math.abs(getValueFromString(prev.value) - targetValue);
                    const currDiff = Math.abs(getValueFromString(curr.value) - targetValue);
                    return currDiff < prevDiff ? curr : prev;
                });
                selected.push(closest);
                usedQuestions.add(closest.question);
            } else {
                return null; // Not enough unique questions
            }
        }
    }
    
    return selected;
}

/**
 * Select categories for a round
 */
function selectCategoriesForRound(byCategory, roundName, targetValues, numCategories = 6) {
    // Find viable categories with enough unique questions
    const viableCategories = [];
    
    for (const [category, rounds] of Object.entries(byCategory)) {
        if (!rounds[roundName]) continue;
        
        const questions = rounds[roundName];
        const uniqueQuestions = new Set(questions.map(q => q.question)).size;
        
        if (uniqueQuestions >= 5 && questions.length >= targetValues.length) {
            viableCategories.push(category);
        }
    }
    
    // Randomly select categories
    const shuffled = viableCategories.sort(() => Math.random() - 0.5);
    const selectedCategories = shuffled.slice(0, Math.min(numCategories, shuffled.length));
    
    const roundData = [];
    for (const category of selectedCategories) {
        const questions = byCategory[category][roundName];
        const selectedQuestions = selectUniqueQuestions(questions, targetValues);
        
        if (selectedQuestions) {
            const categoryObj = {
                name: category.toUpperCase(),
                questions: selectedQuestions.map((q, i) => ({
                    value: targetValues[i],
                    question: q.question.toUpperCase(),
                    answer: q.answer
                }))
            };
            roundData.push(categoryObj);
        }
    }
    
    return roundData;
}

/**
 * Add daily doubles to a round
 */
function addDailyDoubles(roundData, numDoubles, minValueIndex = 2) {
    const validPositions = [];
    
    for (let catIdx = 0; catIdx < roundData.length; catIdx++) {
        for (let qIdx = minValueIndex; qIdx < roundData[catIdx].questions.length; qIdx++) {
            validPositions.push([catIdx, qIdx]);
        }
    }
    
    // Shuffle and take first N positions
    const shuffled = validPositions.sort(() => Math.random() - 0.5);
    const ddPositions = shuffled.slice(0, Math.min(numDoubles, shuffled.length));
    
    for (const [catIdx, qIdx] of ddPositions) {
        roundData[catIdx].questions[qIdx]['daily-double'] = 'true';
    }
    
    return roundData;
}

/**
 * Select Final Jeopardy question
 */
function selectFinalJeopardy(archive) {
    const finalQuestions = archive.filter(q => 
        q.round && q.round.includes('Final') && 
        q.category && q.question && q.answer
    );
    
    if (finalQuestions.length === 0) {
        return {
            category: 'RANDOM TRIVIA',
            question: 'THIS IS A PLACEHOLDER FINAL JEOPARDY QUESTION',
            answer: 'What is a placeholder answer?'
        };
    }
    
    const selected = finalQuestions[Math.floor(Math.random() * finalQuestions.length)];
    return {
        category: selected.category.toUpperCase(),
        question: selected.question.toUpperCase(),
        answer: selected.answer
    };
}

/**
 * Generate a complete board
 */
function generateBoard(difficulty = 'medium') {
    if (!DIFFICULTY_RANGES[difficulty]) {
        throw new Error(`Invalid difficulty: ${difficulty}`);
    }
    
    const archive = loadArchive();
    const byCategory = organizeByCategory(archive);
    
    // Generate Jeopardy round
    const jeopardyValues = DIFFICULTY_RANGES[difficulty]['jeopardy'];
    let jeopardyRound = selectCategoriesForRound(byCategory, 'Jeopardy!', jeopardyValues, 6);
    jeopardyRound = addDailyDoubles(jeopardyRound, 1, 2);
    
    // Generate Double Jeopardy round
    const doubleJeopardyValues = DIFFICULTY_RANGES[difficulty]['double-jeopardy'];
    let doubleJeopardyRound = selectCategoriesForRound(byCategory, 'Double Jeopardy!', doubleJeopardyValues, 6);
    doubleJeopardyRound = addDailyDoubles(doubleJeopardyRound, 2, 2);
    
    // Generate Final Jeopardy
    const finalJeopardy = selectFinalJeopardy(archive);
    
    return {
        'jeopardy': jeopardyRound,
        'double-jeopardy': doubleJeopardyRound,
        'final-jeopardy': finalJeopardy
    };
}

/**
 * API handler function - use this in your Express routes
 */
function handleGenerateBoard(req, res) {
    try {
        const difficulty = req.query.difficulty || 'medium';
        
        console.log(`Generating ${difficulty} board...`);
        const board = generateBoard(difficulty);
        console.log(`✓ Board generated successfully`);
        
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
        
        res.json(board);
    } catch (error) {
        console.error('Error generating board:', error);
        res.status(500).json({
            error: error.message,
            message: 'Failed to generate board'
        });
    }
}

// Export for use in your server
module.exports = {
    generateBoard,
    handleGenerateBoard
};

// If running standalone, start a simple server
if (require.main === module) {
    const http = require('http');
    const url = require('url');
    
    const PORT = 3000;
    
    const server = http.createServer((req, res) => {
        const parsedUrl = url.parse(req.url, true);
        
        // CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        
        if (req.method === 'OPTIONS') {
            res.writeHead(200);
            res.end();
            return;
        }
        
        if (parsedUrl.pathname === '/api/generate-board') {
            handleGenerateBoard({ query: parsedUrl.query }, res);
        } else if (parsedUrl.pathname === '/') {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(`
                <h1>Jeopardy Board Generator API</h1>
                <p>Server is running!</p>
                <p>API Endpoint: <code>/api/generate-board?difficulty=easy|medium|hard</code></p>
                <p><a href="/api/generate-board?difficulty=easy">Test API</a></p>
            `);
        } else {
            // Serve static files from current directory
            const filePath = path.join(__dirname, parsedUrl.pathname);
            if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
                const ext = path.extname(filePath);
                const contentTypes = {
                    '.html': 'text/html',
                    '.js': 'text/javascript',
                    '.css': 'text/css',
                    '.json': 'application/json',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.gif': 'image/gif'
                };
                
                res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'text/plain' });
                fs.createReadStream(filePath).pipe(res);
            } else {
                res.writeHead(404);
                res.end('Not Found');
            }
        }
    });
    
    server.listen(PORT, () => {
        console.log('='.repeat(60));
        console.log('Jeopardy Board Generator - Node.js Server');
        console.log('='.repeat(60));
        console.log();
        console.log(`Server running at http://localhost:${PORT}`);
        console.log(`API endpoint: http://localhost:${PORT}/api/generate-board`);
        console.log();
        console.log('Press Ctrl+C to stop');
        console.log();
    });
}
