import os
import random

import pygame

from game.constants import WIDTH as DEFAULT_WIDTH, HEIGHT as DEFAULT_HEIGHT


class Star:
    def __init__(self, width, height, layer=1):
        self.width = width
        self.height = height
        self.layer = layer
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

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
            tint = random.choice([(180, 200, 255), (255, 200, 200)])
            self.color = (
                min(255, int(brightness * tint[0] / 255)),
                min(255, int(brightness * tint[1] / 255)),
                min(255, int(brightness * tint[2] / 255)),
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
    def __init__(self, image, width, height):
        self.original = image
        # scale planet randomly
        scale = random.uniform(0.25, 0.5)
        self.img = pygame.transform.scale(
            self.original,
            (
                max(16, int(self.original.get_width() * scale)),
                max(16, int(self.original.get_height() * scale)),
            ),
        )

        self.width = width
        self.height = height
        self.x = random.uniform(-self.img.get_width() * 0.75, width + self.img.get_width() * 0.75)
        self.y = -self.img.get_height() - random.randint(0, height // 2)
        self.speed = random.uniform(2.0, 4.6)
        self.drift_x = random.uniform(-0.8, 0.8)
        self.linger = random.randint(280, 680)

    def update(self):
        self.y += self.speed
        self.x += self.drift_x
        self.linger -= 1

    def draw(self, screen):
        screen.blit(self.img, (int(self.x), int(self.y)))

    def expired(self):
        return self.y > self.height + self.img.get_height() or self.linger <= 0


class ForegroundObject:
    def __init__(self, image, width, height):
        self.original = image
        scale = random.uniform(0.5, 1.8)
        self.img = pygame.transform.scale(
            self.original,
            (
                max(6, int(self.original.get_width() * scale)),
                max(6, int(self.original.get_height() * scale)),
            ),
        )
        self.img = self._to_silhouette(self.img)

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


class BackgroundManager:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, assets=None):
        self.width = width
        self.height = height
        self.assets = assets or {}

        self.layer1 = [Star(width, height, layer=1) for _ in range(max(80, int((width * height) / 6000)))]
        self.layer2 = [Star(width, height, layer=2) for _ in range(max(35, int((width * height) / 12000)))]
        self.layer3_planets = []
        self.layer4_objects = []

        self.planet_images = []
        if assets:
            for key in ('planet_blue', 'planet_red', 'planet_green', 'planet_desert'):
                image = assets.get(f'{key}_img')
                if image is not None:
                    self.planet_images.append(image)

        if not self.planet_images:
            planets_dir = os.path.join(os.getcwd(), 'Pixelarts', 'Planets')
            if os.path.isdir(planets_dir):
                for fname in sorted(os.listdir(planets_dir)):
                    path = os.path.join(planets_dir, fname)
                    try:
                        self.planet_images.append(pygame.image.load(path).convert_alpha())
                    except Exception:
                        pass

        if not self.planet_images:
            self.planet_images = self._generate_planet_images()

        self.near_images = []
        if assets and 'asteroid_images' in assets:
            self.near_images = assets['asteroid_images']

        self.planet_spawn_cooldown = 0
        self.foreground_spawn_cooldown = 0
        self.planet_max_visible = 1

    def _generate_planet_images(self):
        palette = [
            (80, 150, 255),
            (255, 110, 90),
            (110, 220, 140),
            (215, 190, 120),
        ]
        images = []
        for color in palette:
            surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (32, 32), 24)
            pygame.draw.circle(surface, (255, 255, 255, 80), (24, 20), 9)
            images.append(surface)
        return images

    def resize(self, width, height):
        self.width = width
        self.height = height

        desired1 = max(80, int((width * height) / 6000))
        desired2 = max(35, int((width * height) / 12000))
        while len(self.layer1) < desired1:
            self.layer1.append(Star(width, height, 1))
        while len(self.layer2) < desired2:
            self.layer2.append(Star(width, height, 2))

    def update(self):
        for star in self.layer1:
            star.update()
        for star in self.layer2:
            star.update()

        if self.planet_spawn_cooldown <= 0 and self.planet_images and len(self.layer3_planets) < self.planet_max_visible:
            if random.random() < 0.35:
                planet = Planet(random.choice(self.planet_images), self.width, self.height)
                self.layer3_planets.append(planet)
                self.planet_spawn_cooldown = random.randint(720, 1700)
        else:
            self.planet_spawn_cooldown = max(0, self.planet_spawn_cooldown - 1)

        for planet in self.layer3_planets[:]:
            planet.update()
            if planet.expired():
                self.layer3_planets.remove(planet)

        if self.foreground_spawn_cooldown <= 0 and self.near_images and random.random() < 0.18:
            obj = ForegroundObject(random.choice(self.near_images), self.width, self.height)
            self.layer4_objects.append(obj)
            self.foreground_spawn_cooldown = random.randint(60, 240)
        else:
            self.foreground_spawn_cooldown = max(0, self.foreground_spawn_cooldown - 1)

        for obj in self.layer4_objects[:]:
            obj.update()
            if obj.expired():
                self.layer4_objects.remove(obj)

    def draw(self, screen):
        for star in self.layer1:
            star.draw(screen)
        for star in self.layer2:
            star.draw(screen)

        for planet in self.layer3_planets:
            planet.draw(screen)

        for obj in self.layer4_objects:
            obj.draw(screen)
