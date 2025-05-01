// This file handles UI elements, event listeners, sound, and game initialization.

// --- DOM Elements ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const messageDiv = document.getElementById('message');
const messageText = document.getElementById('messageText');
const restartButton = document.getElementById('restartButton');
const startButton = document.getElementById('startButton');
const soundToggle = document.getElementById('soundToggle');
const themeSelect = document.getElementById('themeSelect');
const startScreenContent = document.getElementById('startScreenContent');
const gameOverContent = document.getElementById('gameOverContent');
const puffSound = document.getElementById('puffSound');
const gameOverSound = document.getElementById('gameOverSound');

// --- Game State (UI related) ---
let soundEnabled = true;
let currentTheme;
let currentDifficulty = 'easy';

// --- Helper Functions (UI related) ---
function playSound(sound) {
    if (soundEnabled) {
        sound.currentTime = 0;
        sound.play().catch(error => {
            console.error("Error playing sound:", error);
        });
    }
}

// Game Over state
function triggerGameOver() {
    isGameOver = true;
    cancelAnimationFrame(animationFrameId); // Stop the game loop
    messageDiv.style.display = 'block';
    startScreenContent.style.display = 'none'; // Hide start screen
    gameOverContent.style.display = 'block'; // Show game over content
    // Optional: Add a sound effect here later if needed
}

// Reset game variables to start fresh
function resetGame() {
    balloonY = canvas.height / 3; // Start higher up
    balloonVelY = 0;
    obstacles = [];
    clouds = []; // Reset clouds
    birds = [];  // Reset birds
    backgroundElements = []; // Reset background elements array
    frameCount = 0;
    isGameOver = false;
    messageDiv.style.display = 'none';
    startScreenContent.style.display = 'none'; // Ensure start screen is hidden
    gameOverContent.style.display = 'none'; // Ensure game over content is hidden


    // Pre-spawn background elements
    const horizonY = canvas.height * 0.6; // Use the new higher horizon
    const groundY = canvas.height - 20; // Ground level
    const numToPreSpawn = 10; // Number of background elements to pre-spawn

    for(let i = 0; i < numToPreSpawn; i++) {
        const spawnY = horizonY + Math.random() * (groundY - horizonY);
        const elementTypes = currentTheme.layer1Elements.concat(currentTheme.layer2Elements).concat(currentTheme.layer3Elements);
        const type = elementTypes[Math.floor(Math.random() * elementTypes.length)];

        backgroundElements.push(createLayerElement(
            canvas.width * (i / numToPreSpawn), // Distribute elements across the screen
            spawnY,
            type
        ));
    }

    // Pre-spawn some initial clouds/birds
    for(let i=0; i<3; i++) { updateClouds(difficulties[currentDifficulty].CLOUD_SPEED); } // Pass speed
    for(let i=0; i<1; i++) { updateBirds(difficulties[currentDifficulty].BIRD_SPEED); } // Pass speed
    frameCount = 0; // Reset frame count after pre-spawning
}


// --- Event Listeners ---

// Handle keyboard input with sound effects
function handleKeyPress(e) {
    // If game is over and Space is pressed, restart
    if (isGameOver && e.code === 'Space') {
        handleRestart();
    }
    // If game is running and Space is pressed, puff
    else if (!isGameOver && e.code === 'Space') {
        const difficulty = difficulties[currentDifficulty];
        balloonVelY = difficulty.LIFT;
        playSound(puffSound);

        // Add a little visual puff effect (This might be better in game logic, but keeping here for now)
        // ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        // ctx.beginPath();
        // ctx.arc(canvas.width / 4, balloonY, BALLOON_RADIUS + 10, 0, Math.PI * 2);
        // ctx.fill();
    }
}

// Handle mouse clicks or touch taps with sound effects
function handleInteraction() {
    // If game is over, don't do anything on tap/click
    if (isGameOver) {
        return;
    }
    // If game is running, puff the balloon
    else if (!isGameOver) {
        const difficulty = difficulties[currentDifficulty];
        balloonVelY = difficulty.LIFT;
        playSound(puffSound);

        // Add a little visual puff effect (This might be better in game logic, but keeping here for now)
        // ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        // ctx.beginPath();
        // ctx.arc(canvas.width / 4, balloonY, BALLOON_RADIUS + 10, 0, Math.PI * 2);
        // ctx.fill();
    }
}

// Start new game on restart button click
function handleRestart() {
    if (!animationFrameId || isGameOver) { // Prevent multiple restarts if already running
         resetGame();
         gameLoop(); // Start the loop again
    }
}

// --- Initialization ---
function init() {
    resetGame(); // Set initial positions and clear arrays

    // Add event listeners
    window.addEventListener('keydown', handleKeyPress);
    canvas.addEventListener('mousedown', handleInteraction); // For mouse clicks
    canvas.addEventListener('touchstart', handleInteraction, { passive: true }); // For touch screens (passive for performance)
    restartButton.addEventListener('click', handleRestart);

    // Start the game loop
    gameLoop();
}

// --- Window Load ---
window.onload = () => {
    // Set up initial state
    soundEnabled = soundToggle.checked;
    currentTheme = themes[themeSelect.value];
    currentDifficulty = 'easy';

    // Show start screen
    messageDiv.style.display = 'block';
    startScreenContent.style.display = 'block';
    gameOverContent.style.display = 'none';

    // Event listeners for options
    soundToggle.addEventListener('change', () => {
        soundEnabled = soundToggle.checked;
    });

    themeSelect.addEventListener('change', () => {
        currentTheme = themes[themeSelect.value];
    });

    document.querySelectorAll('input[name="difficulty"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentDifficulty = e.target.value;
        });
    });

    // Start button click handler
    startButton.addEventListener('click', () => {
        messageDiv.style.display = 'none';
        init(); // Start the game with selected options
    });
};