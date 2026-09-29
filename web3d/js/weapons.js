/**
 * 3D Lone Cowboy: Weapons & Projectiles
 * Revolver with raycasting & bullet tracers, 3D bouncing dynamite, and melee knife.
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';
import { CONFIG } from './config.js';
import { audio } from './audio.js';

export class WeaponManager {
    constructor(scene, particles) {
        this.scene = scene;
        this.particles = particles;

        // Revolver State
        this.ammo = CONFIG.REVOLVER_CAPACITY;
        this.capacity = CONFIG.REVOLVER_CAPACITY;
        this.fireCooldown = 0.0;
        this.isReloading = false;
        this.reloadTimer = 0.0;

        // Dynamite State
        this.dynamiteCount = CONFIG.DYNAMITE_COUNT;
        this.activeDynamites = [];

        // Melee State
        this.meleeCooldown = 0.0;

        // Visual Bullet Tracers
        this.tracers = [];

        // Raycaster for shooting
        this.raycaster = new THREE.Raycaster();
    }

    update(dt, world, bots, player) {
        // Timers
        if (this.fireCooldown > 0) this.fireCooldown -= dt;
        if (this.meleeCooldown > 0) this.meleeCooldown -= dt;

        // Reload update
        if (this.isReloading) {
            this.reloadTimer -= dt;
            if (this.reloadTimer <= 0) {
                this.ammo = this.capacity;
                this.isReloading = false;
                audio.playReloadClick();
            }
        }

        // Update 3D Dynamite Projectiles
        for (let i = this.activeDynamites.length - 1; i >= 0; i--) {
            const d = this.activeDynamites[i];
            d.fuse -= dt;

            // Fuse sizzle sound
            if (Math.random() < 0.25) audio.playFuseSizzle();

            if (d.fuse <= 0) {
                this.explodeDynamite(d, world, bots, player);
                this.scene.remove(d.mesh);
                this.activeDynamites.splice(i, 1);
                continue;
            }

            // Gravity & velocity
            d.vel.y -= CONFIG.GRAVITY * dt;
            d.pos.addScaledVector(d.vel, dt);
            d.mesh.position.copy(d.pos);
            d.mesh.rotation.x += dt * 8.0;
            d.mesh.rotation.y += dt * 4.0;

            // Ground Bounce
            if (d.pos.y <= 0.2) {
                d.pos.y = 0.2;
                d.vel.y = -d.vel.y * 0.45;
                d.vel.x *= 0.75;
                d.vel.z *= 0.75;
            }

            // Collider bounces
            const dBox = new THREE.Box3().setFromCenterAndSize(d.pos, new THREE.Vector3(0.4, 0.4, 0.4));
            for (const col of world.colliders) {
                if (dBox.intersectsBox(col)) {
                    d.vel.x = -d.vel.x * 0.5;
                    d.vel.z = -d.vel.z * 0.5;
                    d.pos.addScaledVector(d.vel, dt * 2.0);
                }
            }
        }

        // Update Visual Bullet Tracers
        for (let i = this.tracers.length - 1; i >= 0; i--) {
            const tr = this.tracers[i];
            tr.age += dt;
            if (tr.age >= tr.lifetime) {
                this.scene.remove(tr.line);
                tr.line.geometry.dispose();
                this.tracers.splice(i, 1);
            }
        }
    }

    // -------------------------------------------------------------
    // Revolver Shoot
    // -------------------------------------------------------------
    shoot(player, world, bots) {
        if (this.isReloading || this.fireCooldown > 0) return false;

        if (this.ammo <= 0) {
            audio.playDryFire();
            this.startReload();
            return false;
        }

        this.ammo--;
        this.fireCooldown = CONFIG.REVOLVER_FIRE_RATE;
        audio.playGunshot(false);
        player.triggerRecoil();

        const muzzlePos = player.getMuzzlePosition();
        const aimDir = player.getAimDirection();

        // Emit muzzle flash and smoke
        this.particles.emitMuzzleFlash(muzzlePos, aimDir);

        // Raycast from camera center into world
        this.raycaster.set(player.camera.position, aimDir);

        // Check shootable targets: bots, TNT barrels, and world colliders
        let hitPoint = muzzlePos.clone().addScaledVector(aimDir, CONFIG.REVOLVER_RANGE);
        let hitTarget = null;
        let minDist = CONFIG.REVOLVER_RANGE;

        // 1. Check Bots
        for (const bot of bots) {
            if (!bot.alive) continue;
            const botBox = bot.getBoundingBox();
            const intersects = this.raycaster.ray.intersectsBox(botBox);
            if (intersects) {
                const dist = player.camera.position.distanceTo(bot.pos);
                if (dist < minDist) {
                    minDist = dist;
                    hitTarget = { type: 'bot', obj: bot };
                    hitPoint = this.raycaster.ray.intersectBox(botBox, new THREE.Vector3());
                }
            }
        }

        // 2. Check TNT Barrels
        for (const barrel of world.tntBarrels) {
            if (!barrel.alive) continue;
            const bBox = new THREE.Box3().setFromCenterAndSize(barrel.pos, new THREE.Vector3(1.0, 1.4, 1.0));
            if (this.raycaster.ray.intersectsBox(bBox)) {
                const dist = player.camera.position.distanceTo(barrel.pos);
                if (dist < minDist) {
                    minDist = dist;
                    hitTarget = { type: 'tnt', obj: barrel };
                    hitPoint = this.raycaster.ray.intersectBox(bBox, new THREE.Vector3());
                }
            }
        }

        // 3. Check World Colliders (Walls/Crates)
        for (const col of world.colliders) {
            if (this.raycaster.ray.intersectsBox(col)) {
                const dist = player.camera.position.distanceTo(col.getCenter(new THREE.Vector3()));
                if (dist < minDist) {
                    minDist = dist;
                    hitTarget = { type: 'world', obj: col };
                    hitPoint = this.raycaster.ray.intersectBox(col, new THREE.Vector3());
                }
            }
        }

        // Apply Hit Effects
        if (hitTarget) {
            if (hitTarget.type === 'bot') {
                hitTarget.obj.takeDamage(CONFIG.REVOLVER_DAMAGE, aimDir);
                this.particles.emitImpact(hitPoint, true);
            } else if (hitTarget.type === 'tnt') {
                this.detonateTNT(hitTarget.obj, world, bots, player);
            } else {
                audio.playRicochet();
                this.particles.emitImpact(hitPoint, false);
            }
        }

        // Spawn Visual Bullet Tracer Line
        this.spawnTracer(muzzlePos, hitPoint);
        return true;
    }

    spawnTracer(start, end) {
        const mat = new THREE.LineBasicMaterial({ color: 0xffe680, linewidth: 2, transparent: true, opacity: 0.85 });
        const geo = new THREE.BufferGeometry().setFromPoints([start, end]);
        const line = new THREE.Line(geo, mat);
        this.scene.add(line);
        this.tracers.push({ line, age: 0, lifetime: 0.08 });
    }

    startReload() {
        if (this.ammo < this.capacity && !this.isReloading) {
            this.isReloading = true;
            this.reloadTimer = CONFIG.REVOLVER_RELOAD_TIME;
            audio.playReloadClick();
        }
    }

    // -------------------------------------------------------------
    // Dynamite Throwing
    // -------------------------------------------------------------
    throwDynamite(player) {
        if (this.dynamiteCount <= 0) return false;

        this.dynamiteCount--;
        const spawnPos = player.getMuzzlePosition();
        const aimDir = player.getAimDirection();

        // 3D Dynamite Mesh
        const dGroup = new THREE.Group();
        const cyl = new THREE.Mesh(
            new THREE.CylinderGeometry(0.08, 0.08, 0.45, 8),
            new THREE.MeshLambertMaterial({ color: 0xc42820 })
        );
        dGroup.add(cyl);

        // Fuse spark
        const fuse = new THREE.Mesh(
            new THREE.BoxGeometry(0.04, 0.04, 0.04),
            new THREE.MeshBasicMaterial({ color: 0xffd700 })
        );
        fuse.position.y = 0.25;
        dGroup.add(fuse);

        dGroup.position.copy(spawnPos);
        this.scene.add(dGroup);

        const throwVel = aimDir.clone().multiplyScalar(CONFIG.DYNAMITE_THROW_FORCE);
        throwVel.y += 4.5; // arc lob

        this.activeDynamites.push({
            mesh: dGroup,
            pos: spawnPos.clone(),
            vel: throwVel,
            fuse: CONFIG.DYNAMITE_FUSE,
            damage: CONFIG.DYNAMITE_DAMAGE,
            radius: CONFIG.DYNAMITE_RADIUS
        });

        return true;
    }

    explodeDynamite(d, world, bots, player) {
        audio.playExplosion();
        this.particles.emitExplosion(d.pos, d.radius);

        // Damage Player
        const distToPlayer = d.pos.distanceTo(player.pos);
        if (distToPlayer <= d.radius) {
            const kb = player.pos.clone().sub(d.pos).normalize();
            player.takeDamage(d.damage, kb);
        }

        // Damage Bots
        for (const bot of bots) {
            if (!bot.alive) continue;
            const dist = d.pos.distanceTo(bot.pos);
            if (dist <= d.radius) {
                const kb = bot.pos.clone().sub(d.pos).normalize();
                bot.takeDamage(d.damage, kb);
            }
        }

        // Detonate nearby TNT Barrels (Chain Reaction!)
        for (const barrel of world.tntBarrels) {
            if (barrel.alive && d.pos.distanceTo(barrel.pos) <= d.radius) {
                this.detonateTNT(barrel, world, bots, player);
            }
        }
    }

    detonateTNT(barrel, world, bots, player) {
        if (!barrel.alive) return;
        barrel.alive = false;
        this.scene.remove(barrel.mesh);
        audio.playExplosion();
        this.particles.emitExplosion(barrel.pos, barrel.radius);

        // Player damage
        if (barrel.pos.distanceTo(player.pos) <= barrel.radius) {
            const kb = player.pos.clone().sub(barrel.pos).normalize();
            player.takeDamage(barrel.damage, kb);
        }

        // Bots damage
        for (const bot of bots) {
            if (!bot.alive) continue;
            if (barrel.pos.distanceTo(bot.pos) <= barrel.radius) {
                const kb = bot.pos.clone().sub(barrel.pos).normalize();
                bot.takeDamage(barrel.damage, kb);
            }
        }
    }

    // -------------------------------------------------------------
    // Melee Knife Slash
    // -------------------------------------------------------------
    meleeStrike(player, bots) {
        if (this.meleeCooldown > 0) return false;
        this.meleeCooldown = CONFIG.MELEE_COOLDOWN;
        audio.playKnifeSlash();

        const forward = player.getAimDirection();
        const strikePos = player.pos.clone().addScaledVector(forward, 1.2);

        for (const bot of bots) {
            if (!bot.alive) continue;
            const dist = strikePos.distanceTo(bot.pos);
            if (dist <= CONFIG.MELEE_RANGE) {
                bot.takeDamage(CONFIG.MELEE_DAMAGE, forward);
                this.particles.emitImpact(bot.pos.clone().add(new THREE.Vector3(0, 1.2, 0)), true);
            }
        }
        return true;
    }
}
