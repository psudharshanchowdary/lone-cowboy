/**
 * 3D Lone Cowboy: Procedural Web Audio Sound Synthesizer
 * Zero external audio files needed! Generates realistic western sound effects in real-time.
 */
class SoundEngine {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
        this.enabled = true;
    }

    init() {
        if (this.ctx) return;
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.setValueAtTime(0.7, this.ctx.currentTime);
        this.masterGain.connect(this.ctx.destination);
    }

    resume() {
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    // -------------------------------------------------------------
    // Revolver Gunshot (Crisp pop + explosive tail)
    // -------------------------------------------------------------
    playGunshot(isEnemy = false) {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;

        // 1. Initial mechanical transient snap
        const osc = this.ctx.createOscillator();
        const oscGain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(isEnemy ? 180 : 260, t);
        osc.frequency.exponentialRampToValueAtTime(30, t + 0.12);
        oscGain.gain.setValueAtTime(isEnemy ? 0.4 : 0.8, t);
        oscGain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
        osc.connect(oscGain);
        oscGain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.16);

        // 2. Gunpowder explosion burst (filtered white noise)
        const bufferSize = this.ctx.sampleRate * 0.4;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.08));
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2800, t);
        filter.frequency.exponentialRampToValueAtTime(250, t + 0.35);

        const noiseGain = this.ctx.createGain();
        noiseGain.gain.setValueAtTime(isEnemy ? 0.35 : 0.7, t);
        noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.35);

        noise.connect(filter);
        filter.connect(noiseGain);
        noiseGain.connect(this.masterGain);
        noise.start(t);
    }

    // -------------------------------------------------------------
    // Revolver Cylinder Click / Reload
    // -------------------------------------------------------------
    playReloadClick() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(950, t);
        osc.frequency.exponentialRampToValueAtTime(320, t + 0.04);

        gain.gain.setValueAtTime(0.3, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.04);

        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.05);
    }

    playDryFire() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(1400, t);
        gain.gain.setValueAtTime(0.2, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.03);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.04);
    }

    // -------------------------------------------------------------
    // Bullet Ricochet / Ping
    // -------------------------------------------------------------
    playRicochet() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(2200, t);
        osc.frequency.exponentialRampToValueAtTime(600, t + 0.25);

        gain.gain.setValueAtTime(0.25, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);

        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.26);
    }

    // -------------------------------------------------------------
    // Dynamite Fuse Sizzle & Explosion
    // -------------------------------------------------------------
    playFuseSizzle() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;

        const bufferSize = this.ctx.sampleRate * 0.06;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * 0.15;
        }
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.setValueAtTime(3500, t);
        noise.connect(filter);
        filter.connect(this.masterGain);
        noise.start(t);
    }

    playExplosion() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;

        // Sub bass thump
        const osc = this.ctx.createOscillator();
        const oscGain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(140, t);
        osc.frequency.exponentialRampToValueAtTime(25, t + 0.6);
        oscGain.gain.setValueAtTime(1.0, t);
        oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.7);
        osc.connect(oscGain);
        oscGain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.75);

        // Heavy blast noise
        const bufferSize = this.ctx.sampleRate * 0.9;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.25));
        }
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(900, t);
        filter.frequency.exponentialRampToValueAtTime(60, t + 0.8);
        const noiseGain = this.ctx.createGain();
        noiseGain.gain.setValueAtTime(1.0, t);
        noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.85);

        noise.connect(filter);
        filter.connect(noiseGain);
        noiseGain.connect(this.masterGain);
        noise.start(t);
    }

    // -------------------------------------------------------------
    // Melee Knife Slash & Punch
    // -------------------------------------------------------------
    playKnifeSlash() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, t);
        osc.frequency.exponentialRampToValueAtTime(120, t + 0.12);
        gain.gain.setValueAtTime(0.35, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.13);
    }

    // -------------------------------------------------------------
    // Impact, Damage & Victory Chimes
    // -------------------------------------------------------------
    playDamage() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(160, t);
        osc.frequency.exponentialRampToValueAtTime(60, t + 0.2);
        gain.gain.setValueAtTime(0.5, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.2);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 0.22);
    }

    playVictoryFanfare() {
        if (!this.ctx || !this.enabled) return;
        this.resume();
        const t = this.ctx.currentTime;
        const notes = [293.66, 369.99, 440.0, 587.33]; // D major trumpet chords
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, t + idx * 0.12);
            gain.gain.setValueAtTime(0.3, t + idx * 0.12);
            gain.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.12 + 0.4);
            osc.connect(gain);
            gain.connect(this.masterGain);
            osc.start(t + idx * 0.12);
            osc.stop(t + idx * 0.12 + 0.45);
        });
    }
}

export const audio = new SoundEngine();
