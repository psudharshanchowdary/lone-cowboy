# Lone Cowboy: Wild West Outlaws 🤠🌵

A Wild West cowboy action game with two complete experiences:
1. **3D Third-Person Web Game** (`web3d/`): Immersive 3D action shooter built in **Three.js & WebGL** with improved outlaw bot AI, full 3D frontier town, procedural Web Audio sound synthesis, and wave gauntlets. Playable in any browser!
2. **2D Pixel-Art Platformer & Shooter** (`main.py`): 52 levels across 5 outlaw gang territories built in **Python & Pygame**, culminating in the Level 52 Boss Gauntlet against El Diablo.

---

## 🌟 3D Web Game Features & Highlights (`web3d/`)

- **Instant Browser Play**: Zero installation needed! Powered by Three.js and WebGL.
- **Enhanced 3D Outlaw Bot AI**:
  - *No crashes*: Rock-solid null-safe updates.
  - *3D Line-of-sight Raycasting*: Outlaws only spot and shoot when view is not obstructed by buildings or crates.
  - *Obstacle Avoidance & Steering*: Bots navigate smoothly around porches and obstacles.
  - *Cover-Seeking*: Bots duck behind crates when under fire.
  - *Visual Aim Telegraphs*: Alert `!` warning markers, aiming stances, and red laser scopes for snipers giving you time to dodge!
  - *5 Bot Gang Archetypes*: Rattlesnake Gunners, Dust Devil Knife Brawlers, Iron Mask Rooftop Snipers, Black Powder Grenadiers, and Kingpin Boss **El Diablo**.
  - *Floating 3D Health Bars* & Defeat Ragdoll Collapse.
- **3D Western Frontier Town**: Two-story Saloon with balcony, Sheriff's Jail, Bank, Water Tower, spinning Windmill, Saguaro cacti, and interactive shootable **TNT Barrels** for chain-reaction explosions!
- **Procedural Web Audio Engine**: 100% procedural gunshots, cylinder reload clicks, bullet ricochets, sizzling dynamite fuses, and booming explosions generated via the Web Audio API.
- **Dynamic 3D HUD**: Health hearts, spinning 6-chamber revolver cylinder UI, 3D crosshair with hitmarkers, damage screen vignette, and real-time circular **Minimap Radar**!

### 🕹️ 3D Game Controls:

| Action | Controls |
| :--- | :--- |
| **Move** | `W`, `A`, `S`, `D` or Arrow keys |
| **Look / Aim** | Mouse (Pointer Lock) |
| **Sprint / Run** | Hold `Left Shift` |
| **Jump** | `Space` |
| **Crouch (Take Cover)** | `C` or `Ctrl` |
| **Shoot Revolver** | `Left Mouse Click` |
| **Reload Cylinder** | `R` key |
| **Throw Dynamite** | `Right Mouse Click` or `K` |
| **Melee Knife Slash** | `F` or `V` |

### 🚀 How to Launch 3D Game:
```bash
./run_3d.sh
```
*(Or open `web3d/index.html` in your browser / run `python3 -m http.server 8080`)*

---

## 🕹️ 2D Retro Pygame Version (`main.py`)

- 52 levels stored in external JSON files (`data/levels/`).
- 2D side-scrolling platformer with coyote time, jump buffering, crouch ducking, and platform drop-through (`S + Space`).
- Chapter boss gauntlet at Level 52.

### Launch 2D Game:
```bash
./run_game.sh
# Or: .venv/bin/python main.py
```

### Run 2D Automated Tests (Headless):
```bash
.venv/bin/python tests/test_game_engine.py
```

---

## 📁 Codebase Structure

```
cowboy_game/
├── index.html                  # Root entry point (redirects to web3d for GitHub Pages)
├── run_3d.sh                   # 1-Click launcher for 3D Web Game
├── run_game.sh                 # Launcher for 2D Pygame version
├── web3d/                      # Modern 3D Web Game (Three.js WebGL)
│   ├── index.html              # 3D canvas, HUD, crosshair, radar, menus
│   ├── css/
│   │   └── style.css           # Western retro HUD styling
│   └── js/
│       ├── config.js           # 3D camera settings, weapon stats, bot configs, waves
│       ├── audio.js            # Web Audio API procedural sound synthesizer
│       ├── particles.js        # 3D particle system (muzzle flash, smoke, sparks, fireballs)
│       ├── world.js            # 3D Western Town (Saloon, Sheriff, Bank, Water Tower, TNT)
│       ├── player.js           # 3D Cowboy model & third-person controller
│       ├── weapons.js          # 3D Revolver raycasting, bouncing dynamite, melee knife
│       ├── bots.js             # Enhanced 3D Outlaw Bot AI (5 archetypes, cover, aim telegraphs)
│       ├── ui.js               # HUD manager (hearts, cylinder ammo, minimap radar, banners)
│       └── main.js             # 3D Game loop & wave gauntlet manager
├── core/                       # 2D Game core engine
├── entities/                   # 2D Player & outlaw entities
├── weapons/                    # 2D Combat & projectiles
├── world/                      # 2D Tilemap & 52-level JSON generator/loader
├── data/levels/                # All 52 JSON level files
└── tests/                      # Automated test suite
```

---

## 🌐 Deploy to GitHub Pages

To make the 3D game playable online by anyone with a web link:
1. Go to your repository settings on GitHub: `https://github.com/psudharshanchowdary/lone-cowboy/settings/pages`.
2. Under **Build and deployment** -> **Branch**, select `main` and root `/` (or `/web3d`).
3. Click **Save**. Your game will be live online within seconds at `https://psudharshanchowdary.github.io/lone-cowboy/`!
