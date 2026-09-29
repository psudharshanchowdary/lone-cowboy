/**
 * 3D Lone Cowboy: Game Configuration & Tuning
 */
export const CONFIG = {
    // Canvas & Camera
    FOV: 65,
    NEAR: 0.1,
    FAR: 500,
    CAMERA_OFFSET: { x: 0.8, y: 1.8, z: 3.2 }, // Over-the-shoulder third-person
    CAMERA_LOOK_OFFSET: { x: 0.4, y: 1.5, z: -10 },
    CAMERA_LERP: 0.12,

    // Player Physics & Movement
    PLAYER_SPEED: 7.0,
    PLAYER_SPRINT_SPEED: 11.5,
    PLAYER_CROUCH_SPEED: 3.8,
    PLAYER_JUMP_FORCE: 9.0,
    GRAVITY: 24.0,
    PLAYER_MAX_HEALTH: 5,
    INVULNERABILITY_TIME: 1.2,

    // Weapons
    REVOLVER_CAPACITY: 6,
    REVOLVER_DAMAGE: 1,
    REVOLVER_FIRE_RATE: 0.22,      // seconds between shots
    REVOLVER_RELOAD_TIME: 1.1,     // seconds
    REVOLVER_RANGE: 120,

    DYNAMITE_COUNT: 3,
    DYNAMITE_DAMAGE: 4,
    DYNAMITE_RADIUS: 8.5,
    DYNAMITE_FUSE: 2.2,
    DYNAMITE_THROW_FORCE: 16.0,

    MELEE_DAMAGE: 2,
    MELEE_RANGE: 2.6,
    MELEE_COOLDOWN: 0.4,

    // Outlaw Bot AI Tuning
    BOTS: {
        GUNNER: {
            name: "Rattlesnake Gunner",
            hp: 2,
            speed: 3.6,
            sightRange: 35,
            attackRange: 22,
            attackDelay: 0.7,
            damage: 1,
            color: 0x4e703e // Green bandana
        },
        BRAWLER: {
            name: "Dust Devil Brawler",
            hp: 3,
            speed: 6.2,
            sightRange: 30,
            attackRange: 2.4,
            attackDelay: 0.5,
            damage: 1,
            color: 0x8a181c // Crimson headband
        },
        SNIPER: {
            name: "Iron Mask Sniper",
            hp: 2,
            speed: 2.2,
            sightRange: 55,
            attackRange: 45,
            attackDelay: 1.2,
            damage: 2,
            color: 0x707480 // Iron gray
        },
        GRENADIER: {
            name: "Black Powder Grenadier",
            hp: 3,
            speed: 3.2,
            sightRange: 38,
            attackRange: 26,
            attackDelay: 1.5,
            damage: 3,
            color: 0xc42c26 // Dynamite red
        },
        BOSS: {
            name: "El Diablo (Kingpin)",
            hp: 16,
            speed: 4.8,
            sightRange: 50,
            attackRange: 30,
            attackDelay: 0.6,
            damage: 1,
            color: 0x1a1a24 // Black coat & gold
        }
    },

    // Wave Progression
    WAVES: [
        {
            number: 1,
            title: "Wave 1: Rattlesnake Rustlers",
            description: "Gunners have surrounded the town street!",
            enemies: [
                { type: "GUNNER", x: -8, z: -25 },
                { type: "GUNNER", x: 12, z: -30 },
                { type: "GUNNER", x: 0, z: -40 }
            ]
        },
        {
            number: 2,
            title: "Wave 2: Dust Devil Syndicate",
            description: "Knife brawlers are sprinting between buildings!",
            enemies: [
                { type: "BRAWLER", x: -14, z: -20 },
                { type: "BRAWLER", x: 15, z: -22 },
                { type: "GUNNER", x: 2, z: -35 },
                { type: "GUNNER", x: -10, z: -45 }
            ]
        },
        {
            number: 3,
            title: "Wave 3: Iron Mask Outlaws",
            description: "Snipers on rooftops with red laser scopes!",
            enemies: [
                { type: "SNIPER", x: -12, y: 5.5, z: -25 }, // On saloon balcony
                { type: "SNIPER", x: 14, y: 5.5, z: -35 },  // On sheriff roof
                { type: "BRAWLER", x: 0, z: -20 },
                { type: "GUNNER", x: 8, z: -30 }
            ]
        },
        {
            number: 4,
            title: "Wave 4: Black Powder Marauders",
            description: "Grenadiers lobbing dynamite sticks over cover!",
            enemies: [
                { type: "GRENADIER", x: -15, z: -30 },
                { type: "GRENADIER", x: 15, z: -32 },
                { type: "SNIPER", x: 0, y: 5.5, z: -48 },
                { type: "BRAWLER", x: -6, z: -18 },
                { type: "GUNNER", x: 6, z: -22 }
            ]
        },
        {
            number: 5,
            title: "Wave 5: The Grand Showdown (El Diablo)",
            description: "The Kingpin of all gangs has stepped into the street!",
            enemies: [
                { type: "BOSS", x: 0, z: -45 },
                { type: "GUNNER", x: -12, z: -35 },
                { type: "BRAWLER", x: 12, z: -35 },
                { type: "GRENADIER", x: -8, z: -50 }
            ]
        }
    ]
};
