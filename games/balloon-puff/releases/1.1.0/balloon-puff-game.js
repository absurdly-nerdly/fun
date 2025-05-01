// This file contains the core game logic for the Balloon Puff game.

// --- Game State ---
let balloonY, balloonVelY;
let obstacles = [];
let clouds = [];
let birds = [];
let frameCount = 0;
let isGameOver = false;
let animationFrameId;

// --- Parallax Background State ---
let backgroundElements = []; // Combined array for all parallax elements

// --- Parallax Spawn Rates (in frames) ---
// We will use a single spawn rate and determine element type/size based on Y position
const BACKGROUND_SPAWN_RATE = 100; // Spawn background elements more frequently

// --- Parallax Background Functions ---
function createLayerElement(x, y, type) { // Removed layer parameter
    const horizonY = canvas.height * 0.6; // Use the new higher horizon
    let baseHeight, width;
    let color;

    // Determine size and color based on Y position (depth)
    if (y < horizonY + 50) { // Distant elements (near horizon)
        baseHeight = 150;
        width = 120;
        color = currentTheme.layer1Color;
    } else if (y < horizonY + (canvas.height - horizonY) * 0.5) { // Mid-ground elements
        baseHeight = 100;
        width = 80;
        color = currentTheme.layer2Color;
    } else if (type === 'ground-detail-rock') {
        // Ground detail rocks (small squares near horizon)
        baseHeight = 10; // Fixed small size
        width = 15; // Fixed small size
        color = currentTheme.groundDetailColor; // Use ground detail color
    }
    else { // Foreground elements (near ground)
        baseHeight = 50;
        width = 40;
        color = currentTheme.layer3Color;
    }

    const heightMultiplier = 0.8 + Math.random() * 0.7; // Vary height
    const height = baseHeight * heightMultiplier;

    // Add specific properties based on type
    const elementProperties = {
        x,
        y: y - (height - baseHeight), // Adjust y so the base is at the intended level
        baseY: y, // Store the base Y for speed calculation
        type,
        width: width,
        height: height,
        color: color, // Use determined color
        mountainColor: currentTheme.mountainColors[Math.floor(Math.random() * currentTheme.mountainColors.length)] // Assign a random color from the full array
    };

    if (type === 'small-rock') {
        elementProperties.rockSize = width * (0.8 + Math.random() * 0.4); // Calculate size once
        elementProperties.rockColor = currentTheme[`rockColor${Math.floor(Math.random() * 2) + 1}`]; // Assign color once
    }

    return elementProperties;
}

function drawLayerElement(element, color, type) {
    // Use the color stored with the element for mountains, otherwise use the passed color
    const drawColor = (type === 'distant-peak' || type === 'rolling-hill' || type === 'foothill' || type === 'cliff') ? element.mountainColor : color;
    ctx.fillStyle = drawColor;

    switch(type) {
        case 'distant-peak':
        case 'rolling-hill':
        case 'foothill': // Add foothills and cliffs to mountain drawing
        case 'cliff':
            // Mountain shape (simplified triangle for now, can be enhanced)
            ctx.beginPath();
            ctx.moveTo(element.x, element.y + element.height);
            ctx.lineTo(element.x + element.width/2, element.y);
            ctx.lineTo(element.x + element.width, element.y + element.height);
            ctx.closePath();
            ctx.fill();

            // Add snow cap to taller mountains
            const horizonY = canvas.height * 0.7;
            if (element.y < horizonY - element.height * 0.4) { // If peak is significantly above horizon
                ctx.fillStyle = currentTheme.snowCapColor;
                ctx.beginPath();
                ctx.moveTo(element.x + element.width/2, element.y);
                ctx.lineTo(element.x + element.width/2 + element.width * 0.2, element.y + element.height * 0.2);
                ctx.lineTo(element.x + element.width/2 - element.width * 0.2, element.y + element.height * 0.2);
                ctx.closePath();
                ctx.fill();
            }
            break;

        case 'skyscraper':
        case 'tower':
            // Rectangle with optional top detail
            ctx.fillRect(element.x, element.y, element.width, element.height);
            ctx.fillRect(element.x + element.width/4, element.y - 10, element.width/2, 10);
            break;

        case 'pine-tree':
            // More detailed pine tree
            const trunkWidth = element.width * 0.2;
            const trunkHeight = element.height * 0.4;
            const canopyHeight = element.height * 0.8;
            const canopyBaseWidth = element.width * 0.8;

            // Trunk
            ctx.fillStyle = currentTheme.groundDetailColor; // Use a brown for trunk
            ctx.fillRect(element.x + element.width/2 - trunkWidth/2, element.y + element.height - trunkHeight, trunkWidth, trunkHeight);

            // Canopy (multiple triangles)
            ctx.fillStyle = currentTheme.treeColor1;
            ctx.beginPath();
            ctx.moveTo(element.x + element.width/2, element.y);
            ctx.lineTo(element.x + element.width/2 + canopyBaseWidth/2, element.y + canopyHeight * 0.4);
            ctx.lineTo(element.x + element.width/2 + canopyBaseWidth * 0.3, element.y + canopyHeight * 0.4);
            ctx.lineTo(element.x + element.width/2 + canopyBaseWidth/2, element.y + canopyHeight * 0.8);
            ctx.lineTo(element.x + element.width/2 + canopyBaseWidth * 0.2, element.y + canopyHeight * 0.8);
            ctx.lineTo(element.x + element.width/2 + canopyBaseWidth/2, element.y + canopyHeight);
            ctx.lineTo(element.x + element.width/2 - canopyBaseWidth/2, element.y + canopyHeight);
            ctx.lineTo(element.x + element.width/2 - canopyBaseWidth * 0.2, element.y + canopyHeight * 0.8);
            ctx.lineTo(element.x + element.width/2 - canopyBaseWidth/2, element.y + canopyHeight * 0.8);
            ctx.lineTo(element.x + element.width/2 - canopyBaseWidth * 0.3, element.y + canopyHeight * 0.4);
            ctx.lineTo(element.x + element.width/2 - canopyBaseWidth/2, element.y + canopyHeight * 0.4);
            ctx.closePath();
            ctx.fill();

            break;

        case 'small-rock':
            // Simple rock shape (circle or irregular shape)
            // const rockSize = element.width * (0.8 + Math.random() * 0.4); // Size is now calculated on creation
            // const rockColor = currentTheme[`rockColor${Math.floor(Math.random() * 2) + 1}`]; // Color is now calculated on creation
            ctx.fillStyle = element.rockColor; // Use stored rockColor

            // Draw a simple circle for now
            ctx.beginPath();
            ctx.arc(element.x + element.width/2, element.y + element.height - element.rockSize/2, element.rockSize/2, 0, Math.PI * 2); // Use stored rockSize
            ctx.fill();

            break;

        case 'horizon':
        case 'wave':
            // Simple horizontal line with wave effect
            ctx.beginPath();
            ctx.moveTo(element.x, element.y + element.height/2);
            for(let i = 0; i <= element.width; i += 20) {
                ctx.lineTo(element.x + i,
                    element.y + element.height/2 + Math.sin(frameCount/20 + i/20) * 5);
            }
            ctx.lineTo(element.x + element.width, element.y + element.height);
            ctx.lineTo(element.x, element.y + element.height);
            ctx.fill();
            break;

        case 'ground-detail-rock':
            // Draw as a simple rectangle (square)
            ctx.fillRect(element.x, element.y, element.width, element.height);
            break;

        default:
            // Simple rectangle for unspecified types
            ctx.fillRect(element.x, element.y, element.width, element.height);
        }
    }

// Update background elements and spawn new ones with depth-based speed
function updateBackgroundElements(baseSpeed) { // Removed spawnRate and layerNum
    const horizonY = canvas.height * 0.6; // Use the new higher horizon
    const groundY = canvas.height - 20; // Ground level

    // Spawn new elements
    if (frameCount % BACKGROUND_SPAWN_RATE === 0) { // Use single spawn rate
        // Add a small chance to spawn ground detail rocks near the horizon
        if (Math.random() < 0.15) { // Adjust probability as needed
             const spawnY = horizonY + Math.random() * 20; // Spawn very close to the horizon
             backgroundElements.push(createLayerElement(
                canvas.width + Math.random() * 100, // Spawn off-screen
                spawnY,
                'ground-detail-rock' // Specify the new type
            ));
        } else {
            // Determine spawn Y randomly between horizon and ground for other elements
            const spawnY = horizonY + Math.random() * (groundY - horizonY);

            // Determine element type based on spawn Y (depth)
            let type;
            const horizonThreshold = horizonY + (canvas.height - horizonY) * 0.3; // Elements above this are more likely mountains

            if (spawnY < horizonThreshold) {
                // More likely to be a mountain type (distant or mid)
                const mountainTypes = currentTheme.layer1Elements.concat(currentTheme.layer2Elements);
                type = mountainTypes[Math.floor(Math.random() * mountainTypes.length)];
            } else {
                // More likely to be a foreground element
                const foregroundTypes = currentTheme.layer3Elements;
                type = foregroundTypes[Math.floor(Math.random() * foregroundTypes.length)];
            }

            // Add a small chance to spawn any type for variety (excluding ground-detail-rock)
            const allTypesExcludingGroundDetail = currentTheme.layer1Elements.concat(currentTheme.layer2Elements).concat(currentTheme.layer3Elements);
            if (Math.random() < 0.1) {
                 type = allTypesExcludingGroundDetail[Math.floor(Math.random() * allTypesExcludingGroundDetail.length)];
            }


            backgroundElements.push(createLayerElement(
                canvas.width + Math.random() * 100, // Spawn off-screen
                spawnY,
                type
            ));
        }
    }

    // Move existing elements based on their depth (baseY)
    const horizonSpeedMultiplier = 0.2; // Elements exactly at horizonY move at baseSpeed * 0.2

    backgroundElements.forEach(element => {
        let speed;
        if (element.baseY <= horizonY) {
            // Elements at or above the horizon move at a fixed slow speed
            speed = baseSpeed * horizonSpeedMultiplier;
        } else {
            // Elements below the horizon interpolate speed based on depth
            const depthBelowHorizon = element.baseY - horizonY;
            const maxDepth = groundY - horizonY;
            const depthMultiplier = maxDepth > 0 ? depthBelowHorizon / maxDepth : 0; // 0 at horizon, 1 at ground, handle division by zero
            // Interpolate between horizonSpeedMultiplier and 1 (full baseSpeed)
            const speedMultiplier = horizonSpeedMultiplier + depthMultiplier * (1 - horizonSpeedMultiplier);
            speed = baseSpeed * speedMultiplier;
        }
        element.x -= speed;
    });

    // Remove off-screen elements
    backgroundElements = backgroundElements.filter(element => element.x + element.width > 0);
}

function drawLayer(elements) { // This function will now draw all background elements
    elements.forEach(element => {
        drawLayerElement(element, element.color, element.type); // Use element's stored color
    });
}

// Draw the mountain ground and horizon
function drawMountainGroundAndHorizon() {
    const horizonY = canvas.height * 0.6; // Horizon line at 60% of canvas height (raised)

    // Draw ground area below horizon
    ctx.fillStyle = currentTheme.groundColor;
    ctx.fillRect(0, horizonY, canvas.width, canvas.height - horizonY);

    // Add some ground detail (optional, can be enhanced later)
    ctx.fillStyle = currentTheme.groundDetailColor;
}


// Draw Clouds
function drawClouds() {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'; // Semi-transparent white
    clouds.forEach(cloud => {
        // Simple cloud shape using multiple circles
        ctx.beginPath();
        ctx.arc(cloud.x, cloud.y, cloud.size, 0, Math.PI * 2);
        ctx.arc(cloud.x + cloud.size * 0.8, cloud.y, cloud.size * 1.2, 0, Math.PI * 2);
        ctx.arc(cloud.x - cloud.size * 0.7, cloud.y, cloud.size * 1.1, 0, Math.PI * 2);
        ctx.arc(cloud.x + cloud.size * 0.2, cloud.y - cloud.size * 0.5, cloud.size, 0, Math.PI * 2);
        ctx.fill();
    });
}

// Update Cloud Positions & Spawn New Ones
function updateClouds(speed) {
    // Spawn new cloud
    if (frameCount % CLOUD_SPAWN_RATE === 0) {
        clouds.push({
            x: canvas.width + Math.random() * 100,
            y: Math.random() * (canvas.height * 0.4) + 50,
            size: Math.random() * 20 + 25
        });
    }
    // Move existing clouds
    clouds.forEach(cloud => {
        cloud.x -= speed;
    });
    // Remove clouds that have moved off-screen
    clouds = clouds.filter(cloud => cloud.x + cloud.size * 2 > 0);
}

// Draw Birds
function drawBirds() {
    ctx.fillStyle = '#333'; // Dark color for birds
     birds.forEach(bird => {
        ctx.beginPath();
        // Simple V shape for wings, alternates based on phase
        const wingYOffset = Math.sin(bird.phase) * 5; // Wing flap effect
        ctx.moveTo(bird.x - 10, bird.y + wingYOffset);
        ctx.lineTo(bird.x, bird.y - wingYOffset);
        ctx.lineTo(bird.x + 10, bird.y + wingYOffset);
        //ctx.closePath(); // Don't close path for V shape
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#333';
        ctx.stroke(); // Use stroke for thin lines
     });
}

// Update Bird Positions & Spawn New Ones
function updateBirds(speed) {
    // Spawn new bird
    if (frameCount % BIRD_SPAWN_RATE === 0) {
        birds.push({
            x: canvas.width + Math.random() * 50,
            y: Math.random() * (canvas.height * 0.5) + 80,
            phase: Math.random() * Math.PI * 2
        });
    }
    // Move existing birds and update phase
    birds.forEach(bird => {
        bird.x -= speed;
        bird.phase += 0.1;
    });
    // Remove birds that have moved off-screen
    birds = birds.filter(bird => bird.x + 10 > 0);
}


// Draw the balloon
function drawBalloon() {
    ctx.fillStyle = balloonColor;
    ctx.beginPath();
    ctx.arc(canvas.width / 4, balloonY, BALLOON_RADIUS, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#A020F0'; // Purple outline
    ctx.lineWidth = 3;
    ctx.stroke();

    // Simple balloon string
    ctx.strokeStyle = '#555';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 4, balloonY + BALLOON_RADIUS);
    ctx.lineTo(canvas.width / 4, balloonY + BALLOON_RADIUS + 15);
    ctx.stroke();
}

// Draw obstacles using current theme
function drawObstacles() {
    obstacles.forEach(obstacle => {
        currentTheme.drawObstacle(obstacle);
    });
}

// Update balloon position and velocity
function updateBalloon(gravity) {
    balloonVelY += gravity;
    balloonY += balloonVelY;

    // Prevent balloon from going off the top
    if (balloonY - BALLOON_RADIUS < 0) {
        balloonY = BALLOON_RADIUS;
        balloonVelY = 0;
    }
}

// Update obstacle positions and spawn new ones
function updateObstacles(speed, spawnRate) {
    // Spawn new obstacle only if game is running
    if (!isGameOver && frameCount % spawnRate === 0) {
        // The y position is the top of the trunk
        const minTrunkTop = canvas.height - 20 - (canvas.height * 0.6);
        const maxTrunkTop = canvas.height - 20 - 50;
        const trunkY = Math.random() * (maxTrunkTop - minTrunkTop) + minTrunkTop;

        const rockColors = [currentTheme.rockColor1, currentTheme.rockColor2, currentTheme.groundDetailColor];
        const stackWidth = OBSTACLE_WIDTH * 0.8;
        let currentY = trunkY;
        const rocks = [];

        while (currentY < canvas.height - 20) { // Stop above the ground
            const rockHeight = Math.random() * 40 + 30; // Random height for each rock
            const rockWidth = stackWidth * (0.8 + Math.random() * 0.4); // Random width variation
            const offsetX = (OBSTACLE_WIDTH - rockWidth) / 2 + (Math.random() - 0.5) * 10; // Center with slight horizontal offset
            const color = rockColors[Math.floor(Math.random() * rockColors.length)];

            rocks.push({
                y: currentY,
                width: rockWidth,
                height: rockHeight,
                offsetX: offsetX,
                color: color
            });

            currentY += rockHeight * (0.8 + Math.random() * 0.2); // Move down, with some overlap
        }


        obstacles.push({
            x: canvas.width,
            y: trunkY, // Store the top Y for collision detection
            rocks: rocks // Store the generated rock properties
        });
    }

    // Move existing obstacles
    obstacles.forEach(obstacle => {
        obstacle.x -= speed;
    });

    // Remove obstacles that have moved off-screen
    obstacles = obstacles.filter(obstacle => obstacle.x + OBSTACLE_WIDTH > 0);
}

// Check for collisions
function checkCollisions() {
    // Collision with ground
    if (balloonY + BALLOON_RADIUS > canvas.height - 20) { // 20 is ground height
        return true;
    }

    // Collision with obstacles (only bottom part)
    const balloonX = canvas.width / 4;
    for (const obstacle of obstacles) {
        // Check horizontal overlap
        if (balloonX + BALLOON_RADIUS > obstacle.x && balloonX - BALLOON_RADIUS < obstacle.x + OBSTACLE_WIDTH) {
            // Check vertical overlap (hit the trunk)
            if (balloonY + BALLOON_RADIUS > obstacle.y) {
                return true;
            }
        }
    }

    return false;
}

// Main Game Loop
function gameLoop() {
    const difficulty = difficulties[currentDifficulty];
    const baseSpeed = difficulty.OBSTACLE_SPEED;

    // 1. Clear Canvas with theme sky color
    ctx.fillStyle = currentTheme.skyColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 2. Update Game Objects
    frameCount++;

    // Update parallax elements
    updateBackgroundElements(baseSpeed); // Use the new function

    // Update game elements
    updateClouds(difficulty.CLOUD_SPEED);
    updateBirds(difficulty.BIRD_SPEED);

    if (!isGameOver) {
        updateBalloon(difficulty.GRAVITY);
        updateObstacles(difficulty.OBSTACLE_SPEED, difficulty.OBSTACLE_SPAWN_RATE);

        if (checkCollisions()) {
            playSound(gameOverSound);
            triggerGameOver();
        }
    }

    // 3. Draw Game Objects
    // Draw background layers first
    drawMountainGroundAndHorizon(); // Draw ground and horizon
    drawLayer(backgroundElements); // Draw all background elements

    // Draw game elements
    drawClouds();
    drawBirds();
    drawObstacles();
    drawBalloon();

    // 4. Request Next Frame (unless game is over)
    if (!isGameOver) {
        animationFrameId = requestAnimationFrame(gameLoop);
    }
}