// This file contains game constants, difficulty settings, and theme definitions.

// --- Constants ---
const BALLOON_RADIUS = 30;
const OBSTACLE_WIDTH = 60;
const OBSTACLE_GAP = 280;
const CLOUD_SPAWN_RATE = 300;
const BIRD_SPAWN_RATE = 450;

// --- Balloon Properties ---
const balloonColor = '#FF69B4'; // Hot Pink

// --- Difficulty Settings ---
const difficulties = {
    easy: {
        GRAVITY: 0.08,
        LIFT: -3.5,
        OBSTACLE_SPEED: 1.8,
        OBSTACLE_SPAWN_RATE: 240,
        CLOUD_SPEED: 0.5,
        BIRD_SPEED: 1.5
    },
    normal: {
        GRAVITY: 0.1,
        LIFT: -4,
        OBSTACLE_SPEED: 2.2,
        OBSTACLE_SPAWN_RATE: 200,
        CLOUD_SPEED: 0.7,
        BIRD_SPEED: 1.8
    },
    hard: {
        GRAVITY: 0.12,
        LIFT: -4.5,
        OBSTACLE_SPEED: 2.6,
        OBSTACLE_SPAWN_RATE: 180,
        CLOUD_SPEED: 0.9,
        BIRD_SPEED: 2.1
    }
};

// --- Theme Definitions ---
const themes = {
    mountain: {
        name: 'Mountain',
        skyColor: '#87CEEB', // Sky blue
        groundColor: '#A0522D', // Sienna (medium brown)
        groundDetailColor: '#8B4513', // Saddle brown (darker detail)
        // Mountain/Rock Colors
        mountainColors: ['#8B4513', '#A0522D', '#CD853F', '#A9A9A9', '#808080', '#696969'], // Added grey mountain colors
        rockColor1: '#A9A9A9', // Dark gray
        rockColor2: '#808080', // Gray
        snowCapColor: '#FFFFFF', // White
        // Tree Colors
        treeColor1: '#228B22', // Forest green
        treeColor2: '#32CD32', // Lime green
        treeColor3: '#006400', // Dark green
        // Parallax layer colors (using new mountain colors)
        layer1Color: '#CD853F', // Distant mountains (Peru)
        layer2Color: '#A0522D', // Mid mountains (Sienna)
        layer3Color: '#8B4513', // Front mountains (Saddle brown)
        // Element types for each layer
        layer1Elements: ['distant-peak', 'rolling-hill'],
        layer2Elements: ['foothill', 'cliff', 'pine-tree'], // Add trees to layer 2
        layer3Elements: ['boulder', 'pine-tree', 'small-rock', 'pine-tree', 'boulder', 'small-rock'], // Add more trees and small rocks to layer 3
        drawObstacle: (obstacle) => {
            // Draw towering stacks of rocks/boulders using pre-generated properties
            obstacle.rocks.forEach(rock => {
                ctx.fillStyle = rock.color;
                // Using fillRect as a placeholder for a more complex shape
                ctx.fillRect(obstacle.x + rock.offsetX, rock.y, rock.width, rock.height);

                // Add thin dark grey outline
                ctx.strokeStyle = '#696969'; // Dim Gray
                ctx.lineWidth = 1;
                ctx.strokeRect(obstacle.x + rock.offsetX, rock.y, rock.width, rock.height);
            });
        }
    },
    city: {
        name: 'City',
        skyColor: '#4682B4', // Steel blue
        groundColor: '#808080', // Gray
        groundDetailColor: '#696969', // Dim gray
        obstacleColor: '#2F4F4F', // Dark slate gray
        obstacleDetailColor: '#1C2F2F', // Darker slate
        // Parallax layer colors
        layer1Color: '#2B4B6B', // Distant buildings (darker)
        layer2Color: '#3B5B7B', // Mid buildings
        layer3Color: '#4B6B8B', // Front buildings
        // Element types for each layer
        layer1Elements: ['skyscraper', 'tower'],
        layer2Elements: ['building', 'antenna'],
        layer3Elements: ['lamppost', 'fence'],
        drawObstacle: (obstacle) => {
            // Draw building
            ctx.fillStyle = themes.city.obstacleColor;
            ctx.fillRect(obstacle.x, obstacle.y, OBSTACLE_WIDTH, canvas.height - obstacle.y);

            // Add windows
            ctx.fillStyle = '#FFD700'; // Gold windows
            for(let i = 0; i < 4; i++) {
                for(let j = 0; j < 2; j++) {
                    ctx.fillRect(
                        obstacle.x + 10 + (j * 25),
                        obstacle.y + 20 + (i * 40),
                        15,
                        25
                    );
                }
            }
        }
    },
    beach: {
        name: 'Beach',
        skyColor: '#87CEEB', // Sky blue
        groundColor: '#F4A460', // Sandy brown
        groundDetailColor: '#DEB887', // Burlywood
        obstacleColor: '#228B22', // Forest green
        obstacleDetailColor: '#006400', // Dark green
        // Parallax layer colors
        layer1Color: '#ADD8E6', // Distant ocean/horizon
        layer2Color: '#87CEEB', // Mid waves
        layer3Color: '#E6C392', // Front sand features
        // Element types for each layer
        layer1Elements: ['horizon', 'island'],
        layer2Elements: ['wave', 'cloud-reflection'],
        layer3Elements: ['seashell', 'dune-grass'],
        drawObstacle: (obstacle) => {
            // Draw palm tree trunk
            ctx.fillStyle = '#8B4513'; // Saddle brown trunk
            ctx.fillRect(
                obstacle.x + OBSTACLE_WIDTH/3,
                obstacle.y,
                OBSTACLE_WIDTH/3,
                canvas.height - obstacle.y
            );

            // Draw palm leaves
            ctx.fillStyle = themes.beach.obstacleColor;
            for(let i = 0; i < 3; i++) {
                ctx.beginPath();
                ctx.moveTo(obstacle.x + OBSTACLE_WIDTH/2, obstacle.y);
                ctx.quadraticCurveTo(
                    obstacle.x + (i-1) * 30,
                    obstacle.y - 40,
                    obstacle.x + (i-1) * 60,
                    obstacle.y - 20
                );
                ctx.lineTo(obstacle.x + (i-1) * 60, obstacle.y);
                ctx.fill();
            }
        }
    }
};