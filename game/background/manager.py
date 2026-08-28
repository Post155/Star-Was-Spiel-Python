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
        if len(self.visited) >= len(self.order):
            self.visited.clear()
            core = [s for s in self.order if s.id_name == 'CORE WORLDS']
            others = [s for s in self.order if s.id_name != 'CORE WORLDS']
            random.shuffle(others)
            self.order = core + others if core else others
            self.order_index = 0
        self.current_system = self.order[self.order_index]
        self.last_switch_time = pygame.time.get_ticks()
        self.transitioning = False

        self._apply_system_visuals()

    def _apply_system_visuals(self):
        sys = self.current_system
        desired1 = max(50, int((self.width * self.height) / 6000 * sys.star_density))
        desired2 = max(20, int((self.width * self.height) / 12000 * sys.star_density))
        self.layer1 = [Star(self.width, self.height, layer=1, tint=sys.star_tint) for _ in range(desired1)]
        self.layer2 = [Star(self.width, self.height, layer=2, tint=sys.star_tint) for _ in range(desired2)]

        planets, fore, nebula = self._choose_assets_for_system(sys)
        self.planet_images = planets if planets else self._generate_planet_images()
        self.near_images = fore if fore else self.near_images

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

        if self.transitioning:
            now = pygame.time.get_ticks()
            elapsed = now - self.transition_start
            d = self.transition_duration
            if elapsed < d // 2:
                alpha = int(255 * (elapsed / (d / 2)))
            else:
                alpha = int(255 * (1 - ((elapsed - (d / 2)) / (d / 2))))
            alpha = max(0, min(255, alpha))
            self.overlay_surface.set_alpha(alpha)
            screen.blit(self.overlay_surface, (0, 0))

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
