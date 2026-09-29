/**
 * 3D Lone Cowboy: Wild West Frontier Town Environment
 * Builds Saloon, Sheriff Office, Bank, Water Tower, interactive TNT barrels, crates, and cacti.
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';

export class World {
    constructor(scene) {
        this.scene = scene;
        this.colliders = [];        // Static AABB boxes for physics collision
        this.tntBarrels = [];       // Shootable explosive barrels
        this.coverPoints = [];      // Tactical cover locations for bots

        // Materials
        this.matGround = new THREE.MeshLambertMaterial({ color: 0xd6a870 }); // Desert sand
        this.matStreet = new THREE.MeshLambertMaterial({ color: 0xb88850 }); // Packed dirt road
        this.matWood = new THREE.MeshLambertMaterial({ color: 0x825434 });   // Dark saloon wood
        this.matWoodPlank = new THREE.MeshLambertMaterial({ color: 0xa47048 }); // Sidewalk planks
        this.matBrick = new THREE.MeshLambertMaterial({ color: 0x8a382c });  // Red clay / brick
        this.matStone = new THREE.MeshLambertMaterial({ color: 0xba9b76 });  // Bank sandstone
        this.matCactus = new THREE.MeshLambertMaterial({ color: 0x487d3a }); // Desert cactus
        this.matTNT = new THREE.MeshLambertMaterial({ color: 0xc42820 });    // Red TNT barrel
        this.matMetal = new THREE.MeshLambertMaterial({ color: 0x585c64 });  // Iron bands / roof
    }

    build() {
        this.setupLighting();
        this.buildTerrain();
        this.buildSaloon(-15, 0, -25);
        this.buildSheriff(15, 0, -25);
        this.buildBank(15, 0, -45);
        this.buildGeneralStore(-15, 0, -45);
        this.buildWaterTower(-22, 0, -10);
        this.buildWindmill(22, 0, -10);
        this.spawnPropsAndCover();
        this.spawnCacti();
    }

    setupLighting() {
        // Atmospheric desert sunset fog
        this.scene.background = new THREE.Color(0xf5b26e);
        this.scene.fog = new THREE.FogExp2(0xf5b26e, 0.009);

        // Ambient Light
        const ambient = new THREE.AmbientLight(0xffeedd, 0.65);
        this.scene.add(ambient);

        // Western Sunset Sun (Directional Light with crisp shadows)
        const sun = new THREE.DirectionalLight(0xfff2cc, 1.25);
        sun.position.set(45, 60, 35);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.camera.near = 0.5;
        sun.shadow.camera.far = 160;
        const d = 50;
        sun.shadow.camera.left = -d;
        sun.shadow.camera.right = d;
        sun.shadow.camera.top = d;
        sun.shadow.camera.bottom = -d;
        sun.shadow.bias = -0.0005;
        this.scene.add(sun);
    }

    buildTerrain() {
        // Vast desert ground
        const groundGeo = new THREE.PlaneGeometry(300, 300);
        const ground = new THREE.Mesh(groundGeo, this.matGround);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);

        // Main Frontier Street
        const streetGeo = new THREE.PlaneGeometry(16, 120);
        const street = new THREE.Mesh(streetGeo, this.matStreet);
        street.rotation.x = -Math.PI / 2;
        street.position.set(0, 0.02, -30);
        street.receiveShadow = true;
        this.scene.add(street);

        // Boardwalk sidewalks
        for (const side of [-8.5, 8.5]) {
            const walkGeo = new THREE.BoxGeometry(3.5, 0.25, 100);
            const walk = new THREE.Mesh(walkGeo, this.matWoodPlank);
            walk.position.set(side < 0 ? -10.2 : 10.2, 0.12, -35);
            walk.receiveShadow = true;
            this.scene.add(walk);
        }
    }

    addBoxCollider(x, y, z, w, h, d) {
        const box = new THREE.Box3();
        box.setFromCenterAndSize(new THREE.Vector3(x, y, z), new THREE.Vector3(w, h, d));
        this.colliders.push(box);
        return box;
    }

    // -------------------------------------------------------------
    // The Saloon (Two-story with Balcony and Porch)
    // -------------------------------------------------------------
    buildSaloon(x, y, z) {
        const group = new THREE.Group();
        group.position.set(x, y, z);

        // Main building block
        const mainW = 14, mainH = 9, mainD = 16;
        const bldGeo = new THREE.BoxGeometry(mainW, mainH, mainD);
        const bld = new THREE.Mesh(bldGeo, this.matWood);
        bld.position.set(0, mainH / 2, 0);
        bld.castShadow = true;
        bld.receiveShadow = true;
        group.add(bld);
        this.addBoxCollider(x, y + mainH / 2, z, mainW, mainH, mainD);

        // Front Porch & Balcony
        const porchD = 4;
        const porchRoofGeo = new THREE.BoxGeometry(mainW + 1, 0.3, porchD);
        const porchRoof = new THREE.Mesh(porchRoofGeo, this.matWoodPlank);
        porchRoof.position.set(0, 4.8, mainD / 2 + porchD / 2);
        porchRoof.castShadow = true;
        porchRoof.receiveShadow = true;
        group.add(porchRoof);
        // Balcony floor collider
        this.addBoxCollider(x, y + 4.8, z + mainD / 2 + porchD / 2, mainW + 1, 0.3, porchD);

        // Balcony posts
        for (let i = -1; i <= 1; i += 2) {
            const postGeo = new THREE.BoxGeometry(0.3, 4.8, 0.3);
            const post = new THREE.Mesh(postGeo, this.matWood);
            post.position.set(i * (mainW / 2 - 0.5), 2.4, mainD / 2 + porchD - 0.2);
            post.castShadow = true;
            group.add(post);
        }

        // Balcony railing
        const railGeo = new THREE.BoxGeometry(mainW, 0.8, 0.2);
        const rail = new THREE.Mesh(railGeo, this.matWoodPlank);
        rail.position.set(0, 5.3, mainD / 2 + porchD - 0.1);
        group.add(rail);

        // Front "SALOON" Sign Header
        const signGeo = new THREE.BoxGeometry(8, 1.8, 0.4);
        const signMat = new THREE.MeshLambertMaterial({ color: 0x221810 });
        const sign = new THREE.Mesh(signGeo, signMat);
        sign.position.set(0, 8.2, mainD / 2 + 0.3);
        group.add(sign);

        this.scene.add(group);
    }

    // -------------------------------------------------------------
    // Sheriff's Office & Jail
    // -------------------------------------------------------------
    buildSheriff(x, y, z) {
        const group = new THREE.Group();
        group.position.set(x, y, z);

        const w = 12, h = 6.5, d = 14;
        const bldGeo = new THREE.BoxGeometry(w, h, d);
        const bld = new THREE.Mesh(bldGeo, this.matBrick);
        bld.position.set(0, h / 2, 0);
        bld.castShadow = true;
        bld.receiveShadow = true;
        group.add(bld);
        this.addBoxCollider(x, y + h / 2, z, w, h, d);

        // Roof overhang
        const roofGeo = new THREE.BoxGeometry(w + 1.5, 0.6, d + 1.5);
        const roof = new THREE.Mesh(roofGeo, this.matWood);
        roof.position.set(0, h + 0.3, 0);
        roof.castShadow = true;
        group.add(roof);

        // Porch roof
        const porchRoof = new THREE.Mesh(new THREE.BoxGeometry(w, 0.3, 3.5), this.matWoodPlank);
        porchRoof.position.set(0, 4.2, d / 2 + 1.75);
        group.add(porchRoof);

        this.scene.add(group);
    }

    // -------------------------------------------------------------
    // Frontier Bank (Sandstone & Pillars)
    // -------------------------------------------------------------
    buildBank(x, y, z) {
        const group = new THREE.Group();
        group.position.set(x, y, z);

        const w = 13, h = 7.5, d = 15;
        const bldGeo = new THREE.BoxGeometry(w, h, d);
        const bld = new THREE.Mesh(bldGeo, this.matStone);
        bld.position.set(0, h / 2, 0);
        bld.castShadow = true;
        bld.receiveShadow = true;
        group.add(bld);
        this.addBoxCollider(x, y + h / 2, z, w, h, d);

        // Four sandstone columns in front
        for (let i = -1.5; i <= 1.5; i += 1.0) {
            const colGeo = new THREE.CylinderGeometry(0.35, 0.4, 6.5, 8);
            const col = new THREE.Mesh(colGeo, this.matStone);
            col.position.set(i * 3.2, 3.25, d / 2 + 1.8);
            col.castShadow = true;
            group.add(col);
        }

        this.scene.add(group);
    }

    // -------------------------------------------------------------
    // General Store / Gunsmith
    // -------------------------------------------------------------
    buildGeneralStore(x, y, z) {
        const group = new THREE.Group();
        group.position.set(x, y, z);

        const w = 14, h = 6.8, d = 15;
        const bldGeo = new THREE.BoxGeometry(w, h, d);
        const bld = new THREE.Mesh(bldGeo, this.matWoodPlank);
        bld.position.set(0, h / 2, 0);
        bld.castShadow = true;
        bld.receiveShadow = true;
        group.add(bld);
        this.addBoxCollider(x, y + h / 2, z, w, h, d);

        this.scene.add(group);
    }

    // -------------------------------------------------------------
    // Water Tower
    // -------------------------------------------------------------
    buildWaterTower(x, y, z) {
        const group = new THREE.Group();
        group.position.set(x, y, z);

        // 4 Legs
        const legH = 11;
        for (let i = -1; i <= 1; i += 2) {
            for (let j = -1; j <= 1; j += 2) {
                const legGeo = new THREE.BoxGeometry(0.4, legH, 0.4);
                const leg = new THREE.Mesh(legGeo, this.matWood);
                leg.position.set(i * 2.2, legH / 2, j * 2.2);
                leg.castShadow = true;
                group.add(leg);
            }
        }

        // Circular Water Tank
        const tankGeo = new THREE.CylinderGeometry(3.0, 3.0, 5.0, 16);
        const tank = new THREE.Mesh(tankGeo, this.matWood);
        tank.position.set(0, legH + 2.5, 0);
        tank.castShadow = true;
        group.add(tank);

        // Metal roof cone
        const coneGeo = new THREE.ConeGeometry(3.4, 2.0, 16);
        const cone = new THREE.Mesh(coneGeo, this.matMetal);
        cone.position.set(0, legH + 6.0, 0);
        cone.castShadow = true;
        group.add(cone);

        this.addBoxCollider(x, y + legH / 2, z, 5.0, legH + 7.0, 5.0);
        this.scene.add(group);
    }

    // -------------------------------------------------------------
    // Windmill
    // -------------------------------------------------------------
    buildWindmill(x, y, z) {
        const group = new THREE.Group();
        group.position.set(x, y, z);

        const baseGeo = new THREE.CylinderGeometry(1.2, 2.2, 12, 6);
        const base = new THREE.Mesh(baseGeo, this.matWood);
        base.position.set(0, 6, 0);
        base.castShadow = true;
        group.add(base);

        // Fan Blades
        this.windmillBlades = new THREE.Group();
        this.windmillBlades.position.set(0, 11.5, 1.4);
        for (let i = 0; i < 4; i++) {
            const bladeGeo = new THREE.BoxGeometry(0.3, 4.0, 0.05);
            const blade = new THREE.Mesh(bladeGeo, this.matMetal);
            blade.position.set(0, 2.0, 0);
            const pivot = new THREE.Group();
            pivot.rotation.z = i * (Math.PI / 2);
            pivot.add(blade);
            this.windmillBlades.add(pivot);
        }
        group.add(this.windmillBlades);

        this.addBoxCollider(x, y + 6, z, 3.5, 12, 3.5);
        this.scene.add(group);
    }

    // -------------------------------------------------------------
    // Tactical Props: Crates, Barrels, and Shootable TNT
    // -------------------------------------------------------------
    spawnPropsAndCover() {
        const crateGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
        const barrelGeo = new THREE.CylinderGeometry(0.5, 0.5, 1.3, 10);

        const crateLocations = [
            // Cover clusters on street
            { x: -4, z: -15 }, { x: -4, z: -16.2 }, { x: -4, z: -17.4 },
            { x: 4.5, z: -22 }, { x: 4.5, z: -23.4 },
            { x: -3.5, z: -35 }, { x: -3.5, z: -36.5 },
            { x: 3.8, z: -48 }, { x: 3.8, z: -49.5 },
            // Sidewalk props
            { x: -9.5, z: -20 }, { x: 9.5, z: -28 }
        ];

        crateLocations.forEach(c => {
            const mesh = new THREE.Mesh(crateGeo, this.matWoodPlank);
            mesh.position.set(c.x, 0.6, c.z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            this.scene.add(mesh);
            this.addBoxCollider(c.x, 0.6, c.z, 1.2, 1.2, 1.2);
            this.coverPoints.push(new THREE.Vector3(c.x, 0, c.z));
        });

        // Shootable TNT Explosive Barrels
        const tntLocations = [
            { x: -5.5, z: -22 },
            { x: 5.5, z: -34 },
            { x: -5.0, z: -46 },
            { x: 0, z: -30 }
        ];

        tntLocations.forEach(loc => {
            const mesh = new THREE.Mesh(barrelGeo, this.matTNT);
            mesh.position.set(loc.x, 0.65, loc.z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            this.scene.add(mesh);

            const barrelObj = {
                mesh: mesh,
                pos: mesh.position,
                hp: 1,
                alive: true,
                radius: 9.0,
                damage: 6
            };
            this.tntBarrels.push(barrelObj);
            this.addBoxCollider(loc.x, 0.65, loc.z, 1.0, 1.3, 1.0);
        });
    }

    spawnCacti() {
        const cactiLocs = [
            { x: -28, z: -15, s: 1.2 }, { x: -26, z: -35, s: 1.5 },
            { x: 26, z: -18, s: 1.3 }, { x: 28, z: -42, s: 1.6 },
            { x: -18, z: 12, s: 1.1 }, { x: 18, z: 10, s: 1.4 }
        ];

        cactiLocs.forEach(c => {
            const group = new THREE.Group();
            group.position.set(c.x, 0, c.z);
            group.scale.set(c.s, c.s, c.s);

            // Trunk
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 3.5, 8), this.matCactus);
            trunk.position.y = 1.75;
            trunk.castShadow = true;
            group.add(trunk);

            // Left arm
            const arm1 = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 1.2, 8), this.matCactus);
            arm1.position.set(-0.7, 2.0, 0);
            arm1.rotation.z = Math.PI / 2;
            group.add(arm1);
            const arm1Up = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 1.0, 8), this.matCactus);
            arm1Up.position.set(-1.2, 2.5, 0);
            group.add(arm1Up);

            this.scene.add(group);
            this.addBoxCollider(c.x, 1.75, c.z, 1.2, 3.5, 1.2);
        });
    }

    update(dt) {
        if (this.windmillBlades) {
            this.windmillBlades.rotation.z += dt * 1.5;
        }
    }
}
