"""Explosion visual effect entity.

Responsibility:
- Manage explosion lifetime and rendering

Public classes:
- Explosion
"""
import pygame


class Explosion:
    def __init__(self, x, y, asteroid_scale, explosion_img, window_height=None):
        self.x = x
        self.y = y
        self.asteroid_scale = asteroid_scale
        self.explosion_img = explosion_img
        self.window_height = window_height or 600

        self.image = pygame.transform.scale_by(
            self.explosion_img,
            self.asteroid_scale * 0.5
        )

        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.timer = 20

    def resize(self, window_height):
        self.window_height = window_height
        self.image = pygame.transform.scale_by(
            self.explosion_img,
            self.asteroid_scale * 0.5
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.timer -= 1
        return self.timer <= 0  # True when expired

    def draw(self, screen):
        screen.blit(self.image, self.rect)
