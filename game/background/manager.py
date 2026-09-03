import random
from typing import List, Optional

import pygame
import math

from game.constants import HEIGHT as DEFAULT_HEIGHT
from game.constants import WIDTH as DEFAULT_WIDTH
from game.constants import SYSTEM_SWITCH_POINTS, SYSTEM_SWITCH_TIME_MS
from game.constants import HYPERSPACE_DURATION_MS

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

        # System-Reise Gefühl
        self.system_enter_time = pygame.time.get_ticks()

        # Wie lange nach Eintritt keine Planeten erscheinen
        self.system_entry_delay_ms = 10000

        # Wie lange vor einem Wechsel keine neuen Planeten erscheinen
        self.system_exit_delay_ms = 10000

        # Pro System nur ein Planet
        self.planet_spawned_this_system = False

        # transition state
        self.transitioning = False
        self.transition_start = 0
        # use configurable hyperdrive duration (ms)
        self.transition_duration = HYPERSPACE_DURATION_MS
        self.overlay_surface = pygame.Surface((self.width, self.height))
        self.overlay_surface.fill((0, 0, 0))

        # hyperraum background image (optional)
        self.hyper_img = self.assets.get('hyperraum_img') or self.assets.get('hyperraum')
        self._cached_hyper_scaled = None
        # internal phase timings (computed on transition start)
        self._fade_in_ms = 0
        self._hold_ms = 0
        self._fade_out_ms = 0
        # particle seed for visual effects (recreated each transition)
        self._particles = []

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
            'EARTH': {'max_visible': 1, 'spawn_cooldown': (600, 1200), 'speed_range': (0.6, 0.7), 'linger_range': (1200, 2200)},
            'CORUSCANT': {'max_visible': 1, 'spawn_cooldown': (500, 1000), 'speed_range': (0.7, 0.8), 'linger_range': (1300, 2300)},
            'TATOOINE': {'max_visible': 1, 'spawn_cooldown': (450, 900), 'speed_range': (0.8, 0.9), 'linger_range': (1400, 2400)},
            'HOTH': {'max_visible': 1, 'spawn_cooldown': (500, 1000), 'speed_range': (0.7, 0.8), 'linger_range': (1400, 2400)},
            'ENDOR': {'max_visible': 1, 'spawn_cooldown': (450, 900), 'speed_range': (0.8, 0.9), 'linger_range': (1500, 2500)},
            'MUSTAFAR': {'max_visible': 1, 'spawn_cooldown': (400, 800), 'speed_range': (0.85, 0.95), 'linger_range': (1500, 2600)},
            'KAMINO': {'max_visible': 1, 'spawn_cooldown': (400, 850), 'speed_range': (0.8, 0.9), 'linger_range': (1500, 2500)},
            'SATURN': {'max_visible': 1, 'spawn_cooldown': (550, 1100), 'speed_range': (0.6, 0.7), 'linger_range': (1200, 2200)},
            'PURPLE PLANET': {'max_visible': 1, 'spawn_cooldown': (400, 850), 'speed_range': (0.8, 0.9), 'linger_range': (1500, 2500)},
            'DEATH STAR': {'max_visible': 1, 'spawn_cooldown': (350, 800), 'speed_range': (0.9, 1.0), 'linger_range': (1600, 2600)},
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
        self._swapped = False

        self.transition_from = self.current_system

        # Alte Planeten schnell aus dem Bild fliegen lassen
        for planet in self.layer3_planets:
            planet.is_exiting = True

            try:
                planet.speed *= 3.0
            except:
                pass

        next_index = (self.order_index + 1) % len(self.order)
        self.transition_to = self.order[next_index]

        # Zielindex fest speichern
        self.target_order_index = next_index

        from game.constants import GALAXY_MAP_DURATION_MS
        map_dur = int(GALAXY_MAP_DURATION_MS)

        self.phase_durations = [map_dur]
        self.phase_starts = [0]
        self.total_transition_ms = map_dur

        self._particles = []

        self._map_only_mode = True

        self.transition_from_planets = self._get_available_planet_keys(self.transition_from)
        self.transition_to_planets = self._get_available_planet_keys(self.transition_to)

    def _complete_transition(self):

        self.visited.add(self.current_system.id_name)

        # Immer das System verwenden,
        # das auf der Galaxiekarte angezeigt wurde.
        self.order_index = self.target_order_index

        self.current_system = self.transition_to
        self.current_level_name = self.current_system.id_name
        self.current_difficulty = self.current_system.difficulty

        for planet in self.layer3_planets:
            planet.is_exiting = True
            planet.speed = max(planet.speed, 2.0)

        self.layer4_objects.clear()

        self.planet_spawn_cooldown = 0
        self.foreground_spawn_cooldown = 0

        self.last_switch_time = pygame.time.get_ticks()

        self._apply_system_visuals()
        self.planet_spawned_this_system = False
        self.layer3_planets.clear()


    def _get_available_planet_keys(self, system):
        """Return planet keys for the given StarSystem that have loaded assets.

        Uses the loaded assets dict (self.assets) to verify existence. This ensures
        thumbnails and displayed planets match the actual available images.
        """
        if system is None:
            return []
        keys = []
        for k in getattr(system, 'planet_keys', []) or []:
            # try several possible asset key forms
            candidates = [f"{k}_img", k]
            found = False
            for c in candidates:
                if c in self.assets and self.assets.get(c) is not None:
                    keys.append(k)
                    found = True
                    break
            if not found:
                # also try normalized variants (strip common suffixes)
                k2 = k.replace('_planet', '').replace('planet_', '')
                for c in (f"{k2}_img", k2):
                    if c in self.assets and self.assets.get(c) is not None:
                        keys.append(k)
                        break
        return keys

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

        for star in self.layer1:
            star.update()
        for star in self.layer2:
            star.update()

        system_time = pygame.time.get_ticks() - self.system_enter_time

        time_until_switch = (
            self.switch_time_ms -
            (pygame.time.get_ticks() - self.last_switch_time)
        )

        allow_planets = (
            system_time > self.system_entry_delay_ms
            and
            time_until_switch > self.system_exit_delay_ms
        )

        if (
            allow_planets
            and not self.planet_spawned_this_system
            and len(self.layer3_planets) == 0
            and self.planet_images
        ):
            planet = Planet(
                random.choice(self.planet_images),
                self.width,
                self.height,
                speed_range=(0.4, 0.7),
                linger_range=(5000, 7000),
            )

            if self._can_spawn_planet(planet):
                self.layer3_planets.append(planet)
                self.planet_spawned_this_system = True


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
        # base layers
        for star in self.layer1:
            star.draw(screen)
        for star in self.layer2:
            star.draw(screen)

        for planet in self.layer3_planets:
            planet.draw(screen)

        for obj in self.layer4_objects:
            obj.draw(screen)

        # system filter / HUD indicator
        filter_color = self.current_system.visual_filter
        if filter_color and filter_color != (0, 0, 0, 0):
            filter_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            filter_surface.fill((filter_color[0], filter_color[1], filter_color[2], filter_color[3]))
            screen.blit(filter_surface, (0, 0))

            # NOTE: removed top-right indicator circle — it had no functional purpose.

        # If a system transition is in progress, render the simplified Galaxy-Map-only sequence
        if getattr(self, 'transitioning', False):
            now = pygame.time.get_ticks()
            elapsed = now - self.transition_start

            # map-only mode branch
            if getattr(self, '_map_only_mode', False):
                dur = self.phase_durations[0]
                phase_t = min(1.0, max(0.0, elapsed / max(1.0, dur)))

                # near-seamless: dim current scene slightly instead of replacing it
                dim_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                dim_overlay.fill((0, 0, 0, int(180 * (0.6 * phase_t))))
                screen.blit(dim_overlay, (0, 0))

                # simple map: text nodes left and right
                map_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                from_name = getattr(self.transition_from, 'id_name', '')
                to_name = getattr(self.transition_to, 'id_name', '')

                left_pos = (int(self.width * 0.30), int(self.height * 0.45))
                right_pos = (int(self.width * 0.70), int(self.height * 0.45))

                # connection progress (ease)
                def ease(t):
                    return t * t * (3 - 2 * t)
                conn_progress = ease(phase_t)

                # animated connection line drawn progressively
                end_x = left_pos[0] + int((right_pos[0] - left_pos[0]) * conn_progress)
                pygame.draw.line(map_surf, (120, 200, 255, 220), left_pos, (end_x, left_pos[1]), 6)

                # pulsing nodes
                pulse = 1.0 + 0.25 * math.sin(phase_t * math.pi * 2.0)
                pygame.draw.circle(map_surf, (255, 210, 100), left_pos, int(12 * pulse))
                pygame.draw.circle(map_surf, (100, 210, 255), right_pos, int(12 * (0.7 + 0.3 * conn_progress)))

                # labels
                if self.font_title:
                    t1 = self.font_title.render(from_name, True, (220, 220, 220))
                    t2 = self.font_title.render(to_name, True, (220, 220, 220))
                    map_surf.blit(t1, t1.get_rect(center=(left_pos[0], left_pos[1] - 48)))
                    map_surf.blit(t2, t2.get_rect(center=(right_pos[0], right_pos[1] - 48)))

                # show planet thumbnails early so player notices system change
                early_t = 0.35
                if phase_t <= early_t:
                    thumb_alpha = int(255 * ease(min(1.0, phase_t / early_t)))
                    # left system planets (filtered to available assets and captured at transition start)
                    left_keys = getattr(self, 'transition_from_planets', [])
                    for idx, key in enumerate(left_keys[:3]):
                        img = self.assets.get(f"{key}_img") or self.assets.get(key)
                        if img:
                            try:
                                pw = int(min(self.width, self.height) * 0.12)
                                ph = pw
                                thumb = pygame.transform.smoothscale(img, (pw, ph))
                                thumb.set_alpha(thumb_alpha)
                                pos = (left_pos[0] - 100, left_pos[1] - 40 + idx * (ph + 8))
                                map_surf.blit(thumb, thumb.get_rect(center=pos))
                            except Exception:
                                pass
                    # right system planets (filtered to available assets and captured at transition start)
                    right_keys = getattr(self, 'transition_to_planets', [])
                    for idx, key in enumerate(right_keys[:3]):
                        img = self.assets.get(f"{key}_img") or self.assets.get(key)
                        if img:
                            try:
                                pw = int(min(self.width, self.height) * 0.12)
                                ph = pw
                                thumb = pygame.transform.smoothscale(img, (pw, ph))
                                thumb.set_alpha(thumb_alpha)
                                pos = (right_pos[0] + 100, right_pos[1] - 40 + idx * (ph + 8))
                                map_surf.blit(thumb, thumb.get_rect(center=pos))
                            except Exception:
                                pass

                # animate a slow zoom-in to the connection as phase progresses
                zoom = 1.0 + 0.08 * conn_progress
                msw = int(self.width * zoom)
                msh = int(self.height * zoom)
                map_scaled = pygame.transform.smoothscale(map_surf, (msw, msh))
                r = map_scaled.get_rect(center=(self.width // 2, self.height // 2))
                screen.blit(map_scaled, r)

                # overlay text
                if self.font_sub:
                    txt = self.font_sub.render('ZIELSYSTEM ERREICHT', True, (200, 255, 200))
                    txt2 = self.font_sub.render(f'[{to_name}]', True, (240, 240, 255))
                    alpha = int(255 * phase_t)
                    txt.set_alpha(alpha)
                    txt2.set_alpha(alpha)
                    screen.blit(txt, txt.get_rect(center=(self.width // 2, int(self.height * 0.14))))
                    screen.blit(txt2, txt2.get_rect(center=(self.width // 2, int(self.height * 0.18))))

                # subtle particle accents
                for p in list(self._particles):
                    life_ratio = 1.0 - (p['life'] / max(1, p['max_life']))
                    a = int(200 * (0.3 + 0.7 * life_ratio) * phase_t)
                    radius = int(max(1, p['size'] * (0.5 + life_ratio)))

                    if a > 8:
                        s = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                        pygame.draw.circle(
                            s,
                            (180, 220, 255, a),
                            (radius + 2, radius + 2),
                            radius
                        )
                        screen.blit(s, (int(p['x']) - radius, int(p['y']) - radius))

                    p['life'] = max(0, p['life'] - 12)

                # <<< AUSSERHALB DER SCHLEIFE >>>
                if elapsed >= dur:
                    if not self._swapped:
                        self._complete_transition()
                        
                        self._swapped = True

                    self.transitioning = False
                    self._map_only_mode = False

            # otherwise fall back to generic behavior (not used)
            return

        # when not transitioning nothing special to do here
        return

    def get_current_system_name(self) -> str:
        return self.current_system.id_name

    def get_current_level_name(self) -> str:
        return self.current_level_name

    def get_current_level_index(self) -> int:
        return self.level_index
