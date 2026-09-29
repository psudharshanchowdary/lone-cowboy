/**
 * 3D Lone Cowboy: Enhanced Outlaw Bot AI
 * 5 Bot Classes (Gunner, Brawler, Sniper, Grenadier, Boss),
 * 3D line-of-sight raycasting, obstacle avoidance, visual aim telegraphs,
 * cover seeking, floating 3D health bars, and defeat ragdoll collapse.
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';
import { CONFIG } from './config.js';
import { audio } from './audio.js';

export class OutlawBot {
    constructor(scene, type, x, y, z, particles) {
        this.scene = scene;
        this.type = type;
        this.particles = particles;
        this.cfg = CONFIG.BOTS[type];

        this.pos = new THREE.Vector3(x, y, z);
        this.vel = new THREE.Vector3(0, 0, 0);
        this.yaw = Math.random() * Math.PI * 2;

        this.maxHp = this.cfg.hp;
        this.hp = this.maxHp;
        this.alive = true;
        this.speed = this.cfg.speed;

        // AI States: PATROL, ALERT, CHASE, AIMING, ATTACKING, COVER, STAGGER
        this.state = 'PATROL';
        this.stateTimer = Math.random() * 2.0;
        this.aimTimer = 0.0;
        this.attackCooldown = 1.0;
        this.staggerTimer = 0.0;
        this.flashTimer = 0.0;

        // Laser pointer for sniper
        this.laserLine = null;

        // Alert marker ("!" billboard)
        this.alertMesh = null;

        this.buildMesh();
        this.buildHealthBar();
    }

    buildMesh() {
        this.root = new THREE.Group();
        this.root.position.copy(this.pos);

        const isBoss = (this.type === 'BOSS');
        const scale = isBoss ? 1.35 : 1.0;

        // Outlaw Palettes
        const skinMat = new THREE.MeshLambertMaterial({ color: 0xe6b484 });
        const coatMat = new THREE.MeshLambertMaterial({ color: this.cfg.color });
        const darkMat = new THREE.MeshLambertMaterial({ color: 0x221a16 });
        const metalMat = new THREE.MeshLambertMaterial({ color: 0x707480 });

        // Head
        this.head = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 0.35), skinMat);
        this.head.position.y = 1.55 * scale;
        this.head.castShadow = true;
        this.root.add(this.head);

        // Hat
        const brim = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.06, 0.75), darkMat);
        brim.position.y = 0.18;
        this.head.add(brim);
        const crown = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.3, 0.42), darkMat);
        crown.position.y = 0.33;
        this.head.add(crown);

        // Gang Bandana / Mask
        const mask = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.14, 0.38), coatMat);
        mask.position.y = -0.14;
        this.head.add(mask);

        // Torso / Coat
        this.torso = new THREE.Mesh(new THREE.BoxGeometry(0.6 * scale, 0.65 * scale, 0.4 * scale), coatMat);
        this.torso.position.y = 1.1 * scale;
        this.torso.castShadow = true;
        this.root.add(this.torso);

        // Right Arm & Weapon
        this.rightArm = new THREE.Group();
        this.rightArm.position.set(0.38 * scale, 1.35 * scale, 0);
        const rArm = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.55, 0.18), coatMat);
        rArm.position.y = -0.25;
        this.rightArm.add(rArm);

        // Weapon Mesh based on archetype
        if (this.type === 'BRAWLER') {
            // Bowie Knife
            const blade = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.1, 0.4), metalMat);
            blade.position.set(0, -0.45, 0.25);
            this.rightArm.add(blade);
        } else if (this.type === 'SNIPER') {
            // Long Rifle
            const rifle = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.12, 0.85), metalMat);
            rifle.position.set(0, -0.45, 0.45);
            this.rightArm.add(rifle);
        } else {
            // Revolver
            const gun = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.1, 0.32), metalMat);
            gun.position.set(0, -0.45, 0.18);
            this.rightArm.add(gun);
        }
        this.root.add(this.rightArm);

        // Left Arm
        this.leftArm = new THREE.Group();
        this.leftArm.position.set(-0.38 * scale, 1.35 * scale, 0);
        const lArm = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.55, 0.18), coatMat);
        lArm.position.y = -0.25;
        this.leftArm.add(lArm);
        this.root.add(this.leftArm);

        // Legs
        this.leftLeg = new THREE.Group();
        this.leftLeg.position.set(-0.16 * scale, 0.78 * scale, 0);
        const lLeg = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.5, 0.22), darkMat);
        lLeg.position.y = -0.25;
        this.leftLeg.add(lLeg);
        this.root.add(this.leftLeg);

        this.rightLeg = new THREE.Group();
        this.rightLeg.position.set(0.16 * scale, 0.78 * scale, 0);
        const rLeg = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.5, 0.22), darkMat);
        rLeg.position.y = -0.25;
        this.rightLeg.add(rLeg);
        this.root.add(this.rightLeg);

        // Alert Indicator ("!" Billboard)
        const alertCanvas = document.createElement('canvas');
        alertCanvas.width = 64;
        alertCanvas.height = 64;
        const ctx = alertCanvas.getContext('2d');
        ctx.fillStyle = '#ff2222';
        ctx.font = 'bold 50px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('!', 32, 50);
        const alertTex = new THREE.CanvasTexture(alertCanvas);
        const alertMat = new THREE.SpriteMaterial({ map: alertTex, transparent: true });
        this.alertSprite = new THREE.Sprite(alertMat);
        this.alertSprite.scale.set(0.7, 0.7, 0.7);
        this.alertSprite.position.set(0, 2.3 * scale, 0);
        this.alertSprite.visible = false;
        this.root.add(this.alertSprite);

        this.scene.add(this.root);
    }

    buildHealthBar() {
        const canvas = document.createElement('canvas');
        canvas.width = 128;
        canvas.height = 16;
        this.hpTex = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({ map: this.hpTex, transparent: true });
        this.hpSprite = new THREE.Sprite(mat);
        this.hpSprite.scale.set(1.4, 0.2, 1.0);
        this.hpSprite.position.set(0, (this.type === 'BOSS' ? 2.6 : 2.1), 0);
        this.root.add(this.hpSprite);
        this.redrawHealthBar();
    }

    redrawHealthBar() {
        const canvas = this.hpTex.image;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Dark background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Red/Green health fill
        const ratio = Math.max(0, this.hp / this.maxHp);
        ctx.fillStyle = ratio > 0.4 ? '#44cc44' : '#cc2222';
        ctx.fillRect(2, 2, (canvas.width - 4) * ratio, canvas.height - 4);

        // Gold border
        ctx.strokeStyle = '#d4af37';
        ctx.lineWidth = 2;
        ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);

        this.hpTex.needsUpdate = true;
    }

    getBoundingBox() {
        const h = this.type === 'BOSS' ? 2.5 : 1.9;
        const min = new THREE.Vector3(this.pos.x - 0.5, this.pos.y, this.pos.z - 0.5);
        const max = new THREE.Vector3(this.pos.x + 0.5, this.pos.y + h, this.pos.z + 0.5);
        return new THREE.Box3(min, max);
    }

    hasLineOfSight(playerPos, world) {
        const start = this.pos.clone().add(new THREE.Vector3(0, 1.4, 0));
        const end = playerPos.clone().add(new THREE.Vector3(0, 1.2, 0));
        const dir = end.clone().sub(start);
        const dist = dir.length();

        if (dist > this.cfg.sightRange) return false;
        dir.normalize();

        const ray = new THREE.Ray(start, dir);
        for (const col of world.colliders) {
            const hit = ray.intersectBox(col, new THREE.Vector3());
            if (hit) {
                const hitDist = start.distanceTo(hit);
                if (hitDist < dist - 0.5) return false; // Obstructed by building/crate
            }
        }
        return true;
    }

    takeDamage(amount, knockbackDir = null) {
        if (!this.alive) return;
        this.hp -= amount;
        this.flashTimer = 0.2;
        this.staggerTimer = 0.25;
        this.state = 'ALERT';
        this.redrawHealthBar();

        if (knockbackDir) {
            this.vel.addScaledVector(knockbackDir, 4.5);
        }

        if (this.hp <= 0) {
            this.hp = 0;
            this.alive = false;
            this.alertSprite.visible = false;
            this.hpSprite.visible = false;
            if (this.laserLine) {
                this.scene.remove(this.laserLine);
                this.laserLine = null;
            }
            // Collapse rotation
            this.root.rotation.x = Math.PI / 2;
            this.root.position.y = 0.25;
            this.particles.emitImpact(this.pos.clone().add(new THREE.Vector3(0, 0.5, 0)), true);
        }
    }

    update(dt, player, world, weaponManager) {
        if (!this.alive) return;

        // Timers
        if (this.staggerTimer > 0) this.staggerTimer -= dt;
        if (this.attackCooldown > 0) this.attackCooldown -= dt;
        if (this.flashTimer > 0) this.flashTimer -= dt;

        // Flash visual
        const isFlashing = this.flashTimer > 0 && Math.floor(this.flashTimer * 30) % 2 === 0;
        this.root.visible = !isFlashing;

        if (this.staggerTimer > 0) {
            // Apply knockback drag
            this.vel.multiplyScalar(0.85);
            this.pos.addScaledVector(this.vel, dt);
            this.root.position.copy(this.pos);
            return;
        }

        const distToPlayer = this.pos.distanceTo(player.pos);
        const canSee = player.alive && this.hasLineOfSight(player.pos, world);

        // ---------------------------------------------------------
        // State Machine
        // ---------------------------------------------------------
        if (canSee) {
            this.alertSprite.visible = true;

            // Turn towards player
            const dx = player.pos.x - this.pos.x;
            const dz = player.pos.z - this.pos.z;
            const targetYaw = Math.atan2(dx, dz);
            this.yaw += (targetYaw - this.yaw) * Math.min(1.0, 8.0 * dt);

            if (distToPlayer <= this.cfg.attackRange && this.attackCooldown <= 0) {
                // Begin Aim Telegraph
                this.state = 'AIMING';
                this.aimTimer += dt;
                this.vel.set(0, 0, 0);

                // Aim arm at player
                this.rightArm.rotation.x = -Math.PI / 2;

                // Sniper Laser Sight
                if (this.type === 'SNIPER') {
                    this.updateSniperLaser(player.pos);
                }

                if (this.aimTimer >= this.cfg.attackDelay) {
                    // FIRE ATTACK!
                    this.executeAttack(player, weaponManager, world);
                    this.aimTimer = 0.0;
                    this.attackCooldown = (this.type === 'BOSS') ? 1.2 : 2.0;
                    this.state = 'CHASE';
                    if (this.laserLine) {
                        this.scene.remove(this.laserLine);
                        this.laserLine = null;
                    }
                }
            } else {
                this.state = 'CHASE';
                this.aimTimer = 0.0;
                if (this.laserLine) {
                    this.scene.remove(this.laserLine);
                    this.laserLine = null;
                }

                // Close in or flank
                if (distToPlayer > (this.type === 'SNIPER' ? 25 : this.cfg.attackRange * 0.8)) {
                    this.moveTowards(player.pos, dt, world);
                } else {
                    this.vel.set(0, 0, 0);
                }
            }
        } else {
            // Lost sight -> Patrol or search
            this.alertSprite.visible = false;
            this.state = 'PATROL';
            this.aimTimer = 0.0;
            if (this.laserLine) {
                this.scene.remove(this.laserLine);
                this.laserLine = null;
            }

            this.stateTimer -= dt;
            if (this.stateTimer <= 0) {
                this.stateTimer = 2.0 + Math.random() * 3.0;
                this.yaw += (Math.random() - 0.5) * Math.PI;
            }

            // Patrol slowly
            const forward = new THREE.Vector3(Math.sin(this.yaw), 0, Math.cos(this.yaw));
            this.vel.copy(forward).multiplyScalar(this.speed * 0.4);
            this.moveAndAvoid(dt, world);
        }

        // Apply Position
        this.root.position.copy(this.pos);
        this.root.rotation.y = this.yaw;

        // Animate legs when moving
        const isMoving = this.vel.lengthSq() > 0.1;
        if (isMoving) {
            const legSwing = Math.sin(Date.now() * 0.012) * 0.5;
            this.leftLeg.rotation.x = legSwing;
            this.rightLeg.rotation.x = -legSwing;
        } else {
            this.leftLeg.rotation.x = 0;
            this.rightLeg.rotation.x = 0;
        }
    }

    moveTowards(targetPos, dt, world) {
        const dir = targetPos.clone().sub(this.pos);
        dir.y = 0;
        dir.normalize();

        // 3D Obstacle Avoidance (Left and Right whisker checks)
        const whiskerLeft = dir.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.5);
        const whiskerRight = dir.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), -0.5);

        const checkLeft = this.pos.clone().addScaledVector(whiskerLeft, 1.8);
        const checkRight = this.pos.clone().addScaledVector(whiskerRight, 1.8);

        let steer = dir.clone();
        for (const col of world.colliders) {
            if (col.containsPoint(checkLeft)) steer.addScaledVector(whiskerRight, 1.2);
            if (col.containsPoint(checkRight)) steer.addScaledVector(whiskerLeft, 1.2);
        }
        steer.normalize();

        this.vel.copy(steer).multiplyScalar(this.speed);
        this.moveAndAvoid(dt, world);
    }

    moveAndAvoid(dt, world) {
        const nextPos = this.pos.clone().addScaledVector(this.vel, dt);

        // 1. X collision
        this.pos.x = nextPos.x;
        let bBox = this.getBoundingBox();
        for (const col of world.colliders) {
            if (bBox.intersectsBox(col)) {
                this.pos.x = (this.vel.x > 0) ? col.min.x - 0.5 : col.max.x + 0.5;
                this.vel.x = 0;
                bBox = this.getBoundingBox();
            }
        }

        // 2. Z collision
        this.pos.z = nextPos.z;
        bBox = this.getBoundingBox();
        for (const col of world.colliders) {
            if (bBox.intersectsBox(col)) {
                this.pos.z = (this.vel.z > 0) ? col.min.z - 0.5 : col.max.z + 0.5;
                this.vel.z = 0;
                bBox = this.getBoundingBox();
            }
        }
    }

    updateSniperLaser(targetPos) {
        const muzzlePos = this.pos.clone().add(new THREE.Vector3(0, 1.35, 0));
        const endPos = targetPos.clone().add(new THREE.Vector3(0, 1.2, 0));

        if (!this.laserLine) {
            const mat = new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: 2 });
            const geo = new THREE.BufferGeometry().setFromPoints([muzzlePos, endPos]);
            this.laserLine = new THREE.Line(geo, mat);
            this.scene.add(this.laserLine);
        } else {
            this.laserLine.geometry.setFromPoints([muzzlePos, endPos]);
        }
    }

    executeAttack(player, weaponManager, world) {
        const muzzlePos = this.pos.clone().add(new THREE.Vector3(0, 1.35, 0));
        const aimDir = player.pos.clone().add(new THREE.Vector3(0, 1.1, 0)).sub(muzzlePos).normalize();

        if (this.type === 'BRAWLER') {
            // Melee Knife Charge
            audio.playKnifeSlash();
            if (this.pos.distanceTo(player.pos) <= 3.2) {
                player.takeDamage(this.cfg.damage, aimDir);
            }
        } else if (this.type === 'GRENADIER') {
            // Lob 3D Dynamite
            audio.playFuseSizzle();
            const dGroup = new THREE.Group();
            const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.45, 8), new THREE.MeshLambertMaterial({ color: 0xc42820 }));
            dGroup.add(cyl);
            dGroup.position.copy(muzzlePos);
            this.scene.add(dGroup);

            const throwVel = aimDir.clone().multiplyScalar(13.0);
            throwVel.y += 5.5;

            weaponManager.activeDynamites.push({
                mesh: dGroup,
                pos: muzzlePos.clone(),
                vel: throwVel,
                fuse: 2.2,
                damage: 3,
                radius: 7.0
            });
        } else if (this.type === 'BOSS') {
            // Boss Barrage: Dual revolver burst + cluster dynamite
            audio.playGunshot(true);
            this.particles.emitMuzzleFlash(muzzlePos, aimDir);
            player.takeDamage(1, aimDir);

            // 50% chance to also lob a dynamite stick
            if (Math.random() < 0.5) {
                const dGroup = new THREE.Group();
                const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.5, 8), new THREE.MeshLambertMaterial({ color: 0xc42820 }));
                dGroup.add(cyl);
                dGroup.position.copy(muzzlePos);
                this.scene.add(dGroup);

                weaponManager.activeDynamites.push({
                    mesh: dGroup,
                    pos: muzzlePos.clone(),
                    vel: aimDir.clone().multiplyScalar(14.0).add(new THREE.Vector3(0, 4, 0)),
                    fuse: 2.0,
                    damage: 4,
                    radius: 8.0
                });
            }
        } else {
            // Standard Gunner / Sniper Shot
            audio.playGunshot(true);
            this.particles.emitMuzzleFlash(muzzlePos, aimDir);

            // Bullet raycast
            const hitPoint = muzzlePos.clone().addScaledVector(aimDir, 40);
            weaponManager.spawnTracer(muzzlePos, hitPoint);

            // Accuracy check (player can dodge by moving or crouching!)
            const hitChance = (this.type === 'SNIPER') ? 0.85 : (player.isCrouching ? 0.35 : 0.65);
            if (Math.random() < hitChance) {
                player.takeDamage(this.cfg.damage, aimDir);
            }
        }
    }

    dispose() {
        this.scene.remove(this.root);
        if (this.laserLine) this.scene.remove(this.laserLine);
    }
}
