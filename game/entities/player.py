"""Player base class and hitbox utility.

Responsibility:
- Represent a player-controlled ship with movement, lives and invulnerability
- Provide accurate hitbox calculation based on sprite alpha

Public classes:
- Player (preferred English name)
- Spieler (alias kept for compatibility with older code)
"""
import pygame

from game.constants import PLAYER_BASE_SPEED


class Player:
    """Base player ship class.

    This class encapsulates image handling, position, movement, lives,
    invulnerability and precise hitbox calculation from sprite alpha channel.
    """

    def __init__(self, image, window_width, window_height, scale):
        self.show_hitbox = False

        self.image = pygame.transform.scale_by(image, scale)
        self.width, self.height = self.image.get_size()

        self.x = (window_width // 2 - self.width // 2)
        self.y = (window_height - self.height - 20)

        self.speed = PLAYER_BASE_SPEED

        # Lives and invulnerability
        self.lives = 3
        self.invulnerable_until = 0  # pygame.time.get_ticks() value until which player is invulnerable
        self.invulnerable_duration_ms = 2000  # 2 seconds of invulnerability after a hit
        self.invulnerable_blink_interval = 200  # ms blink interval while invulnerable

        hitbox_rect = self._calculate_alpha_hitbox()
        self.hitbox_offset_x = int(round(hitbox_rect.x))
        self.hitbox_offset_y = int(round(hitbox_rect.y))
        self.hitbox = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            int(round(hitbox_rect.width)),
            int(round(hitbox_rect.height)),
        )

    def _calculate_alpha_hitbox(self):
        """Calculate a tight hitbox based on alpha channel of the sprite.

        Returns a pygame.Rect in local-sprite coordinates (x,y,width,height).
        """
        width, height = self.image.get_size()
        pixel_data = pygame.image.tostring(self.image, "RGBA", False)
        min_x = width
        min_y = height
        max_x = -1
        max_y = -1

        for y in range(height):
            row_offset = y * width * 4
            for x in range(width):
                alpha_index = row_offset + x * 4 + 3
                if pixel_data[alpha_index] > 0:
                    if x < min_x:
                        min_x = x
                    if y < min_y:
                        min_y = y
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y

        if max_x < 0:
            return pygame.Rect(0, 0, 0, 0)

        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def update_hitbox(self):
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y

    def is_invulnerable(self):
        return pygame.time.get_ticks() < getattr(self, 'invulnerable_until', 0)

    def take_damage(self):
        """Apply damage to the player if not currently invulnerable.
        Returns True if the player has no lives left (dead), False otherwise or when hit was ignored.
        """
        now = pygame.time.get_ticks()
        if now < getattr(self, 'invulnerable_until', 0):
            # still invulnerable, ignore
            return False
        # lose one life and start invulnerability
        self.lives = max(0, self.lives - 1)
        self.invulnerable_until = now + getattr(self, 'invulnerable_duration_ms', 2000)
        return self.lives <= 0

    def resize(self, window_width, window_height):
        self.y = window_height - self.height - 20
        self.x = max(0, min(self.x, window_width - self.width))
        self.update_hitbox()

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0
        self.update_hitbox()

    def move_right(self, window_width):
        self.x += self.speed
        if self.x > window_width - self.width:
            self.x = window_width - self.width
        self.update_hitbox()

    def draw(self, screen):
        # If currently invulnerable, blink the ship by skipping draws on alternate intervals
        if self.is_invulnerable():
            blink_on = (pygame.time.get_ticks() // self.invulnerable_blink_interval) % 2 == 0
            if blink_on:
                screen.blit(self.image, (self.x, self.y))
        else:
            screen.blit(self.image, (self.x, self.y))

        if self.show_hitbox:
            pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


# Compatibility alias for existing code
Spieler = Player
