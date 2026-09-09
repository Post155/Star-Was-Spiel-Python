"""Safe optional sound effects for the enemy subsystem."""
from __future__ import annotations

import os
import pygame


class EnemyAudio:
    def __init__(self, explosion_path="Pixelarts/Sounds/explosion.wav"):
        self.explosion_sound = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if os.path.exists(explosion_path):
                self.explosion_sound = pygame.mixer.Sound(explosion_path)
                self.explosion_sound.set_volume(0.42)
        except pygame.error:
            # The game remains playable on PCs/headless systems without audio.
            self.explosion_sound = None

    def play_explosion(self):
        if self.explosion_sound is not None:
            try:
                self.explosion_sound.play()
            except pygame.error:
                pass
