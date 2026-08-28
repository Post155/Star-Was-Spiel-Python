import random

import pygame


class Star:
    def __init__(self, width, height, layer=1, tint=None):
        self.width = width
        self.height = height
        self.layer = layer
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

        # size and speed influenced by layer for parallax
        if layer == 1:
            self.size = random.choice([1, 1, 1, 1])
            self.base_speed = 0.12
            self.brightness_min = 110
            self.brightness_max = 220
        elif layer == 2:
            self.size = random.choice([1, 2, 2, 3])
            self.base_speed = 0.35
            self.brightness_min = 140
            self.brightness_max = 255
        else:
            self.size = random.choice([2, 3, 4])
            self.base_speed = 0.7
            self.brightness_min = 180
            self.brightness_max = 255

        self.speed = self.base_speed * (self.size / 1.5) * (0.6 + random.random())
        brightness = random.randint(self.brightness_min, self.brightness_max)

        if layer == 2 and random.random() < 0.3:
            tint_choice = tint or random.choice([(180, 200, 255), (255, 200, 200)])
            self.color = (
                min(255, int(brightness * tint_choice[0] / 255)),
                min(255, int(brightness * tint_choice[1] / 255)),
                min(255, int(brightness * tint_choice[2] / 255)),
            )
        else:
            self.color = (brightness, brightness, brightness)

        self.twinkle = random.random() < 0.25
        self.brightness_change = random.choice([-1, 1]) if self.twinkle else 0

    def update(self):
        self.y += self.speed
        if self.twinkle:
            step = random.randint(0, 3)
            r = self.color[0] + self.brightness_change * step
            if r > self.brightness_max:
                r = self.brightness_max
                self.brightness_change = -1
            elif r < self.brightness_min:
                r = self.brightness_min
                self.brightness_change = 1
            self.color = (r, r, r)

        if self.y > self.height:
            self.y = -self.size - 2
            self.x = random.uniform(0, self.width)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.size, self.size))


class Planet:
    def __init__(self, image, width, height, speed_range=(0.6, 1.8), scale_range=(0.25, 0.6), linger_range=(900, 1800)):
        self.original = image
        scale = random.uniform(scale_range[0], scale_range[1])
        self.img = pygame.transform.scale(
            self.original,
            (
                max(16, int(self.original.get_width() * scale)),
                max(16, int(self.original.get_height() * scale)),
            ),
        )

        self.width = width
        self.height = height
        self.x = random.uniform(0, max(0, width - self.img.get_width()))
        self.y = -self.img.get_height() - random.randint(0, height // 2)
        self.speed = random.uniform(speed_range[0], speed_range[1])
        self.drift_x = random.uniform(-0.8, 0.8)
        self.linger = random.randint(linger_range[0], linger_range[1])
        self.is_exiting = False

    def update(self):
        if self.is_exiting:
            self.y += self.speed * 2.6
            self.x += self.drift_x * 2.2
            self.linger -= 1
            return

        self.y += self.speed
        self.x += self.drift_x
        self.linger -= 1

    def draw(self, screen):
        screen.blit(self.img, (int(self.x), int(self.y)))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.img.get_width(), self.img.get_height())

    def expired(self):
        return self.y > self.height + self.img.get_height() or self.linger <= 0


class ForegroundObject:
    def __init__(self, image, width, height, silhouette=True):
        self.original = image
        scale = random.uniform(0.5, 1.8)
        self.img = pygame.transform.scale(
            self.original,
            (
                max(6, int(self.original.get_width() * scale)),
                max(6, int(self.original.get_height() * scale)),
            ),
        )
        self.img = self._to_silhouette(self.img) if silhouette else self.img

        self.width = width
        self.height = height
        self.x = random.randint(0, max(0, width - self.img.get_width()))
        self.y = -self.img.get_height()
        self.speed = random.uniform(1.8, 3.5)
        self.drift_x = random.uniform(-0.6, 0.6)

    def _to_silhouette(self, surf):
        try:
            mask = pygame.mask.from_surface(surf)
            s = mask.to_surface(setcolor=(8, 8, 12, 255), unsetcolor=(0, 0, 0, 0))
            return s.convert_alpha()
        except Exception:
            s = surf.copy()
            try:
                s.fill((8, 8, 12, 0), special_flags=pygame.BLEND_RGBA_MULT)
            except Exception:
                s.fill((8, 8, 12))
            return s

    def update(self):
        self.y += self.speed
        self.x += self.drift_x

    def draw(self, screen):
        screen.blit(self.img, (int(self.x), int(self.y)))

    def expired(self):
        return self.y > self.height
