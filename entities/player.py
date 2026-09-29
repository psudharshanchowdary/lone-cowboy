"""
Player character: The Lone Cowboy.
Implements walk, run, jump (with coyote time & jump buffering), crouch,
revolver shooting, cylinder reloading, melee knife strike, dynamite throwing,
and checkpoint respawn.
"""
import pygame
from config import (
    PLAYER_WALK_SPEED, PLAYER_RUN_SPEED, PLAYER_CROUCH_SPEED,
    PLAYER_JUMP_FORCE, PLAYER_MAX_HEALTH, COYOTE_TIME, JUMP_BUFFER_TIME,
    KNOCKBACK_FORCE_X, KNOCKBACK_FORCE_Y
)
from entities.entity import Entity
from weapons.weapon import Revolver, DynamiteWeapon, MeleeWeapon
from gfx.sprites import SpriteManager
from gfx.particles import ParticleManager

class Player(Entity):
    def __init__(self, x, y):
        # 16 wide x 24 high base bounding box
        super().__init__(x, y, width=12, height=22, max_health=PLAYER_MAX_HEALTH)

        self.spawn_x = float(x)
        self.spawn_y = float(y)
        self.checkpoint_x = float(x)
        self.checkpoint_y = float(y)

        # Platforming feel enhancements
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0

        # Weapons
        self.revolver = Revolver()
        self.dynamite = DynamiteWeapon()
        self.melee = MeleeWeapon()

        # States & Animation
        self.state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.action_anim_timer = 0.0  # timer for shoot/melee overlays

        # Crouching state
        self.is_crouching = False
        self.stand_height = 22
        self.crouch_height = 14

    def respawn_at_checkpoint(self):
        self.x = self.checkpoint_x
        self.y = self.checkpoint_y
        self.vx = 0.0
        self.vy = 0.0
        self.health = self.max_health
        self.is_alive = True
        self.invulnerable_timer = 1.5
        self.flash_timer = 0.0
        self.knockback_active = False
        self.revolver.ammo = self.revolver.capacity
        self.revolver.cancel_reload()

    def set_checkpoint(self, x, y):
        self.checkpoint_x = float(x)
        self.checkpoint_y = float(y)

    def handle_input(self, input_handler, tilemap):
        if not self.is_alive:
            return None, None, None

        new_bullets = []
        new_dynamites = []
        new_melee = []

        # Buffer jump input
        if input_handler.jump_pressed:
            self.jump_buffer_timer = JUMP_BUFFER_TIME

        # Drop down through one-way platform
        if input_handler.is_crouching and input_handler.jump_pressed:
            self.drop_through_timer = 0.25
            self.jump_buffer_timer = 0.0

        # Crouch handling
        if input_handler.is_crouching and self.on_ground:
            if not self.is_crouching:
                self.is_crouching = True
                self.height = self.crouch_height
                self.y += (self.stand_height - self.crouch_height)
        else:
            if self.is_crouching:
                # Stand up if space above allows
                test_rect = pygame.Rect(int(self.x), int(self.y - (self.stand_height - self.crouch_height)), self.width, self.stand_height)
                solids = tilemap.get_solid_tiles_near(test_rect)
                can_stand = not any(test_rect.colliderect(s) for s in solids)
                if can_stand:
                    self.is_crouching = False
                    self.y -= (self.stand_height - self.crouch_height)
                    self.height = self.stand_height

        # Horizontal movement
        if not self.knockback_active:
            if self.is_crouching:
                speed = PLAYER_CROUCH_SPEED
            elif input_handler.is_running:
                speed = PLAYER_RUN_SPEED
            else:
                speed = PLAYER_WALK_SPEED

            self.vx = input_handler.move_x * speed

            if input_handler.move_x != 0:
                self.facing_right = (input_handler.move_x > 0)
                if self.on_ground and self.anim_frame % 2 == 0:
                    ParticleManager.get_instance().emit_dust(self.x + self.width // 2, self.y + self.height)

        # Jumping (Coyote time + Jump buffer)
        can_jump = (self.on_ground or self.coyote_timer > 0.0)
        if self.jump_buffer_timer > 0.0 and can_jump and not self.is_crouching:
            self.vy = PLAYER_JUMP_FORCE
            self.on_ground = False
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0
            ParticleManager.get_instance().emit_dust(self.x + self.width // 2, self.y + self.height)

        # Variable jump height (releasing jump early truncates ascent)
        if not input_handler.jump_held and self.vy < -80.0:
            self.vy *= 0.55

        # Combat Actions
        # 1. Melee knife attack
        if input_handler.melee_pressed:
            strike = self.melee.strike(self.rect, self.facing_right, owner="player")
            if strike:
                new_melee.append(strike)
                self.action_anim_timer = 0.18
                self.state = "melee"

        # 2. Revolver Shoot
        elif input_handler.shoot_pressed:
            bullet = self.revolver.shoot(self.x, self.y, 1 if self.facing_right else -1, owner="player")
            if bullet:
                new_bullets.append(bullet)
                self.action_anim_timer = 0.16
                self.state = "shoot"

        # 3. Reload Revolver
        if input_handler.reload_pressed:
            self.revolver.start_reload()

        # 4. Throw Dynamite
        if input_handler.dynamite_pressed:
            dyn = self.dynamite.throw(self.x, self.y, 1 if self.facing_right else -1, owner="player")
            if dyn:
                new_dynamites.append(dyn)
                self.action_anim_timer = 0.16

        return new_bullets, new_dynamites, new_melee

    def update(self, tilemap, dt):
        if not self.is_alive:
            return

        # Update weapons
        self.revolver.update(dt)
        self.dynamite.update(dt)
        self.melee.update(dt)

        # Timers
        self.update_timers(dt)

        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if self.jump_buffer_timer > 0.0:
            self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        # Apply gravity & slide
        self.apply_gravity(dt)
        self.move_and_slide(tilemap, dt)

        # Animation states
        if self.action_anim_timer > 0.0:
            self.action_anim_timer -= dt
        else:
            if self.is_crouching:
                self.state = "crouch"
            elif not self.on_ground:
                self.state = "jump" if self.vy < 0 else "fall"
            elif abs(self.vx) > 10.0:
                self.state = "walk"
            else:
                self.state = "idle"

        # Walk cycle frame ticker
        self.anim_timer += dt
        if self.anim_timer >= 0.12:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, surface, camera):
        if not self.is_alive:
            return

        sprite = SpriteManager.get_instance().get_player_sprite(
            state=self.state,
            facing_right=self.facing_right,
            frame=self.anim_frame
        )

        draw_rect = camera.apply(self.rect)
        # Adjust draw y slightly to align sprite feet with bottom of hitbox
        sprite_y = draw_rect.bottom - sprite.get_height()
        sprite_x = draw_rect.centerx - sprite.get_width() // 2

        self.draw_flash_silhouette(surface, sprite, (sprite_x, sprite_y))
