"""Asteroid entity module.

Responsibility:
- Represent an asteroid with animated frames, scaling and movement
- Provide collision rect and point value calculation

Public classes:
- Asteroid
"""
import pygame
import random
from game.constants import ASTEROID_SPEED_RANGE


class Asteroid:
    """Asteroid entity.

    Attributes:
        window_width, window_height: current window size
        asteroid_images: list of pygame.Surface frames
        scale: visual scale factor
        x, y: position (top-left)
        speed: vertical speed
    """

    def __init__(self, window_width, window_height, asteroid_images):
        self.window_width = window_width
        self.window_height = window_height
        self.asteroid_images = asteroid_images

        self.scale = random.choice([0.25, 0.5, 0.75, 1.0])

        self.frame = 0
        self.frame_counter = 0
        self.frame_delay = 5

        # scale relative to base height (600)
        self.image = pygame.transform.scale_by(
            self.asteroid_images[self.frame],
            self.scale * (self.window_height / 600)
        )

        self.width, self.height = self.image.get_size()

        self.x = random.randint(
            0,
            max(0, self.window_width - self.width)
        )

        self.y = -self.height

        # asteroid speed is chosen from ASTEROID_SPEED_RANGE in constants.py
        self.speed = random.randint(ASTEROID_SPEED_RANGE[0], ASTEROID_SPEED_RANGE[1])

    def update(self):
        self.y += self.speed

        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame = (self.frame + 1) % len(self.asteroid_images)
            self.image = pygame.transform.scale_by(
                self.asteroid_images[self.frame],
                self.scale * (self.window_height / 600)
            )
            self.width, self.height = self.image.get_size()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(
            self.x + self.width * 0.15,
            self.y + self.height * 0.15,
            self.width * 0.7,
            self.height * 0.7
        )

    def get_points(self):
        if self.scale <= 0.5:
            return 100
        if self.scale <= 0.75:
            return 75
        return 50

    def resize(self, window_width, window_height):
        # keep center while resizing
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        self.window_width = window_width
        self.window_height = window_height

        self.image = pygame.transform.scale_by(
            self.asteroid_images[self.frame],
            self.scale * (self.window_height / 600)
        )

        self.width, self.height = self.image.get_size()

        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2
