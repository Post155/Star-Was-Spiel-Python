import random
from typing import List, Optional

import pygame

from game.constants import HEIGHT as DEFAULT_HEIGHT
from game.constants import WIDTH as DEFAULT_WIDTH
from game.constants import SYSTEM_SWITCH_POINTS, SYSTEM_SWITCH_TIME_MS

from .objects import ForegroundObject, Planet, Star
from .systems import StarSystem, build_systems


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
        first_system = self.systems[0] if self.systems else None
        others = self.systems[1:] if self.systems else []
        random.shuffle(others)
        if first_system:
            self.order = [first_system] + others
        else:
            self.order = []
        self.order_index = 0
        self.level_index = 0
        self.visited = set()
        self.current_system = self.order[self.order_index]
        self.current_level_name = self.current_system.id_name
        self.planet_spawn_range = (700, 1400)
        self.planet_speed_range = (0.6, 1.6)
        self.planet_linger_range = (1200, 2200)
        self.current_difficulty = self.current_system.difficulty
        self._apply_system_visuals()

        # transition state
        self.transitioning = False
        self.transition_start = 0
        self.transition_duration = 1800
        self.overlay_surface = pygame.Surface((self.width, self.height))
        self.overlay_surface.fill((0, 0, 0))

        try:
            self.font_title = pygame.font.Font(None, 64)
            self.font_sub = pygame.font.Font(None, 36)
        except Exception:
            self.font_title = None
            self.font_sub = None

    def _build_systems(self) -> List[StarSystem]:
        return build_systems(self.assets)

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

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.overlay_surface = pygame.Surface((self.width, self.height))
        self.overlay_surface.fill((0, 0, 0))
        self._init_star_layers()

        for p in self.layer3_planets:
            p.width = width
            p.height = height
        for o in self.layer4_objects:
            o.width = width
            o.height = height

    def _choose_assets_for_system(self, system: StarSystem):
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

    def _planet_spawn_settings(self):
        # One planet per level: keep it simple and deterministic.
        settings = {
            'EARTH': {'max_visible': 1, 'spawn_cooldown': (600, 1200), 'speed_range': (0.6, 1.2), 'linger_range': (1200, 2200)},
            'CORUSCANT': {'max_visible': 1, 'spawn_cooldown': (500, 1000), 'speed_range': (0.7, 1.3), 'linger_range': (1300, 2300)},
            'TATOOINE': {'max_visible': 1, 'spawn_cooldown': (450, 900), 'speed_range': (0.8, 1.4), 'linger_range': (1400, 2400)},
            'HOTH': {'max_visible': 1, 'spawn_cooldown': (500, 1000), 'speed_range': (0.7, 1.3), 'linger_range': (1400, 2400)},
            'ENDOR': {'max_visible': 1, 'spawn_cooldown': (450, 900), 'speed_range': (0.8, 1.5), 'linger_range': (1500, 2500)},
            'MUSTAFAR': {'max_visible': 1, 'spawn_cooldown': (400, 800), 'speed_range': (0.85, 1.55), 'linger_range': (1500, 2600)},
            'KAMINO': {'max_visible': 1, 'spawn_cooldown': (400, 850), 'speed_range': (0.8, 1.4), 'linger_range': (1500, 2500)},
            'SATURN': {'max_visible': 1, 'spawn_cooldown': (550, 1100), 'speed_range': (0.6, 1.2), 'linger_range': (1200, 2200)},
            'PURPLE PLANET': {'max_visible': 1, 'spawn_cooldown': (400, 850), 'speed_range': (0.8, 1.6), 'linger_range': (1500, 2500)},
            'DEATH STAR': {'max_visible': 1, 'spawn_cooldown': (350, 800), 'speed_range': (0.9, 1.7), 'linger_range': (1600, 2600)},
        }
        return settings.get(self.current_system.id_name, {'max_visible': 1, 'spawn_cooldown': (500, 1000), 'speed_range': (0.7, 1.4), 'linger_range': (1300, 2300)})

    def get_current_difficulty(self):
        """Return current sector difficulty values for gameplay tuning."""
        return {
            'level': self.current_difficulty,
            'planet_max_visible': self.planet_max_visible,
            'asteroid_speed_multiplier': self.current_system.asteroid_speed_mul,
            'asteroid_spawn_interval': max(18, int(60 / max(1, self.current_difficulty))),
        }

    def _can_spawn_planet(self, candidate):
        for existing in self.layer3_planets:
            if existing.is_exiting:
                continue
            if candidate.get_rect().colliderect(existing.get_rect()):
                return False
        return True

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
            self.last_score_at_switch = current_score
            self.last_switch_time = now
            self._start_transition()

    def _start_transition(self):
        self.transitioning = True
        self.transition_start = pygame.time.get_ticks()

    def _complete_transition(self):
        self.visited.add(self.current_system.id_name)
        self.order_index = (self.order_index + 1) % len(self.order)
        self.level_index = self.order_index
        if len(self.visited) >= len(self.order):
            self.visited.clear()
            first_system = self.order[0] if self.order else None
            others = self.order[1:] if self.order else []
            random.shuffle(others)
            self.order = ([first_system] if first_system else []) + others
            self.order_index = 0
            self.level_index = 0
        self.current_system = self.order[self.order_index]
        self.current_level_name = self.current_system.id_name
        self.current_difficulty = self.current_system.difficulty
        for planet in self.layer3_planets:
            planet.is_exiting = True
            planet.speed = max(planet.speed, 2.0)
        self.layer4_objects.clear()
        self.planet_spawn_cooldown = 0
        self.foreground_spawn_cooldown = 0
        self.last_switch_time = pygame.time.get_ticks()
        self.transitioning = False

        self._apply_system_visuals()

    def _apply_system_visuals(self):
        sys = self.current_system
        self.current_difficulty = sys.difficulty
        desired1 = max(50, int((self.width * self.height) / 6000 * sys.star_density))
        desired2 = max(20, int((self.width * self.height) / 12000 * sys.star_density))
        self.layer1 = [Star(self.width, self.height, layer=1, tint=sys.star_tint) for _ in range(desired1)]
        self.layer2 = [Star(self.width, self.height, layer=2, tint=sys.star_tint) for _ in range(desired2)]

        planets, fore, nebula = self._choose_assets_for_system(sys)
        self.planet_images = planets if planets else self._generate_planet_images()
        self.near_images = fore if fore else self.near_images

        settings = self._planet_spawn_settings()
        self.planet_max_visible = settings['max_visible']
        self.planet_spawn_range = settings['spawn_cooldown']
        self.planet_speed_range = settings['speed_range']
        self.planet_linger_range = settings['linger_range']

    def notify_score_anchor(self, score: int):
        """Call from game when a system switch happens to anchor score/time tracking."""
        self.last_score_at_switch = score
        self.last_switch_time = pygame.time.get_ticks()

    def update(self, current_score: int = 0):
        self.request_switch_if_needed(current_score)

        now = pygame.time.get_ticks()
        if self.transitioning:
            elapsed = now - self.transition_start
            if elapsed >= (self.transition_duration // 2) and getattr(self, '_swapped', False) is False:
                self._complete_transition()
                self._swapped = True
            if elapsed >= self.transition_duration:
                self.transitioning = False
                self._swapped = False

            for star in self.layer1:
                star.update()
            for star in self.layer2:
                star.update()
            return

        for star in self.layer1:
            star.update()
        for star in self.layer2:
            star.update()

        if self.planet_spawn_cooldown <= 0 and self.planet_images and len(self.layer3_planets) < self.planet_max_visible:
            if random.random() < 0.9:
                planet = Planet(
                    random.choice(self.planet_images),
                    self.width,
                    self.height,
                    speed_range=self.planet_speed_range,
                    linger_range=self.planet_linger_range,
                )
                if self._can_spawn_planet(planet):
                    self.layer3_planets.append(planet)
                    self.planet_spawn_cooldown = random.randint(*self.planet_spawn_range)
                else:
                    self.planet_spawn_cooldown = max(15, min(self.planet_spawn_range))
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

        filter_color = self.current_system.visual_filter
        if filter_color and filter_color != (0, 0, 0, 0):
            filter_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            filter_surface.fill((filter_color[0], filter_color[1], filter_color[2], filter_color[3]))
            screen.blit(filter_surface, (0, 0))

            indicator = pygame.Surface((110, 110), pygame.SRCALPHA)
            pygame.draw.circle(indicator, (filter_color[0], filter_color[1], filter_color[2], 120), (55, 55), 52)
            screen.blit(indicator, (self.width - 120, 20))

    def get_current_system_name(self) -> str:
        return self.current_system.id_name

    def get_current_level_name(self) -> str:
        return self.current_level_name

    def get_current_level_index(self) -> int:
        return self.level_index
