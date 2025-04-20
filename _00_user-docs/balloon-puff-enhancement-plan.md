# Balloon Puff Game Enhancement Plan

**Goal:** Enhance the Balloon Puff game with retro sound effects, cycle-through scenery, and a start screen with options, based on user selections:
*   **Sound:** Basic HTML5 Audio
*   **Scenery:** Themed Scenery (Mountain, City, Beach)
*   **Start Screen:** Modify existing `#message` Div

---

## Phase 1: Setup & Start Screen

1.  **HTML Modifications (`balloon-puff.html`):**
    *   **Audio Elements:** Add hidden `<audio>` elements within the `<body>` for the sound effects. Assign IDs (`puffSound`, `gameOverSound`) and set `preload="auto"`. *Note: Actual sound file paths (`src`) need to be determined.*
        ```html
        <audio id="puffSound" src="sounds/puff.wav" preload="auto"></audio> <!-- Example path -->
        <audio id="gameOverSound" src="sounds/game_over.wav" preload="auto"></audio> <!-- Example path -->
        ```
    *   **Modify `#message` Div:** Restructure to contain two main child divs: `#startScreenContent` (visible initially) and `#gameOverContent` (hidden initially).
        *   Populate `#startScreenContent` with a title (`<h2>`), labels and inputs for Sound toggle (checkbox), Difficulty selection (radio buttons: easy, normal, hard), Theme selection (select dropdown: Mountain, City, Beach), and a "Start Game" button (`#startButton`).
        *   Populate `#gameOverContent` with the original game over text (`#messageText`), instructions (`<small>`), and the restart button (`#restartButton`).
        ```html
        <div id="message">
            <!-- Start Screen Content (initially visible) -->
            <div id="startScreenContent">
                <h2>Balloon Puff Options</h2>
                <div>
                    <label>
                        <input type="checkbox" id="soundToggle" checked> Sound On
                    </label>
                </div>
                <div>
                    Difficulty:
                    <label><input type="radio" name="difficulty" value="easy" checked> Easy</label>
                    <label><input type="radio" name="difficulty" value="normal"> Normal</label>
                    <label><input type="radio" name="difficulty" value="hard"> Hard</label>
                </div>
                 <div>
                    Starting Theme:
                    <select id="themeSelect">
                        <option value="mountain">Mountain</option>
                        <option value="city">City</option>
                        <option value="beach">Beach</option>
                    </select>
                </div>
                <button id="startButton">Start Game</button>
            </div>

            <!-- Game Over Content (initially hidden) -->
            <div id="gameOverContent" style="display: none;">
                <span id="messageText">Game Over!</span>
                <small>(Press SPACE or click Restart)</small>
                <button id="restartButton">Restart</button>
            </div>
        </div>
        ```

2.  **CSS Modifications (within `<style>` tags):**
    *   Adjust `#message` styles for initial visibility and centering.
    *   Style the new form elements (`label`, `input`, `select`, `#startButton`) to match the retro theme.
    *   Ensure `#gameOverContent` has `display: none;` initially.

3.  **JavaScript Modifications (Initial Setup & Start Logic):**
    *   **Global Variables:** Add `soundEnabled`, `currentDifficulty`, `currentTheme`, `themes` array, and references to new DOM elements (`soundToggle`, `difficultyRadios`, `themeSelect`, `startButton`, `startScreenContent`, `gameOverContent`, `puffSoundElement`, `gameOverSoundElement`).
    *   **`window.onload`:** Modify to show the start screen content within `#message` and hide the game over content. Do *not* call `init()` directly.
    *   **New `startGame()` Function:**
        *   Create this function.
        *   Add event listener: `startButton.addEventListener('click', startGame);`.
        *   Inside `startGame()`: Read options from inputs, update global variables (`soundEnabled`, `currentDifficulty`, `currentTheme`), hide `#message`, call `init()`.
    *   **Modify `init()`:**
        *   Apply difficulty settings based on `currentDifficulty`. Define parameter sets (e.g., `const difficulties = { easy: {...}, normal: {...}, hard: {...} };`) and apply `difficulties[currentDifficulty]` values to game constants like `GRAVITY`, `LIFT`, etc.
        *   Ensure `resetGame()` is called to set the initial state based on selected theme/difficulty *before* starting the loop.
        *   Keep existing event listener additions.
        *   Call `gameLoop()` at the end.
    *   **Modify `resetGame()`:**
        *   Reset game state variables (balloon position, obstacles, etc.).
        *   Apply theme settings based on `currentTheme`.
        *   Apply difficulty settings based on `currentDifficulty`.
    *   **Modify `triggerGameOver()`:**
        *   Stop animation frame.
        *   Show `#message`, hide `#startScreenContent`, show `#gameOverContent`.
        *   Play `gameOverSoundElement` if `soundEnabled`.
    *   **Modify `handleRestart()` (associated with `#restartButton`):** Change this to reload the page (`window.location.reload();`) to return to the start screen cleanly.

---

## Phase 2: Themed Scenery

1.  **JavaScript Modifications:**
    *   **Define Themes:** Create the `themes` array. Each theme object should include `name`, `skyColor`, `groundColor`, `obstacleDrawFn`.
        ```javascript
        const themes = [
            { name: 'mountain', skyColor: '#ADD8E6', groundColor: '#A0522D', obstacleDrawFn: drawMountainObstacles },
            { name: 'city', skyColor: '#778899', groundColor: '#696969', obstacleDrawFn: drawCityObstacles },
            { name: 'beach', skyColor: '#87CEEB', groundColor: '#F4A460', obstacleDrawFn: drawBeachObstacles }
        ];
        // Find the selected theme in startGame() and assign to currentTheme
        // e.g., currentTheme = themes.find(t => t.name === themeSelect.value);
        ```
    *   **Create Theme-Specific Drawing Functions:** Implement `drawMountainObstacles(obstacle)`, `drawCityObstacles(obstacle)`, `drawBeachObstacles(obstacle)`. These functions take an obstacle object and draw it using theme-specific shapes and colors (e.g., rocks, buildings, palm trees).
    *   **Modify Core Drawing Functions:**
        *   **`gameLoop` (Clear Canvas):** Use `ctx.fillStyle = currentTheme.skyColor;`.
        *   **`drawGround()`:** Use `ctx.fillStyle = currentTheme.groundColor;`.
        *   **`drawObstacles()`:** Loop through `obstacles` and call `currentTheme.obstacleDrawFn(obstacle);`.
    *   **Theme Cycling Logic (Optional Extension):** If desired later, add logic (time/score based) to cycle `currentTheme` through the `themes` array during gameplay.

---

## Phase 3: Sound Effects

1.  **JavaScript Modifications:**
    *   **Create `playSound(soundElement)` Helper:**
        ```javascript
        function playSound(soundElement) {
            if (!soundEnabled) return;
            soundElement.currentTime = 0; // Rewind to start
            soundElement.play().catch(error => {
                console.error("Error playing sound:", error);
                // Optional: Disable sound temporarily if playback fails repeatedly
            });
        }
        ```
    *   **Integrate Sound Calls:**
        *   In `handleInteraction` and `handleKeyPress` (for space): Call `playSound(puffSoundElement);`.
        *   In `triggerGameOver()`: Call `playSound(gameOverSoundElement);`.

---

## Phase 4: Refinement & Testing

1.  **Asset Acquisition:** Obtain/create `.wav` or `.mp3` files for "puff" and "game over". Place them in an accessible path (e.g., a `sounds/` folder) and update the `src` attributes in the HTML. Define appropriate color palettes for themes.
2.  **Testing:** Thoroughly test:
    *   Start screen options are correctly applied (sound toggle, difficulty parameters, initial theme).
    *   Difficulty levels feel distinct.
    *   Themes render correctly (sky, ground, obstacles).
    *   Sounds play when expected and respect the sound toggle.
    *   Game over state functions correctly.
    *   Restart button reloads the page, showing the start screen.
---

## Phase 5: Add Parallax Background Scenery

**Goal:** Enhance visual depth and retro feel using parallax scrolling with simple shapes.

1.  **Layer Structure:** Implement 3 background layers:
    *   Layer 1 (Distant): Moves slowest.
    *   Layer 2 (Mid-ground): Moves at a medium speed.
    *   Layer 3 (Foreground): Moves slightly slower than the main ground/obstacles.

2.  **Theme-Specific Elements (Simple Shapes):**
    *   **Mountain Theme:**
        *   Layer 1: Very simple, distant, lighter-colored mountain range silhouette.
        *   Layer 2: Slightly more detailed, darker hills or foothills.
        *   Layer 3: Occasional simple pine tree silhouettes or large rocks near the bottom edge.
    *   **City Theme:**
        *   Layer 1: Basic, distant skyline silhouette (rectangles).
        *   Layer 2: Slightly more detailed buildings, maybe some simple antenna shapes.
        *   Layer 3: Simple lamppost silhouettes or basic fence lines near the bottom.
    *   **Beach Theme:**
        *   Layer 1: Simple ocean horizon line, maybe a distant island silhouette.
        *   Layer 2: Gentle wave shapes (simple curves) moving slowly.
        *   Layer 3: Occasional simple seashell shapes or dune grass near the bottom.

3.  **Data Structure:** Store background elements in separate arrays (e.g., `layer1Elements`, `layer2Elements`, `layer3Elements`). Each element needs `x`, `y`, and potentially `type` or theme-specific properties.

4.  **JavaScript Implementation:**
    *   **Global Variables:** Add layer element arrays and speed factors (e.g., `LAYER1_SPEED_FACTOR = 0.2`).
    *   **Drawing Functions:** Create `drawLayer1()`, `drawLayer2()`, `drawLayer3()`. These will iterate through their respective arrays and draw elements using simple shapes based on `currentTheme`.
    *   **Update Functions:** Create `updateLayer1(speed)`, `updateLayer2(speed)`, `updateLayer3(speed)`. These handle moving elements based on layer speed, spawning new elements off-screen, and removing off-screen elements.
    *   **Modify `gameLoop()`:** Call `updateLayerX` functions early. Call `drawLayerX` functions *before* other game elements, in order (Layer 1 -> Layer 2 -> Layer 3).
    *   **Modify `resetGame()`:** Clear layer arrays and pre-spawn initial elements for the selected theme.

5.  **Refinement & Testing (Phase 6):**
    *   Adjust layer speeds, spawning rates, and color palettes.
    *   Test parallax effect, theme consistency, and performance.
    *   Update the main testing section (previously Phase 4) to include parallax checks.