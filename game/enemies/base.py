"""Base class for all AI-controlled enemy ships."""
from __future__ import annotations

import random
import pygame

from .ai import EnemyBrain
from .movement import EnemyMovement
from .weapons import EnemyWeaponSystem


class EnemyBase:
    """Composable enemy entity used by standard, fast, heavy and elite variants.

    Bosses can later subclass this class while reusing movement, weapons and
    collision handling, or replace individual components.
    """

    def __init__(
        self,
        image,
        ship_name,
        archetype,
        window_width,
        window_height,
        spawn_x,
        spawn_y,
        ship_scale,
        role="attacker",
        torpedo_image=None,
        difficulty_scale=1.0,
    ):
        self.ship_name = ship_name
        self.archetype = archetype
        self.role = role
        self.window_width = window_width
        self.window_height = window_height
        self.base_image = image
        self.ship_scale = ship_scale
        self.visual_scale = ship_scale * archetype.visual_scale_multiplier

        # Enemy ships fly toward the player, so use the player sprite rotated 180°.
        scaled = pygame.transform.scale_by(image, self.visual_scale)
        self.image = pygame.transform.rotate(scaled, 180)
        self.flash_image = self.image.copy()
        self.flash_image.fill((85, 85, 85, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.width, self.height = self.image.get_size()

        self.x = float(spawn_x)
        self.y = float(spawn_y)
        self.vx = 0.0
        self.vy = 0.0
        # The manager already applies the selected difficulty and system
        # progression to the archetype. Keep the entity itself data-driven so
        # balancing stays centralized in game/constants.py.
        self.max_hp = int(archetype.max_hp)
        self.hp = self.max_hp
        self.max_speed = float(archetype.max_speed)
        self.acceleration = float(archetype.acceleration)
        self.alive = True
        self.damage_flash_timer = 0.0
        self.previous_player_x = None
        self.estimated_player_vx = 0.0

        local_hitbox = self._build_local_hitbox()
        self.hitbox_offset_x = local_hitbox.x
        self.hitbox_offset_y = local_hitbox.y
        self.hitbox = local_hitbox.copy()
        self.hitbox.x += round(self.x)
        self.hitbox.y += round(self.y)
        self.movement = EnemyMovement(self)
        self.brain = EnemyBrain(self, role=role)
        self.weapons = EnemyWeaponSystem(self, torpedo_image=torpedo_image)

    @property
    def centerx(self):
        return self.x + self.width * 0.5

    @property
    def centery(self):
        return self.y + self.height * 0.5

    def _build_local_hitbox(self):
        # Use alpha bounds once at construction time; this is much cheaper than
        # scanning pixels each frame and is accurate enough for these sprites.
        mask = pygame.mask.from_surface(self.image)
        rects = mask.get_bounding_rects()
        if rects:
            local = rects[0]
            for rect in rects[1:]:
                local.union_ip(rect)
        else:
            local = self.image.get_rect()
        return local.copy()

    def update_hitbox(self):
        self.hitbox.x = round(self.x + self.hitbox_offset_x)
        self.hitbox.y = round(self.y + self.hitbox_offset_y)

    def update(self, dt, player, player_projectiles, nearby_enemies, difficulty_scale=1.0):
        if not self.alive:
            return []

        if self.previous_player_x is not None and dt > 0:
            instantaneous = (player.hitbox.centerx - self.previous_player_x) / dt
            self.estimated_player_vx = self.estimated_player_vx * 0.78 + instantaneous * 0.22
        self.previous_player_x = player.hitbox.centerx

        target_x, target_y, dodge_velocity = self.brain.update(
            dt, player, player_projectiles, nearby_enemies, difficulty_scale
        )
        self.movement.update(dt, target_x, target_y, dodge_velocity)
        self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        return self.weapons.update(dt, player, difficulty_scale)

    def take_damage(self, amount):
        effective = max(1, int(round(float(amount) * (1.0 - self.archetype.armor_resistance))))
        self.hp -= effective
        self.damage_flash_timer = 0.11
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return not self.alive

    def score_value(self):
        low, high = self.archetype.bonus_score
        return self.archetype.base_score + random.randint(low, high)

    def resize(self, width, height):
        old_width = max(1, self.window_width)
        old_height = max(1, self.window_height)
        rel_x = self.centerx / old_width
        rel_y = self.centery / old_height
        self.window_width = width
        self.window_height = height
        self.x = rel_x * width - self.width * 0.5
        self.y = rel_y * height - self.height * 0.5
        self.x = max(0.0, min(self.x, width - self.width))
        self.y = max(-self.height * 0.15, min(self.y, height * 0.58 - self.height))
        self.update_hitbox()

    def draw(self, screen, show_hitbox=False):
        screen.blit(self.image, (round(self.x), round(self.y)))
        if self.damage_flash_timer > 0:
            screen.blit(self.flash_image, (round(self.x), round(self.y)))

        # Compact HP bar; elite/heavy enemies are immediately readable.
        bar_width = max(28, int(self.width * 0.75))
        bar_height = 5
        bar_x = int(self.centerx - bar_width / 2)
        bar_y = int(self.y - 9)
        pygame.draw.rect(screen, (45, 45, 55), (bar_x, bar_y, bar_width, bar_height))
        hp_width = int(bar_width * (self.hp / max(1, self.max_hp)))
        pygame.draw.rect(screen, (220, 70, 70), (bar_x, bar_y, hp_width, bar_height))

        if show_hitbox:
            pygame.draw.rect(screen, (255, 80, 80), self.hitbox, 1)
