import random
import os
import pygame

from game.constants import WIDTH as DEFAULT_WIDTH, HEIGHT as DEFAULT_HEIGHT


class Star:
    def __init__(self, width, height, layer=1):
        self.reset(width, height, layer)

    def reset(self, width, height, layer=1):
        self.width = width
        self.height = height
        self.layer = layer

        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

        # size and speed depend on layer (far, mid, near)
        if layer == 1:
            self.size = random.choice([1, 1, 1, 1])
            base_speed = 0.1
            self.brightness_min = 120
            self.brightness_max = 220
        elif layer == 2:
            self.size = random.choice([1, 1, 2, 2, 3])
            base_speed = 0.3
            self.brightness_min = 140
            self.brightness_max = 255
        else:
            self.size = random.choice([2, 3, 4])
            base_speed = 0.6
            self.brightness_min = 180
            self.brightness_max = 255

        # speed scales with size slightly (gives depth feel)
        self.speed = base_speed * (self.size / 1.5) * (0.5 + random.random())

        b = random.randint(self.brightness_min, self.brightness_max)
        # for some mid-layer stars, give slight color tint
        if layer == 2 and random.random() < 0.25:
            tint = random.choice([(180, 200, 255), (255, 200, 200)])
            self.color = (
                min(255, int(b * tint[0] / 255)),
                min(255, int(b * tint[1] / 255)),
                min(255, int(b * tint[2] / 255)),
            )
        else:
            self.color = (b, b, b)

        # twinkle
        self.twinkle = random.random() < 0.25
        self.brightness_change = random.choice([-1, 1]) if self.twinkle else 0

    def update(self):
        self.y += self.speed
        if self.twinkle and self.brightness_change != 0:
            r = self.color[0] + self.brightness_change * random.randint(0, 3)
            if r > self.brightness_max:
                r = self.brightness_max
                self.brightness_change = -1
            elif r < self.brightness_min:
                r = self.brightness_min
                self.brightness_change = 1
            self.color = (r, r, r)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.size, self.size))


class Planet:
    def __init__(self, image, width, height):
        self.original = image
        # scale planet randomly
        scale = random.uniform(1.5, 3.5)
        self.img = pygame.transform.scale(
            self.original,
            (
                max(8, int(self.original.get_width() * scale)),
                max(8, int(self.original.get_height() * scale)),
            ),
        )
        self.w = width
        self.h = height
        self.x = random.randint(-self.img.get_width() // 2, max(0, width - self.img.get_width() // 2))
        self.y = -self.img.get_height() - random.randint(0, height // 3)
        self.speed = random.uniform(0.05, 0.25)
        # linger time to keep visible
        self.linger = random.randint(600, 2400)

    def update(self):
        self.y += self.speed
        self.linger -= 1

    def draw(self, screen):
        screen.blit(self.img, (int(self.x), int(self.y)))

    def expired(self):
        return self.y > self.h or self.linger <= 0


class ForegroundObject:
    """Simple near-object using a surface (e.g., asteroid silhouette)."""

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
        # tint to silhouette (dark)
        self.img = self._to_silhouette(self.img)

        self.w = width
        self.h = height
        self.x = random.randint(0, max(0, width - self.img.get_width()))
        self.y = -self.img.get_height()
        self.speed = random.uniform(0.6, 1.6)

    def _to_silhouette(self, surf):
        s = surf.copy()
        arr = pygame.surfarray.pixels3d(s)
        # darken all pixels (silhouette)
        arr[:, :, :] = (20, 20, 20)
        del arr
        return s

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        screen.blit(self.img, (int(self.x), int(self.y)))

    def expired(self):
        return self.y > self.h


class BackgroundManager:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, assets=None):
        self.width = width
        self.height = height
        self.assets = assets or {}

        # layer populations
        self.layer1 = [Star(width, height, layer=1) for _ in range(max(40, int((width * height) / 8000)))]
        self.layer2 = [Star(width, height, layer=2) for _ in range(max(20, int((width * height) / 16000)))]
        self.layer3_planets = []
        self.layer4_objects = []

        # pre-load possible planet images if provided in assets
        self.planet_images = []
        if assets:
            for k in ('planet_blue', 'planet_red', 'planet_green', 'planet_desert'):
                img = assets.get(k + '_img') if assets.get(k + '_img') is not None else None
                if img:
                    self.planet_images.append(img)

        # fallback: try to load any images in Pixelarts/Planets folder
        planets_dir = os.path.join(os.getcwd(), 'Pixelarts', 'Planets')
        if os.path.isdir(planets_dir):
            for fname in os.listdir(planets_dir):
                fpath = os.path.join(planets_dir, fname)
                try:
                    img = pygame.image.load(fpath).convert_alpha()
                    self.planet_images.append(img)
                except Exception:
                    pass

        # near object candidates: try asteroid frames from assets
        self.near_images = []
        if assets and 'asteroid_images' in assets:
            self.near_images = assets['asteroid_images']

        # control spawn timers
        self.planet_spawn_cooldown = 0
        self.foreground_spawn_cooldown = 0

    def resize(self, width, height):
        self.width = width
        self.height = height
        # optionally repopulate layers to match new area
        desired1 = max(40, int((width * height) / 8000))
        desired2 = max(20, int((width * height) / 16000))
        while len(self.layer1) < desired1:
            self.layer1.append(Star(width, height, 1))
        while len(self.layer2) < desired2:
            self.layer2.append(Star(width, height, 2))

    def update(self):
        # update stars
        for s in self.layer1[:]:
            s.update()
            if s.y > self.height:
                s.reset(self.width, self.height, 1)
                s.y = -s.size
        for s in self.layer2[:]:
            s.update()
            if s.y > self.height:
                s.reset(self.width, self.height, 2)
                s.y = -s.size

        # planets: spawn rarely
        if self.planet_spawn_cooldown <= 0 and self.planet_images and random.randint(1, 4000) == 1:
            img = random.choice(self.planet_images)
            self.layer3_planets.append(Planet(img, self.width, self.height))
            self.planet_spawn_cooldown = random.randint(600, 2400)
        else:
            self.planet_spawn_cooldown = max(0, self.planet_spawn_cooldown - 1)

        for p in self.layer3_planets[:]:
            p.update()
            if p.expired():
                self.layer3_planets.remove(p)

        # foreground objects: more frequent
        if self.foreground_spawn_cooldown <= 0 and self.near_images and random.randint(1, 200) == 1:
            img = random.choice(self.near_images)
            self.layer4_objects.append(ForegroundObject(img, self.width, self.height))
            self.foreground_spawn_cooldown = random.randint(20, 200)
        else:
            self.foreground_spawn_cooldown = max(0, self.foreground_spawn_cooldown - 1)

        for o in self.layer4_objects[:]:
            o.update()
            if o.expired():
                self.layer4_objects.remove(o)

    def draw(self, screen):
        # draw far background first
        for s in self.layer1:
            s.draw(screen)
        for s in self.layer2:
            s.draw(screen)

        # planets behind gameplay but in front of far stars
        for p in self.layer3_planets:
            p.draw(screen)

        # near objects on top of planets but behind player (depending on game layering)
        for o in self.layer4_objects:
            o.draw(screen)


# end of file
