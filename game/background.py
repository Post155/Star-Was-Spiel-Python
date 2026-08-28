import os
import random
import time
from typing import List, Optional

import pygame

from game.constants import WIDTH as DEFAULT_WIDTH, HEIGHT as DEFAULT_HEIGHT
from game.constants import SYSTEM_SWITCH_POINTS, SYSTEM_SWITCH_TIME_MS


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
    def __init__(self, image, width, height, speed_range=(0.6, 1.8), scale_range=(0.25, 0.6)):
        self.original = image
        # scale planet randomly
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
        # place inside visible horizontal bounds and above screen to drift down
        self.x = random.uniform(0, max(0, width - self.img.get_width()))
        self.y = -self.img.get_height() - random.randint(0, height // 2)
        self.speed = random.uniform(speed_range[0], speed_range[1])
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


class StarSystem:
    """Configuration holder for a star system/sector."""

    def __init__(self, id_name: str, display_lines: List[str], planet_keys: List[str] = None, foreground_keys: List[str] = None,
                 star_tint=None, star_density=1.0, asteroid_speed_mul=1.0, nebula_keys: List[str] = None,
                 extra_flags: dict = None):
        self.id_name = id_name
        self.display_lines = display_lines
        self.planet_keys = planet_keys or []
        self.foreground_keys = foreground_keys or []
        self.nebula_keys = nebula_keys or []
        self.star_tint = star_tint
        self.star_density = star_density
        self.asteroid_speed_mul = asteroid_speed_mul
        self.extra_flags = extra_flags or {}


class BackgroundManager:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, assets: Optional[dict] = None,
                 switch_points: int = SYSTEM_SWITCH_POINTS, switch_time_ms: int = SYSTEM_SWITCH_TIME_MS):
        self.width = width
        self.height = height
        self.assets = assets or {}

        # base star layers
        self.layer1: List[Star] = []
        self.layer2: List[Star] = []
        self._init_star_layers()

        # dynamic objects
        self.layer3_planets: List[Planet] = []
        self.layer4_objects: List[ForegroundObject] = []

        # available planet images
        self.planet_images = assets.get('planet_images', []) if assets else []
        if not self.planet_images:
            self.planet_images = self._generate_planet_images()

        # near/fgn objects (asteroids etc.)
        self.near_images = assets.get('asteroid_images', []) if assets else []

        # spawn cooldowns
        self.planet_spawn_cooldown = 0
        self.foreground_spawn_cooldown = 0
        self.planet_max_visible = 1

        # system switching
        self.switch_points = switch_points
        self.switch_time_ms = switch_time_ms
        self.last_switch_time = pygame.time.get_ticks()
        self.last_score_at_switch = 0

        # define systems
        self.systems = self._build_systems()
        # ensure CORE WORLDS start first, then shuffled others
        core = next((s for s in self.systems if s.id_name == 'CORE WORLDS'), None)
        others = [s for s in self.systems if s.id_name != 'CORE WORLDS']
        random.shuffle(others)
        if core:
            self.order = [core] + others
        else:
            self.order = others
        self.order_index = 0
        self.visited = set()
        self.current_system = self.order[self.order_index]

        # transition state
        self.transitioning = False
        self.transition_start = 0
        self.transition_duration = 1800  # ms total (fade out -> swap -> fade in)
        self.overlay_surface = pygame.Surface((self.width, self.height))
        self.overlay_surface.fill((0, 0, 0))

        # precompute fonts for overlay text
        try:
            self.font_title = pygame.font.Font(None, 64)
            self.font_sub = pygame.font.Font(None, 36)
        except Exception:
            self.font_title = None
            self.font_sub = None

    def _init_star_layers(self):
        desired1 = max(80, int((self.width * self.height) / 6000))
        desired2 = max(35, int((self.width * self.height) / 12000))
        self.layer1 = [Star(self.width, self.height, layer=1) for _ in range(desired1)]
        self.layer2 = [Star(self.width, self.height, layer=2) for _ in range(desired2)]

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

    def _build_systems(self) -> List[StarSystem]:
        # Build systems from specification. Assets are optional.
        a = self.assets
        systems = [
            StarSystem(
                'CORE WORLDS',
                ['SYSTEMWECHSEL', 'CORE WORLDS'],
                planet_keys=['earth', 'coruscant', 'satellites'],
                foreground_keys=[],
                star_tint=None,
                star_density=1.0,
                asteroid_speed_mul=1.0,
            ),
            StarSystem(
                'TATOOINE',
                ['WARNUNG', 'TATOOINE-SEKTOR ERREICHT'],
                planet_keys=['tatooine_planet'],
                foreground_keys=['sun_1', 'sun_2'],
                star_tint=(255, 230, 160),
                star_density=0.9,
                asteroid_speed_mul=1.25,
                nebula_keys=['gelber_nebel'],
            ),
            StarSystem(
                'HOTH',
                ['WARNUNG', 'HOTH-SEKTOR ERREICHT'],
                planet_keys=['hoth_planet'],
                star_tint=(200, 220, 255),
                star_density=1.1,
                asteroid_speed_mul=0.95,
                nebula_keys=['blue_nebula'],
            ),
            StarSystem(
                'ENDOR',
                ['WARNUNG', 'ENDOR-SEKTOR ERREICHT'],
                planet_keys=['endor', 'forest_moon'],
                star_tint=(180, 230, 180),
                star_density=1.3,
                asteroid_speed_mul=1.0,
                extra_flags={'more_enemies': True},
            ),
            StarSystem(
                'DEATH STAR SECTOR',
                ['WARNUNG', 'IMPERIALER RAUM'],
                planet_keys=['death_star', 'imperial_station', 'star_destroyer'],
                star_tint=(120, 120, 120),
                star_density=0.6,
                asteroid_speed_mul=0.8,
                extra_flags={'imperial_presence': True},
            ),
            StarSystem(
                'NEBULA',
                ['WARNUNG', 'NEBELSEKTOR ERREICHT'],
                nebula_keys=['nebula_red', 'nebula_blue', 'nebula_purple'],
                star_tint=None,
                star_density=1.0,
                asteroid_speed_mul=0.9,
            ),
            StarSystem(
                'KRIEGSGEBIET',
                ['WARNUNG', 'AKTIVE KRIEGSZONE'],
                foreground_keys=['star_destroyer', 'xwing_squadron', 'tie_fighter', 'battle_explosion'],
                star_tint=None,
                star_density=0.8,
                asteroid_speed_mul=1.0,
                extra_flags={'battle': True},
            ),
        ]
        return systems

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.overlay_surface = pygame.Surface((self.width, self.height))
        self.overlay_surface.fill((0, 0, 0))
        self._init_star_layers()

        # resize planets/foreground lists conservatively
        for p in self.layer3_planets:
            p.width = width
            p.height = height
        for o in self.layer4_objects:
            o.width = width
            o.height = height

    def _choose_assets_for_system(self, system: StarSystem):
        # gather images by keys defined in system
        planets = []
        for key in system.planet_keys:
            img = self.assets.get(f'{key}_img')
            if img:
                planets.append(img)
        if not planets:
            planets = self.planet_images

        fore = []
        for key in system.foreground_keys:
            img = self.assets.get(f'{key}_img')
            if img:
                fore.append(img)

        nebula = []
        for key in system.nebula_keys:
            img = self.assets.get(f'{key}_img')
            if img:
                nebula.append(img)

        return planets, fore, nebula

    def request_switch_if_needed(self, current_score: int = 0):
        """Check timers / score and start a transition when threshold reached.

        Anchors the current score at the moment the transition is started so the
        next threshold is evaluated relative to that.
        """
        now = pygame.time.get_ticks()
        time_elapsed = now - self.last_switch_time
        score_diff = current_score - self.last_score_at_switch

        if self.transitioning:
            return

        if score_diff >= self.switch_points or time_elapsed >= self.switch_time_ms:
            # anchor the score/time now so repeated checks don't immediately re-trigger
            self.last_score_at_switch = current_score
            self.last_switch_time = now
            self._start_transition()

    def _start_transition(self):
        self.transitioning = True
        self.transition_start = pygame.time.get_ticks()

    def _complete_transition(self):
        # advance order, wrap and reshuffle when all visited
        self.visited.add(self.current_system.id_name)
        self.order_index = (self.order_index + 1) % len(self.order)
        if len(self.visited) >= len(self.order):
            # reset visited and reshuffle non-core systems
            self.visited.clear()
            core = [s for s in self.order if s.id_name == 'CORE WORLDS']
            others = [s for s in self.order if s.id_name != 'CORE WORLDS']
            random.shuffle(others)
            self.order = core + others if core else others
            self.order_index = 0
        self.current_system = self.order[self.order_index]
        self.last_switch_time = pygame.time.get_ticks()
        # reset score anchor - caller (game) should update last_score_at_switch via notify_score
        self.transitioning = False

        # refresh star layers to reflect new tint and density
        self._apply_system_visuals()

    def _apply_system_visuals(self):
        sys = self.current_system
        # adjust star density by regenerating layers with density multiplier
        desired1 = max(50, int((self.width * self.height) / 6000 * sys.star_density))
        desired2 = max(20, int((self.width * self.height) / 12000 * sys.star_density))
        self.layer1 = [Star(self.width, self.height, layer=1, tint=sys.star_tint) for _ in range(desired1)]
        self.layer2 = [Star(self.width, self.height, layer=2, tint=sys.star_tint) for _ in range(desired2)]

        # planetary assets selection updated
        planets, fore, nebula = self._choose_assets_for_system(sys)
        self.planet_images = planets if planets else self._generate_planet_images()
        self.near_images = fore if fore else self.near_images

        # planet spawn behavior
        if sys.id_name == 'CORE WORLDS':
            self.planet_max_visible = 1
        elif sys.id_name == 'ENDOR':
            self.planet_max_visible = 2
        else:
            self.planet_max_visible = 1

    def notify_score_anchor(self, score: int):
        """Call from game when a system switch happens to anchor score/time tracking."""
        self.last_score_at_switch = score
        self.last_switch_time = pygame.time.get_ticks()

    def update(self, current_score: int = 0):
        # allow external triggering via score/time
        self.request_switch_if_needed(current_score)

        now = pygame.time.get_ticks()
        if self.transitioning:
            elapsed = now - self.transition_start
            # when elapsed reaches half duration -> swap in middle of fade
            if elapsed >= (self.transition_duration // 2) and getattr(self, '_swapped', False) is False:
                # perform system swap while screen is fully covered
                self._complete_transition()
                self._swapped = True
            # if transition fully done, clear swap flag
            if elapsed >= self.transition_duration:
                self.transitioning = False
                self._swapped = False

            # while transitioning, keep updating stars for subtle motion
            for star in self.layer1:
                star.update()
            for star in self.layer2:
                star.update()
            return

        # normal updates
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
        # draw base layers
        for star in self.layer1:
            star.draw(screen)
        for star in self.layer2:
            star.draw(screen)

        for planet in self.layer3_planets:
            planet.draw(screen)

        for obj in self.layer4_objects:
            obj.draw(screen)

        # draw transition overlay if active
        if self.transitioning:
            now = pygame.time.get_ticks()
            elapsed = now - self.transition_start
            d = self.transition_duration
            # alpha: 0 -> 255 -> 0
            if elapsed < d // 2:
                # fade to black
                alpha = int(255 * (elapsed / (d / 2)))
            else:
                # fade back
                alpha = int(255 * (1 - ((elapsed - (d / 2)) / (d / 2))))
            alpha = max(0, min(255, alpha))
            self.overlay_surface.set_alpha(alpha)
            screen.blit(self.overlay_surface, (0, 0))

            # draw centered text during transition at top of fade-in
            # prefer showing while alpha > ~20 to be visible
            if alpha > 20:
                title = self.current_system.display_lines[0] if self.current_system.display_lines else ''
                subtitle = self.current_system.display_lines[1] if len(self.current_system.display_lines) > 1 else ''
                if self.font_title:
                    title_surf = self.font_title.render(title, True, (255, 255, 255))
                    sub_surf = self.font_sub.render(subtitle, True, (230, 230, 230)) if self.font_sub else None
                    tx = (self.width - title_surf.get_width()) // 2
                    ty = (self.height - title_surf.get_height()) // 2 - 20
                    screen.blit(title_surf, (tx, ty))
                    if sub_surf:
                        sx = (self.width - sub_surf.get_width()) // 2
                        screen.blit(sub_surf, (sx, ty + title_surf.get_height() + 6))

    def get_current_system_name(self) -> str:
        return self.current_system.id_name
