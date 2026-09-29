/**
 * 3D Lone Cowboy: HUD, UI Overlays, and Minimap Radar
 */
export class UIManager {
    constructor() {
        this.heartsContainer = document.getElementById('hearts');
        this.waveTitleEl = document.getElementById('wave-title');
        this.outlawsCountEl = document.getElementById('outlaws-count');
        this.ammoTextEl = document.getElementById('ammo-text');
        this.reloadPromptEl = document.getElementById('reload-prompt');
        this.dynamiteCountEl = document.getElementById('dynamite-count');
        this.hitmarkerEl = document.getElementById('hitmarker');
        this.damageFlashEl = document.getElementById('damage-flash');
        this.bannerEl = document.getElementById('banner');

        // Cylinder 2D Canvas
        this.cylCanvas = document.getElementById('cylinder-canvas');
        this.cylCtx = this.cylCanvas.getContext('2d');

        // Minimap 2D Canvas
        this.mapCanvas = document.getElementById('minimap');
        this.mapCtx = this.mapCanvas.getContext('2d');

        this.bannerTimer = 0.0;
        this.hitmarkerTimer = 0.0;
    }

    triggerHitmarker() {
        this.hitmarkerEl.style.opacity = '1.0';
        this.hitmarkerTimer = 0.12;
    }

    triggerDamageFlash() {
        this.damageFlashEl.style.opacity = '0.85';
        setTimeout(() => {
            this.damageFlashEl.style.opacity = '0';
        }, 180);
    }

    showBanner(title, subtitle = '', duration = 2.5) {
        this.bannerEl.innerHTML = `${title}<div style="font-size:22px;color:#eedcc0;margin-top:6px;">${subtitle}</div>`;
        this.bannerEl.style.opacity = '1.0';
        this.bannerTimer = duration;
    }

    update(dt, player, weaponManager, bots, currentWave) {
        // Timers
        if (this.hitmarkerTimer > 0) {
            this.hitmarkerTimer -= dt;
            if (this.hitmarkerTimer <= 0) this.hitmarkerEl.style.opacity = '0';
        }

        if (this.bannerTimer > 0) {
            this.bannerTimer -= dt;
            if (this.bannerTimer <= 0) this.bannerEl.style.opacity = '0';
        }

        // 1. Update Hearts
        this.heartsContainer.innerHTML = '';
        for (let i = 0; i < player.maxHp; i++) {
            const heart = document.createElement('div');
            heart.className = `heart ${i < player.hp ? '' : 'depleted'}`;
            this.heartsContainer.appendChild(heart);
        }

        // 2. Wave & Outlaws Counter
        const livingBots = bots.filter(b => b.alive).length;
        this.waveTitleEl.textContent = currentWave.title;
        this.outlawsCountEl.textContent = `OUTLAWS REMAINING: ${livingBots}`;

        // 3. Ammo & Cylinder
        this.ammoTextEl.textContent = `${weaponManager.ammo} / ${weaponManager.capacity}`;
        if (weaponManager.isReloading) {
            const pct = Math.floor((1.0 - weaponManager.reloadTimer / 1.1) * 100);
            this.reloadPromptEl.textContent = `RELOADING... ${pct}%`;
            this.reloadPromptEl.className = 'reload-prompt reloading';
        } else {
            this.reloadPromptEl.textContent = `[R] TO RELOAD`;
            this.reloadPromptEl.className = 'reload-prompt';
        }

        this.dynamiteCountEl.innerHTML = `🧨 x${weaponManager.dynamiteCount} [RMB/K]`;

        // Draw Cylinder
        this.drawCylinder(weaponManager.ammo, weaponManager.isReloading);

        // 4. Draw Minimap Radar
        this.drawMinimap(player, bots);
    }

    drawCylinder(ammo, isReloading) {
        const ctx = this.cylCtx;
        const w = this.cylCanvas.width;
        const h = this.cylCanvas.height;
        const cx = w / 2;
        const cy = h / 2;

        ctx.clearRect(0, 0, w, h);

        // Cylinder base metal disk
        ctx.fillStyle = '#2a2826';
        ctx.beginPath();
        ctx.arc(cx, cy, 26, 0, Math.PI * 2);
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#825434';
        ctx.stroke();

        // Center hub
        ctx.fillStyle = '#100c0a';
        ctx.beginPath();
        ctx.arc(cx, cy, 7, 0, Math.PI * 2);
        ctx.fill();

        // 6 Chambers
        const rot = isReloading ? Date.now() * 0.015 : 0;
        for (let i = 0; i < 6; i++) {
            const angle = i * (Math.PI * 2 / 6) + rot;
            const x = cx + Math.cos(angle) * 16;
            const y = cy + Math.sin(angle) * 16;

            ctx.fillStyle = (i < ammo) ? '#ffd700' : '#141210';
            ctx.beginPath();
            ctx.arc(x, y, 4.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#8a6e36';
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }

    drawMinimap(player, bots) {
        const ctx = this.mapCtx;
        const w = this.mapCanvas.width;
        const h = this.mapCanvas.height;
        const cx = w / 2;
        const cy = h / 2;
        const scale = 1.3; // radar range scale

        ctx.clearRect(0, 0, w, h);

        // Radar grid circles
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.25)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(cx, cy, 30, 0, Math.PI * 2);
        ctx.arc(cx, cy, 55, 0, Math.PI * 2);
        ctx.stroke();

        // Living Bots (Red blips, Boss is larger Gold/Red)
        for (const bot of bots) {
            if (!bot.alive) continue;
            const dx = (bot.pos.x - player.pos.x) * scale;
            const dz = (bot.pos.z - player.pos.z) * scale;

            const mapX = cx + dx;
            const mapY = cy + dz;

            // Check if inside circular radar bounds
            const distSq = (mapX - cx) * (mapX - cx) + (mapY - cy) * (mapY - cy);
            if (distSq < (w / 2 - 4) * (w / 2 - 4)) {
                ctx.fillStyle = (bot.type === 'BOSS') ? '#ffdd00' : '#ff3333';
                ctx.beginPath();
                ctx.arc(mapX, mapY, bot.type === 'BOSS' ? 5 : 3.5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Cowboy Player (Gold Arrow facing yaw direction)
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(-player.yaw);

        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(0, -7);
        ctx.lineTo(5, 5);
        ctx.lineTo(0, 2);
        ctx.lineTo(-5, 5);
        ctx.closePath();
        ctx.fill();

        ctx.restore();
    }
}
