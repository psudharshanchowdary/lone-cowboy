# Lone Cowboy: Wild West Outlaws 🤠🌵

A 2D Wild West retro pixel-art platformer and shooter built in Python with Pygame. Take on the role of a lone cowboy fighting through 52 levels across 5 notorious outlaw gang territories, culminating in an epic multi-phase boss gauntlet at Level 52!

---

## 🎯 Key Features & Specs

- **Fluid Platformer Movement**:
  - Walk, sprint (`Shift`), jump with coyote time & jump buffering, crouch (`S`/`Down`).
  - Drop down through wooden one-way platforms (`S + Space`).
- **Tactical Combat**:
  - **Revolver (Six-Shooter)**: 6 rounds, realistic cylinder reload with visual UI.
  - **Melee Bowie Knife**: Quick close-range slash for dispatching flanking bandits.
  - **Dynamite Throwable**: High-arc physics, wall bounces, fuse timer, and area-of-effect blast damage.
- **Dynamic Enemy AI**:
  - **Chapter 1 (Rattlesnake Rustlers)**: Grunt bandits armed with revolvers, ledge awareness, and aim telegraphs.
  - **Chapter 2 (Dust Devil Syndicate)**: Fast dual-knife melee brawlers who rush and leap at the cowboy.
  - **Chapter 3 (Iron Mask Outlaws)**: Rooftop snipers with visible red laser-aim telegraphs.
  - **Chapter 4 (Black Powder Marauders)**: Grenadiers lobbing dynamite sticks in parabolic arcs.
  - **Chapter 5 (Desperado Cartel & Level 52 Gauntlet)**: Elite squads leading up to the 5-wave gauntlet facing every gang leader and the ultimate kingpin: **El Diablo**!
- **Level Architecture (All 52 Levels in JSON)**:
  - 100% data-driven: all 52 levels are individual JSON files in `data/levels/level_01.json` ... `level_52.json`.
  - Easy to hand-edit or create custom levels.
- **Checkpoints**:
  - Warmly glowing lanterns act as checkpoints within levels, saving respawn positions.
- **Procedural Pixel Art Engine**:
  - Custom retro pixel art generated programmatically (Cowboy with Stetson/poncho, bandits, tiles, muzzle flashes, gunpowder smoke).
  - Built-in custom sprite loader: drop any custom PNG into `assets/sprites/` to swap art instantly!
- **Menus & UI**:
  - Main Menu, Chapter/Level Select (browsing all 52 levels), Controls guide, Pause menu, Game Over, and Victory screens.

---

## 🎮 Controls

| Action | Primary Key | Alternate / Mouse |
| :--- | :--- | :--- |
| **Move Left / Right** | `A` / `D` | `Left` / `Right` Arrow |
| **Sprint / Run** | `Left Shift` | `Right Shift` |
| **Jump** | `Space` | `W` / `Up` Arrow |
| **Crouch / Duck** | `S` | `Down` Arrow |
| **Drop Through Platform** | `S + Space` | `Down + Space` |
| **Shoot Revolver** | `J` or `Z` | `Left Mouse Click` |
| **Reload Cylinder** | `R` | (Auto reloads when empty) |
| **Melee Knife Slash** | `F` or `V` or `X` | `Middle Mouse Click` |
| **Throw Dynamite** | `K` or `C` | `Right Mouse Click` |
| **Pause Game** | `Escape` | `P` |

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Pygame 2.5+

A virtual environment is already prepared in the project folder with Pygame installed.

### 2. Run the Game
From the project folder, execute:

```bash
# Using the project's virtual environment:
.venv/bin/python main.py

# Or using your system python (if pygame is installed globally):
python3 main.py
```

Or run the convenient launcher:
```bash
./run_game.sh
```

### 3. Run Automated Tests (Headless)
To run the automated test suite without opening a display window:

```bash
.venv/bin/python tests/test_game_engine.py
```

---

## 🗺️ Chapter & Level Progression

| Chapter | Gang | Theme & Hazard | Signature Outlaw | Chapter Boss | Levels |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Rattlesnake Rustlers** | Dusty Canyons & Cacti | Revolver Grunt | Rattlesnake Jake | Levels 1–10 |
| **2** | **Dust Devil Syndicate** | Abandoned Mines & Spikes | Knife Brawler | Iron Bull Logan | Levels 11–20 |
| **3** | **Iron Mask Outlaws** | Saloon Rooftops & Chasms | Laser Sniper | One-Eyed Silas | Levels 21–30 |
| **4** | **Black Powder Marauders** | Dynamite Caverns & Fire | Grenadier | Mad Pete 'Kaboom' | Levels 31–40 |
| **5** | **The Desperado Cartel** | Fortress & Hacienda | Mixed Vanguard | **Level 52: Boss Gauntlet + El Diablo** | Levels 41–52 |

---

## 🛠️ Codebase Structure

```
cowboy_game/
├── main.py                     # Entry point & 60 FPS game loop
├── config.py                   # Constants (screen resolution, physics, controls, gang data)
├── requirements.txt            # Dependency list (pygame>=2.5.0)
├── run_game.sh                 # Convenience shell launcher
├── core/
│   ├── game.py                 # Game state manager, scene transitions, gauntlet logic
│   ├── camera.py               # Smooth lerp camera with deadzone and level clamping
│   └── input_handler.py        # Centralized event & input polling
├── entities/
│   ├── entity.py               # Physics entity (sub-pixel AABB, gravity, knockback, flash)
│   ├── player.py               # Lone Cowboy character mechanics
│   └── enemies/
│       ├── enemy_base.py       # Patrol, line-of-sight raycasting, state machine
│       ├── bandit.py           # Chapter 1 Revolver grunt
│       ├── brawler.py          # Chapter 2 Melee rusher
│       ├── sniper.py           # Chapter 3 Laser-sight sniper
│       ├── grenadier.py        # Chapter 4 Dynamite thrower
│       └── boss.py             # Chapter bosses & multi-phase boss mechanics
├── weapons/
│   ├── weapon.py               # Revolver, Dynamite, and Melee knife systems
│   └── projectile.py           # Bullets, bouncing dynamite, and melee hitboxes
├── world/
│   ├── tilemap.py              # Grid tilemap, solid blocks, one-way ledges, hazards
│   ├── level_loader.py         # JSON level parser and entity spawner
│   └── level_generator.py      # Procedural generator & validator for all 52 levels
├── ui/
│   ├── hud.py                  # Hearts, 6-round cylinder indicator, dynamite counter
│   ├── menu.py                 # Main menu, 52-level select browser, pause, victory
│   └── font_manager.py         # Retro font rendering with drop shadows
├── gfx/
│   ├── sprites.py              # Procedural pixel art generator & custom PNG loader
│   └── particles.py            # Gunpowder smoke, sparks, bullet hits, explosions
├── data/
│   ├── levels/                 # JSON files: level_01.json ... level_52.json
│   └── saves/                  # Progress save data (unlocked levels)
└── tests/
    └── test_game_engine.py     # 10 headless automated integration tests
```

---

## 🎨 How to Swap in Custom Pixel Art

The game works out of the box with procedural pixel art, but you can drop custom `.png` files into `assets/sprites/` anytime:
- `player_idle_r_0.png`, `player_walk_r_0.png`, etc.
- `enemy_bandit_patrol_r_0.png`, `enemy_sniper_patrol_r_0.png`, etc.
- `tile_sandstone.png`, `tile_wood.png`, `tile_platform.png`, etc.

The engine will automatically detect and load your custom image files!

---

## ✏️ How to Edit Levels

Open any level file in `data/levels/level_XX.json`:
- `width` / `height`: Grid dimensions (in 16px tiles).
- `tiles`: 2D matrix where:
  - `0`: Air / Empty
  - `1`: Sandstone block
  - `2`: Wood saloon block
  - `3`: Wooden one-way platform
  - `4`: Cactus hazard
  - `5`: Mine spikes hazard
  - `6`: Checkpoint lantern
  - `7`: Exit door
- `enemies`: List of `{"type": "bandit"|"brawler"|"sniper"|"grenadier", "x": px, "y": px}`
- `boss`: `{"name": "Boss Name", "x": px, "y": px, "health": hp}`
