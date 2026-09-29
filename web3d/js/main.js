/**
 * 3D Lone Cowboy: Main Game Loop & Wave Gauntlet Manager
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';
import { CONFIG } from './config.js';
import { audio } from './audio.js';
import { World } from './world.js';
import { Player } from './player.js';
import { WeaponManager } from './weapons.js';
import { ParticleSystem } from './particles.js';
import { OutlawBot } from './bots.js';
import { UIManager } from './ui.js';

class Game {
    constructor() {
        this.container = document.getElementById('game-container');
        this.canvas = document.getElementById('webgl-canvas');

        // Three.js Core
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(CONFIG.FOV, window.innerWidth / window.innerHeight, CONFIG.NEAR, CONFIG.FAR);
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Subsystems
        this.particles = new ParticleSystem(this.scene);
        this.world = new World(this.scene);
        this.player = new Player(this.scene, this.camera);
        this.weapons = new WeaponManager(this.scene, this.particles);
        this.ui = new UIManager();

        // Wave Management
        this.currentWaveIndex = 0;
        this.bots = [];
        this.gameState = 'MENU'; // 'MENU', 'PLAYING', 'WAVE_TRANSITION', 'GAME_OVER', 'VICTORY'
        this.waveTransitionTimer = 0;

        // Input state
        this.input = {
            moveX: 0,
            moveZ: 0,
            jump: false,
            crouch: false,
            sprint: false,
            mouseDeltaX: 0,
            mouseDeltaY: 0
        };

        this.lastTime = performance.now();
        this.isPointerLocked = false;

        this.init();
    }

    init() {
        this.world.build();
        this.setupEventListeners();
        this.showStartMenu();
        this.animate();
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());

        // Keyboard inputs
        window.addEventListener('keydown', (e) => this.onKeyDown(e));
        window.addEventListener('keyup', (e) => this.onKeyUp(e));

        // Pointer Lock & Mouse Look
        this.container.addEventListener('click', () => {
            if (this.gameState === 'PLAYING' && !this.isPointerLocked) {
                this.container.requestPointerLock();
                audio.init();
            }
        });

        document.addEventListener('pointerlockchange', () => {
            this.isPointerLocked = (document.pointerLockElement === this.container);
        });

        document.addEventListener('mousemove', (e) => {
            if (this.isPointerLocked) {
                this.input.mouseDeltaX = e.movementX;
                this.input.mouseDeltaY = e.movementY;
            }
        });

        // Mouse buttons for shooting & dynamite
        window.addEventListener('mousedown', (e) => {
            if (this.gameState !== 'PLAYING') return;
            audio.init();

            if (e.button === 0) { // Left Click = Shoot Revolver
                const hit = this.weapons.shoot(this.player, this.world, this.bots);
                if (hit) this.ui.triggerHitmarker();
            } else if (e.button === 2) { // Right Click = Throw Dynamite
                this.weapons.throwDynamite(this.player);
            }
        });

        window.addEventListener('contextmenu', (e) => e.preventDefault());

        // UI Menu Buttons
        document.getElementById('start-btn').addEventListener('click', () => {
            audio.init();
            this.startGame();
            this.container.requestPointerLock();
        });

        document.getElementById('retry-btn').addEventListener('click', () => {
            audio.init();
            this.restartCurrentWave();
            this.container.requestPointerLock();
        });

        document.getElementById('victory-btn').addEventListener('click', () => {
            audio.init();
            this.currentWaveIndex = 0;
            this.startGame();
            this.container.requestPointerLock();
        });
    }

    onKeyDown(e) {
        if (e.code === 'KeyW' || e.code === 'ArrowUp') this.input.moveZ = -1;
        if (e.code === 'KeyS' || e.code === 'ArrowDown') this.input.moveZ = 1;
        if (e.code === 'KeyA' || e.code === 'ArrowLeft') this.input.moveX = -1;
        if (e.code === 'KeyD' || e.code === 'ArrowRight') this.input.moveX = 1;

        if (e.code === 'Space') this.input.jump = true;
        if (e.code === 'KeyC' || e.code === 'ControlLeft') this.input.crouch = true;
        if (e.code === 'ShiftLeft' || e.code === 'ShiftRight') this.input.sprint = true;

        if (e.code === 'KeyR') this.weapons.startReload();
        if (e.code === 'KeyF' || e.code === 'KeyV') this.weapons.meleeStrike(this.player, this.bots);
        if (e.code === 'KeyK') this.weapons.throwDynamite(this.player);
    }

    onKeyUp(e) {
        if (e.code === 'KeyW' || e.code === 'ArrowUp') if (this.input.moveZ < 0) this.input.moveZ = 0;
        if (e.code === 'KeyS' || e.code === 'ArrowDown') if (this.input.moveZ > 0) this.input.moveZ = 0;
        if (e.code === 'KeyA' || e.code === 'ArrowLeft') if (this.input.moveX < 0) this.input.moveX = 0;
        if (e.code === 'KeyD' || e.code === 'ArrowRight') if (this.input.moveX > 0) this.input.moveX = 0;

        if (e.code === 'Space') this.input.jump = false;
        if (e.code === 'KeyC' || e.code === 'ControlLeft') this.input.crouch = false;
        if (e.code === 'ShiftLeft' || e.code === 'ShiftRight') this.input.sprint = false;
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    showStartMenu() {
        this.gameState = 'MENU';
        document.getElementById('start-screen').style.display = 'flex';
        document.getElementById('game-over-screen').style.display = 'none';
        document.getElementById('victory-screen').style.display = 'none';
    }

    startGame() {
        document.getElementById('start-screen').style.display = 'none';
        document.getElementById('game-over-screen').style.display = 'none';
        document.getElementById('victory-screen').style.display = 'none';
        this.loadWave(this.currentWaveIndex);
    }

    restartCurrentWave() {
        document.getElementById('game-over-screen').style.display = 'none';
        this.player.hp = this.player.maxHp;
        this.player.alive = true;
        this.player.pos.set(0, 0, 10);
        this.weapons.ammo = this.weapons.capacity;
        this.weapons.dynamiteCount = CONFIG.DYNAMITE_COUNT;
        this.loadWave(this.currentWaveIndex);
    }

    loadWave(waveIdx) {
        this.currentWaveIndex = waveIdx;
        const waveData = CONFIG.WAVES[this.currentWaveIndex];

        // Clear existing bots
        this.bots.forEach(b => b.dispose());
        this.bots = [];

        // Spawn Wave Bots
        waveData.enemies.forEach(e => {
            const bot = new OutlawBot(this.scene, e.type, e.x, e.y || 0, e.z, this.particles);
            this.bots.push(bot);
        });

        // Banner Announcement
        this.ui.showBanner(waveData.title, waveData.description, 3.2);

        this.gameState = 'PLAYING';
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const now = performance.now();
        const dt = Math.min(0.06, (now - this.lastTime) / 1000.0);
        this.lastTime = now;

        this.update(dt);
        this.renderer.render(this.scene, this.camera);

        // Reset per-frame mouse deltas
        this.input.mouseDeltaX = 0;
        this.input.mouseDeltaY = 0;
    }

    update(dt) {
        // World & Particle animation
        this.world.update(dt);
        this.particles.update(dt);

        if (this.gameState === 'PLAYING' || this.gameState === 'WAVE_TRANSITION') {
            // Update Player
            const prevHp = this.player.hp;
            this.player.update(dt, this.input, this.world);
            if (this.player.hp < prevHp) {
                this.ui.triggerDamageFlash();
            }

            // Check Player Death
            if (!this.player.alive) {
                this.gameState = 'GAME_OVER';
                document.exitPointerLock();
                document.getElementById('game-over-screen').style.display = 'flex';
                return;
            }

            // Update Weapons & Projectiles
            this.weapons.update(dt, this.world, this.bots, this.player);

            // Update Bots AI
            for (const bot of this.bots) {
                bot.update(dt, this.player, this.world, this.weapons);
            }

            // Check Wave Completion
            const livingBots = this.bots.filter(b => b.alive).length;
            if (livingBots === 0 && this.gameState === 'PLAYING') {
                this.gameState = 'WAVE_TRANSITION';
                this.waveTransitionTimer = 3.0;
                audio.playVictoryFanfare();

                if (this.currentWaveIndex < CONFIG.WAVES.length - 1) {
                    this.ui.showBanner("WAVE CLEARED!", "Next gang incoming...", 2.8);
                } else {
                    // Final Boss Defeated!
                    this.gameState = 'VICTORY';
                    document.exitPointerLock();
                    document.getElementById('victory-screen').style.display = 'flex';
                    return;
                }
            }

            // Handle transition to next wave
            if (this.gameState === 'WAVE_TRANSITION') {
                this.waveTransitionTimer -= dt;
                if (this.waveTransitionTimer <= 0) {
                    this.loadWave(this.currentWaveIndex + 1);
                }
            }

            // Update HUD
            this.ui.update(dt, this.player, this.weapons, this.bots, CONFIG.WAVES[this.currentWaveIndex]);
        }
    }
}

// Launch on page load
window.addEventListener('DOMContentLoaded', () => {
    new Game();
});
