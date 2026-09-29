/**
 * 3D Lone Cowboy: Visual Particle System
 * Muzzle flashes, gunpowder smoke, ricochet sparks, blood puffs, and dynamite explosions.
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';

export class ParticleSystem {
    constructor(scene) {
        this.scene = scene;
        this.particles = [];

        // Shared geometries & materials for high performance
        this.sparkGeo = new THREE.BufferGeometry();
        this.sparkGeo.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0], 3));

        this.smokeGeo = new THREE.DodecahedronGeometry(0.2, 1);
        this.fireGeo = new THREE.DodecahedronGeometry(0.4, 1);
    }

    update(dt) {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.age += dt;

            if (p.age >= p.lifetime) {
                this.scene.remove(p.mesh);
                if (p.mesh.geometry && p.disposeGeo) p.mesh.geometry.dispose();
                this.particles.splice(i, 1);
                continue;
            }

            // Physics update
            p.vel.y -= p.gravity * dt;
            p.mesh.position.addScaledVector(p.vel, dt);

            // Scale & Fade
            const progress = p.age / p.lifetime;
            if (p.shrink) {
                const s = Math.max(0.01, (1.0 - progress) * p.initialScale);
                p.mesh.scale.set(s, s, s);
            } else if (p.expand) {
                const s = p.initialScale * (1.0 + progress * 2.5);
                p.mesh.scale.set(s, s, s);
            }

            if (p.mesh.material && p.mesh.material.opacity !== undefined) {
                p.mesh.material.opacity = Math.max(0.0, 1.0 - progress);
            }
        }
    }

    emitMuzzleFlash(pos, dir) {
        // Point light flash
        const light = new THREE.PointLight(0xffcc44, 4.0, 6.0);
        light.position.copy(pos);
        this.scene.add(light);
        this.particles.push({
            mesh: light,
            vel: new THREE.Vector3(0, 0, 0),
            gravity: 0,
            age: 0,
            lifetime: 0.06,
            initialScale: 1,
            shrink: false
        });

        // Sparks
        for (let i = 0; i < 6; i++) {
            const mat = new THREE.MeshBasicMaterial({ color: 0xffe066, transparent: true, opacity: 1.0 });
            const mesh = new THREE.Mesh(this.smokeGeo, mat);
            mesh.scale.set(0.2, 0.2, 0.2);
            mesh.position.copy(pos);
            this.scene.add(mesh);

            const spread = new THREE.Vector3(
                (Math.random() - 0.5) * 1.5,
                (Math.random() - 0.5) * 1.5,
                (Math.random() - 0.5) * 1.5
            );
            const vel = dir.clone().multiplyScalar(15.0).add(spread);

            this.particles.push({
                mesh: mesh,
                vel: vel,
                gravity: 12.0,
                age: 0,
                lifetime: 0.12,
                initialScale: 0.2,
                shrink: true,
                disposeGeo: false
            });
        }

        // Smoke puff
        for (let i = 0; i < 3; i++) {
            const mat = new THREE.MeshLambertMaterial({ color: 0x909090, transparent: true, opacity: 0.5 });
            const mesh = new THREE.Mesh(this.smokeGeo, mat);
            mesh.position.copy(pos);
            this.scene.add(mesh);

            const vel = dir.clone().multiplyScalar(2.0).add(new THREE.Vector3(
                (Math.random() - 0.5) * 1.0,
                Math.random() * 1.2,
                (Math.random() - 0.5) * 1.0
            ));

            this.particles.push({
                mesh: mesh,
                vel: vel,
                gravity: -1.0, // floats up
                age: 0,
                lifetime: 0.6,
                initialScale: 0.35,
                expand: true,
                disposeGeo: false
            });
        }
    }

    emitImpact(pos, isFlesh = false) {
        const count = isFlesh ? 8 : 12;
        const color = isFlesh ? 0xaa1818 : 0xffcc66;

        for (let i = 0; i < count; i++) {
            const mat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 1.0 });
            const mesh = new THREE.Mesh(this.smokeGeo, mat);
            mesh.scale.set(0.18, 0.18, 0.18);
            mesh.position.copy(pos);
            this.scene.add(mesh);

            const vel = new THREE.Vector3(
                (Math.random() - 0.5) * 8.0,
                Math.random() * 6.0 + 1.0,
                (Math.random() - 0.5) * 8.0
            );

            this.particles.push({
                mesh: mesh,
                vel: vel,
                gravity: 18.0,
                age: 0,
                lifetime: 0.3,
                initialScale: 0.18,
                shrink: true,
                disposeGeo: false
            });
        }
    }

    emitExplosion(pos, radius = 8.5) {
        // Flash light
        const light = new THREE.PointLight(0xff8822, 10.0, radius * 2.5);
        light.position.copy(pos);
        this.scene.add(light);
        this.particles.push({
            mesh: light,
            vel: new THREE.Vector3(0, 0, 0),
            gravity: 0,
            age: 0,
            lifetime: 0.25,
            initialScale: 1
        });

        // Fireballs
        for (let i = 0; i < 20; i++) {
            const col = Math.random() > 0.4 ? 0xff4411 : 0xffbb22;
            const mat = new THREE.MeshLambertMaterial({ color: col, transparent: true, opacity: 0.9 });
            const mesh = new THREE.Mesh(this.fireGeo, mat);
            mesh.position.copy(pos);
            this.scene.add(mesh);

            const vel = new THREE.Vector3(
                (Math.random() - 0.5) * 16.0,
                Math.random() * 12.0 + 2.0,
                (Math.random() - 0.5) * 16.0
            );

            this.particles.push({
                mesh: mesh,
                vel: vel,
                gravity: 8.0,
                age: 0,
                lifetime: 0.45,
                initialScale: 0.6,
                expand: true,
                disposeGeo: false
            });
        }

        // Heavy smoke column
        for (let i = 0; i < 15; i++) {
            const mat = new THREE.MeshLambertMaterial({ color: 0x444444, transparent: true, opacity: 0.7 });
            const mesh = new THREE.Mesh(this.smokeGeo, mat);
            mesh.position.copy(pos);
            this.scene.add(mesh);

            const vel = new THREE.Vector3(
                (Math.random() - 0.5) * 6.0,
                Math.random() * 8.0 + 3.0,
                (Math.random() - 0.5) * 6.0
            );

            this.particles.push({
                mesh: mesh,
                vel: vel,
                gravity: -1.5,
                age: 0,
                lifetime: 1.2,
                initialScale: 0.8,
                expand: true,
                disposeGeo: false
            });
        }
    }
}
