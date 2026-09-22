"""Projectile entities: Laser and Torpedo.

Responsibility:
- Simple update/draw behavior for bullets/torpedoes

Public classes:
- Laser
- Torpedo
"""
import pygame


class Laser:
    """Simple rectangular laser projectile."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 3, 20)
        self.speed = 15

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)


class Torpedo:
    """Image-based torpedo projectile."""

    def __init__(self, x, y, torpedo_img):
        # torpedo_img expected to be a pygame.Surface or None
        if torpedo_img is None:
            # fallback to a small rect if image missing
            self.image = None
            self.rect = pygame.Rect(x, y, 8, 16)
        else:
            self.image = pygame.transform.scale_by(torpedo_img, 0.50)
            self.rect = self.image.get_rect(center=(x + 4, y + 10))
        self.speed = 10

    def update(self):
        if self.image is None:
            self.rect.y -= self.speed
        else:
            self.rect.y -= self.speed

    def draw(self, screen):
        if self.image is None:
            pygame.draw.rect(screen, (200, 200, 0), self.rect)
        else:
            screen.blit(self.image, self.rect)
