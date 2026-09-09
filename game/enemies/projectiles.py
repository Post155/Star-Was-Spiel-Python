"""Projectiles fired by AI enemies."""
from __future__ import annotations

import math
import pygame


class EnemyProjectileBase:
    def __init__(self, x, y, target_x, target_y, speed, damage):
        self.x = float(x)
        self.y = float(y)
        self.damage = int(damage)
        dx = float(target_x) - self.x
        dy = float(target_y) - self.y
        length = max(1.0, math.hypot(dx, dy))
        self.vx = dx / length * speed
        self.vy = dy / length * speed
        self.alive = True
        self.rect = pygame.Rect(0, 0, 1, 1)

    def update(self, dt, width, height):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (round(self.x), round(self.y))
        margin = 100
        if (
            self.rect.right < -margin
            or self.rect.left > width + margin
            or self.rect.bottom < -margin
            or self.rect.top > height + margin
        ):
            self.alive = False


class EnemyLaser(EnemyProjectileBase):
    def __init__(self, x, y, target_x, target_y, damage=1, speed=470.0):
        super().__init__(x, y, target_x, target_y, speed, damage)
        self.rect = pygame.Rect(0, 0, 5, 22)
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, screen):
        # A short bright core plus a wider red glow keeps it readable.
        glow = self.rect.inflate(6, 8)
        pygame.draw.rect(screen, (120, 20, 20), glow, border_radius=3)
        pygame.draw.rect(screen, (255, 70, 45), self.rect, border_radius=2)


class EnemyTorpedo(EnemyProjectileBase):
    def __init__(self, x, y, target_x, target_y, image=None, damage=2, speed=285.0):
        super().__init__(x, y, target_x, target_y, speed, damage)
        self.image = None
        if image is not None:
            scaled = pygame.transform.scale_by(image, 0.42)
            self.image = pygame.transform.rotate(scaled, 180)
            self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))
        else:
            self.rect = pygame.Rect(0, 0, 10, 24)
            self.rect.center = (round(self.x), round(self.y))

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.ellipse(screen, (255, 185, 60), self.rect)
