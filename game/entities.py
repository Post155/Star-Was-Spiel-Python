import pygame
import random


class Asteroid:
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

        self.speed = random.randint(2, 8)

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


class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 3, 20)
        self.speed = 15

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)


class Torpedo:
    def __init__(self, x, y, torpedo_img):
        self.image = pygame.transform.scale_by(torpedo_img, 0.50)
        self.rect = self.image.get_rect(center=(x + 4, y + 10))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


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


class Spieler:
    def __init__(self, bild, fenster_breite, fenster_hoehe, scale):
        self.show_hitbox = False

        self.image = pygame.transform.scale_by(bild, scale)
        self.width, self.height = self.image.get_size()

        self.x = (fenster_breite // 2 - self.width // 2)
        self.y = (fenster_hoehe - self.height - 20)

        self.speed = 10

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
        screen.blit(self.image, (self.x, self.y))
        if self.show_hitbox:
            pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


class XWing(Spieler):
    def __init__(self, fenster_breite, fenster_hoehe, x_wing_img, torpedo_img=None):
        super().__init__(x_wing_img, fenster_breite, fenster_hoehe, 0.20)
        self.speed = 10
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.18, self.y + self.height * 0.3)
        l2 = Laser(self.x + self.width * 0.82, self.y + self.height * 0.3)
        return [l1, l2]

    def torpedo(self):
        if self.torpedo_img is None:
            return None
        return Torpedo(self.hitbox.centerx, self.y, self.torpedo_img)


class MillenniumFalcon(Spieler):
    def __init__(self, fenster_breite, fenster_hoehe, millennium_falcon_img, torpedo_img=None):
        super().__init__(millennium_falcon_img, fenster_breite, fenster_hoehe, 0.75)
        self.speed = 12
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.43, self.y + self.height * 0.06)
        l2 = Laser(self.x + self.width * 0.58, self.y + self.height * 0.06)
        return [l1, l2]

    def torpedo(self):
        return None
