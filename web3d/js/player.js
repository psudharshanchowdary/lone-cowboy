/**
 * 3D Lone Cowboy: Third-Person Player Character & Controller
 * Procedural 3D cowboy model, third-person over-the-shoulder camera,
 * sub-step AABB collision, walk/run/jump/crouch, and recoil animation.
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';
import { CONFIG } from './config.js';
import { audio } from './audio.js';

export class Player {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;

        // Position & Physics
        this.pos = new THREE.Vector3(0, 0, 10);
        this.vel = new THREE.Vector3(0, 0, 0);
        this.onGround = true;
        this.isCrouching = false;
        this.isSprinting = false;

        // Mouse look / Aim rotation (in radians)
        this.yaw = 0.0;
        this.pitch = 0.0;

        // Health & Status
        this.maxHp = CONFIG.PLAYER_MAX_HEALTH;
        this.hp = this.maxHp;
        this.alive = true;
        this.invulnerableTimer = 0.0;
        this.flashTimer = 0.0;

        // Dimensions
        this.standHeight = 1.9;
        this.crouchHeight = 1.2;
        this.radius = 0.45;

        // Animation state
        this.walkCycle = 0.0;
        this.recoilTimer = 0.0;

        this.buildMesh();
    }

    buildMesh() {
        this.root = new THREE.Group();

        // Palette materials
        this.matSkin = new THREE.MeshLambertMaterial({ color: 0xf0c096 });
        this.matHat = new THREE.MeshLambertMaterial({ color: 0x442a1c });
        this.matHatBand = new THREE.MeshLambertMaterial({ color: 0xeeb830 });
        this.matBandana = new THREE.MeshLambertMaterial({ color: 0xc42c26 });
        this.matPoncho = new THREE.MeshLambertMaterial({ color: 0xaa6e36 });
        this.matPants = new THREE.MeshLambertMaterial({ color: 0x304058 });
        this.matBoots = new THREE.MeshLambertMaterial({ color: 0x281812 });
        this.matGun = new THREE.MeshLambertMaterial({ color: 0x50545c });

        // Head
        this.head = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 0.35), this.matSkin);
        this.head.position.y = 1.55;
        this.head.castShadow = true;
        this.root.add(this.head);

        // Stetson Hat
        const hatBrim = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.06, 0.75), this.matHat);
        hatBrim.position.y = 0.18;
        this.head.add(hatBrim);
        const hatCrown = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.3, 0.42), this.matHat);
        hatCrown.position.y = 0.33;
        this.head.add(hatCrown);
        const hatBand = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.06, 0.44), this.matHatBand);
        hatBand.position.y = 0.22;
        this.head.add(hatBand);

        // Red Bandana
        const bandana = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.12, 0.38), this.matBandana);
        bandana.position.y = -0.16;
        this.head.add(bandana);

        // Torso / Poncho
        this.torso = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.65, 0.4), this.matPoncho);
        this.torso.position.y = 1.1;
        this.torso.castShadow = true;
        this.root.add(this.torso);

        // Right Arm & Revolver
        this.rightArm = new THREE.Group();
        this.rightArm.position.set(0.38, 1.35, 0);
        const armMesh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.55, 0.18), this.matPoncho);
        armMesh.position.y = -0.25;
        armMesh.castShadow = true;
        this.rightArm.add(armMesh);

        // Gun in hand
        this.gun = new THREE.Group();
        this.gun.position.set(0, -0.48, 0.2);
        const barrel = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.1, 0.35), this.matGun);
        barrel.position.z = 0.15;
        this.gun.add(barrel);
        const grip = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.15, 0.08), this.matHat);
        grip.position.set(0, -0.08, 0.02);
        this.gun.add(grip);
        this.rightArm.add(this.gun);
        this.root.add(this.rightArm);

        // Left Arm
        this.leftArm = new THREE.Group();
        this.leftArm.position.set(-0.38, 1.35, 0);
        const leftArmMesh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.55, 0.18), this.matPoncho);
        leftArmMesh.position.y = -0.25;
        this.leftArm.add(leftArmMesh);
        this.root.add(this.leftArm);

        // Left & Right Legs
        this.leftLeg = new THREE.Group();
        this.leftLeg.position.set(-0.16, 0.78, 0);
        const legMat = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.5, 0.22), this.matPants);
        legMat.position.y = -0.25;
        this.leftLeg.add(legMat);
        const bootL = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.28, 0.32), this.matBoots);
        bootL.position.set(0, -0.64, 0.05);
        this.leftLeg.add(bootL);
        this.root.add(this.leftLeg);

        this.rightLeg = new THREE.Group();
        this.rightLeg.position.set(0.16, 0.78, 0);
        const legRMat = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.5, 0.22), this.matPants);
        legRMat.position.y = -0.25;
        this.rightLeg.add(legRMat);
        const bootR = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.28, 0.32), this.matBoots);
        bootR.position.set(0, -0.64, 0.05);
        this.rightLeg.add(bootR);
        this.root.add(this.rightLeg);

        this.scene.add(this.root);
    }

    triggerRecoil() {
        this.recoilTimer = 0.14;
    }

    takeDamage(amount, knockbackDir = null) {
        if (!this.alive || this.invulnerableTimer > 0.0) return false;

        this.hp -= amount;
        this.invulnerableTimer = CONFIG.INVULNERABILITY_TIME;
        this.flashTimer = 0.25;
        audio.playDamage();

        if (knockbackDir) {
            this.vel.x += knockbackDir.x * 6.0;
            this.vel.z += knockbackDir.z * 6.0;
            this.vel.y = 4.0;
            this.onGround = false;
        }

        if (this.hp <= 0) {
            this.hp = 0;
            this.alive = false;
        }
        return true;
    }

    update(dt, input, world) {
        if (!this.alive) return;

        // Timers
        if (this.invulnerableTimer > 0) this.invulnerableTimer -= dt;
        if (this.flashTimer > 0) this.flashTimer -= dt;

        // Flash visual
        const isFlashing = this.flashTimer > 0 && Math.floor(this.flashTimer * 25) % 2 === 0;
        this.root.visible = !isFlashing;

        // Mouse look angles update
        this.yaw -= input.mouseDeltaX * 0.0022;
        this.pitch -= input.mouseDeltaY * 0.0022;
        this.pitch = Math.max(-1.1, Math.min(1.1, this.pitch));

        // State flags
        this.isCrouching = input.crouch && this.onGround;
        this.isSprinting = input.sprint && !this.isCrouching && input.moveZ < 0;

        let speed = CONFIG.PLAYER_SPEED;
        if (this.isCrouching) speed = CONFIG.PLAYER_CROUCH_SPEED;
        else if (this.isSprinting) speed = CONFIG.PLAYER_SPRINT_SPEED;

        // Calculate move direction relative to camera yaw
        const forward = new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
        const right = new THREE.Vector3(Math.cos(this.yaw), 0, -Math.sin(this.yaw));

        const moveDir = new THREE.Vector3(0, 0, 0);
        if (input.moveZ !== 0) moveDir.addScaledVector(forward, -input.moveZ);
        if (input.moveX !== 0) moveDir.addScaledVector(right, input.moveX);
        if (moveDir.lengthSq() > 0.001) moveDir.normalize();

        // Horizontal velocity
        this.vel.x = moveDir.x * speed;
        this.vel.z = moveDir.z * speed;

        // Jump
        if (input.jump && this.onGround && !this.isCrouching) {
            this.vel.y = CONFIG.PLAYER_JUMP_FORCE;
            this.onGround = false;
        }

        // Apply Gravity
        this.vel.y -= CONFIG.GRAVITY * dt;

        // 3D Collision Movement & Slide
        this.moveAndCollide(dt, world);

        // Rotate root model towards camera aim
        this.root.position.copy(this.pos);
        this.root.rotation.y = this.yaw;

        // Limb walk animation
        const isMoving = this.vel.x * this.vel.x + this.vel.z * this.vel.z > 0.5;
        if (isMoving && this.onGround) {
            this.walkCycle += dt * (this.isSprinting ? 18 : 11);
            const swing = Math.sin(this.walkCycle) * 0.55;
            this.leftLeg.rotation.x = swing;
            this.rightLeg.rotation.x = -swing;
            this.leftArm.rotation.x = -swing * 0.5;
        } else {
            this.leftLeg.rotation.x *= 0.8;
            this.rightLeg.rotation.x *= 0.8;
            this.leftArm.rotation.x *= 0.8;
        }

        // Gun aim & Recoil animation
        if (this.recoilTimer > 0) {
            this.recoilTimer -= dt;
            this.rightArm.rotation.x = -Math.PI / 2 + this.pitch - 0.35;
        } else {
            this.rightArm.rotation.x = -Math.PI / 2 + this.pitch;
        }

        // Crouch stance adjustment
        const targetScaleY = this.isCrouching ? 0.65 : 1.0;
        this.root.scale.y += (targetScaleY - this.root.scale.y) * Math.min(1.0, 15.0 * dt);

        // Update Over-the-shoulder Third-Person Camera
        this.updateCamera(dt);
    }

    moveAndCollide(dt, world) {
        // Sub-step movement: X, Z, then Y
        const nextPos = this.pos.clone().addScaledVector(this.vel, dt);

        // 1. Horizontal X
        this.pos.x = nextPos.x;
        let pBox = this.getBoundingBox();
        for (const col of world.colliders) {
            if (pBox.intersectsBox(col)) {
                if (this.vel.x > 0) this.pos.x = col.min.x - this.radius;
                else if (this.vel.x < 0) this.pos.x = col.max.x + this.radius;
                this.vel.x = 0;
                pBox = this.getBoundingBox();
            }
        }

        // 2. Horizontal Z
        this.pos.z = nextPos.z;
        pBox = this.getBoundingBox();
        for (const col of world.colliders) {
            if (pBox.intersectsBox(col)) {
                if (this.vel.z > 0) this.pos.z = col.min.z - this.radius;
                else if (this.vel.z < 0) this.pos.z = col.max.z + this.radius;
                this.vel.z = 0;
                pBox = this.getBoundingBox();
            }
        }

        // 3. Vertical Y & Ground check
        this.pos.y = nextPos.y;
        this.onGround = false;

        // Ground plane floor at y = 0
        if (this.pos.y <= 0) {
            this.pos.y = 0;
            this.vel.y = 0;
            this.onGround = true;
        }

        // Solid box collisions for roofs/crates
        pBox = this.getBoundingBox();
        for (const col of world.colliders) {
            if (pBox.intersectsBox(col)) {
                if (this.vel.y < 0 && this.pos.y >= col.max.y - 0.4) {
                    this.pos.y = col.max.y;
                    this.vel.y = 0;
                    this.onGround = true;
                } else if (this.vel.y > 0) {
                    this.pos.y = col.min.y - (this.isCrouching ? this.crouchHeight : this.standHeight);
                    this.vel.y = 0;
                }
                pBox = this.getBoundingBox();
            }
        }
    }

    getBoundingBox() {
        const h = this.isCrouching ? this.crouchHeight : this.standHeight;
        const min = new THREE.Vector3(this.pos.x - this.radius, this.pos.y, this.pos.z - this.radius);
        const max = new THREE.Vector3(this.pos.x + this.radius, this.pos.y + h, this.pos.z + this.radius);
        return new THREE.Box3(min, max);
    }

    updateCamera(dt) {
        // Calculate offset vector rotated by yaw & pitch
        const offset = new THREE.Vector3(
            CONFIG.CAMERA_OFFSET.x,
            CONFIG.CAMERA_OFFSET.y * (this.isCrouching ? 0.75 : 1.0),
            CONFIG.CAMERA_OFFSET.z
        );
        offset.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.yaw);

        const targetCamPos = this.pos.clone().add(offset);
        this.camera.position.lerp(targetCamPos, CONFIG.CAMERA_LERP);

        // Look at point ahead in direction of yaw & pitch
        const lookDir = new THREE.Vector3(
            -Math.sin(this.yaw) * Math.cos(this.pitch),
            Math.sin(this.pitch),
            -Math.cos(this.yaw) * Math.cos(this.pitch)
        ).normalize();

        const lookTarget = this.camera.position.clone().add(lookDir.multiplyScalar(20));
        this.camera.lookAt(lookTarget);
    }

    getMuzzlePosition() {
        const v = new THREE.Vector3(0.38, 0.85, 0.4);
        v.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.yaw);
        return this.pos.clone().add(v);
    }

    getAimDirection() {
        return new THREE.Vector3(
            -Math.sin(this.yaw) * Math.cos(this.pitch),
            Math.sin(this.pitch),
            -Math.cos(this.yaw) * Math.cos(this.pitch)
        ).normalize();
    }
}
