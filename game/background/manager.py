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
        # mark start and record from/to systems for the transition screen
        self.transitioning = True
        self.transition_start = pygame.time.get_ticks()
        self._swapped = False
        # record source system and next target system for display
        self.transition_from = self.current_system
        next_index = (self.order_index + 1) % len(self.order) if self.order else 0
        self.transition_to = self.order[next_index] if self.order else None

        # compute phase durations using min/max constraints so total feels cinematic
        total = max(12000, int(getattr(self, 'transition_duration', 14000)))  # enforce minimum 12s
        # Phase min/max (ms): P1 warning, P2 prep, P3 jump, P4 map, P5 planet
        mins = [2000, 2000, 4000, 2000, 2000]
        maxs = [2000, 3000, 6000, 3000, 4000]
        # ensure total can be distributed within mins/maxs
        total_min = sum(mins)
        total_max = sum(maxs)
        target = min(max(total, total_min), total_max)

        # start with mins, distribute remaining proportionally to (max-min)
        remain = target - total_min
        caps = [maxs[i] - mins[i] for i in range(len(mins))]
        allocated = [mins[i] for i in range(len(mins))]
        if remain > 0:
            cap_sum = sum(caps)
            for i in range(len(allocated)):
                if cap_sum > 0:
                    add = int(round(remain * (caps[i] / cap_sum)))
                else:
                    add = 0
                add = min(add, caps[i])
                allocated[i] += add

            # if rounding left a small remainder, distribute
            leftover = target - sum(allocated)
            idx = 0
            while leftover > 0 and idx < len(allocated):
                if allocated[idx] < maxs[idx]:
                    allocated[idx] += 1
                    leftover -= 1
                idx += 1

        self.phase_durations = allocated  # [p1, p2, p3, p4, p5]
        self.phase_starts = []
        acc = 0
        for d in self.phase_durations:
            self.phase_starts.append(acc)
            acc += d
        self.total_transition_ms = acc

        # prepare cached scaled hyper image for current resolution
        self._cached_hyper_scaled = None

        # generate particles for subtle flashes/flares
        self._particles = []
        for i in range(28):
            px = random.uniform(0, self.width)
            py = random.uniform(0, self.height)
            life = random.randint(int(target * 0.15), int(target * 0.9))
            self._particles.append({'x': px, 'y': py, 'life': life, 'max_life': life, 'size': random.uniform(1.2, 6.8), 'phase': random.choice([2, 3])})

        # camera/visual state
        self._camera_zoom = 0.0
        self._star_stretch = 0.0
        self._hyper_size_checked = False
        self._hyper_too_small = False

    def _complete_transition(self):
        # actually advance the system order and swap current system
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
        # keep transitioning True until the visual duration completes; _swapped handles swap state

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

    def update(self, current_score: int = 0):
        """Main per-frame update for background manager.

        Handles system switch requests, ongoing transition progression, star updates,
        planet/foreground spawning and particle lifetime updates. Non-blocking.
        """
        # Check whether a transition should be started (score/time based)
        now = pygame.time.get_ticks()
        time_elapsed = now - self.last_switch_time
        score_diff = current_score - self.last_score_at_switch
        if not self.transitioning:
            if score_diff >= self.switch_points or time_elapsed >= self.switch_time_ms:
                self.last_score_at_switch = current_score
                self.last_switch_time = now
                self._start_transition()

        # If a cinematic transition is running, update its internal timers and particles
        if self.transitioning:
            elapsed = now - self.transition_start
            # swap to next system at end of phase 3
            if hasattr(self, 'phase_durations'):
                swap_time = sum(self.phase_durations[:3])
                total = self.total_transition_ms
            else:
                swap_time = 2000 + 2000 + 4000
                total = swap_time + 2000 + 2000

            if elapsed >= swap_time and not getattr(self, '_swapped', False):
                self._complete_transition()
                self._swapped = True

            if elapsed >= total:
                self.transitioning = False
                self._swapped = False

            # update star particles and basic star layers even during transition for motion
            for star in self.layer1:
                star.update()
            for star in self.layer2:
                star.update()

            # update simple particle lifetimes
            for p in self._particles:
                p['life'] = max(0, p['life'] - 16)
                # slight drift for phase 3 particles
                if p.get('phase') == 3:
                    p['x'] += random.uniform(-0.6, 0.6)
                    p['y'] += random.uniform(-1.2, 1.2)

            return

        # Normal update when not transitioning
        for star in self.layer1:
            star.update()
        for star in self.layer2:
            star.update()

        # planet spawning
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

    def notify_score_anchor(self, score: int):
        """Call from game when a system switch happens to anchor score/time tracking."""
        self.last_score_at_switch = score
        self.last_switch_time = pygame.time.get_ticks()

    def update(self, current_score: int = 0):
        self.request_switch_if_needed(current_score)

        now = pygame.time.get_ticks()
        if self.transitioning:
            elapsed = now - self.transition_start
            # swap to the next system at the end of the hold phase so the player
            # sees the fully faded-in hyperraum image before the new system loads
            if (elapsed >= (self._fade_in_ms + self._hold_ms)) and getattr(self, '_swapped', False) is False:
                self._complete_transition()
                self._swapped = True
            if elapsed >= self.transition_duration:
                self.transitioning = False
                self._swapped = False

            for star in self.layer1:
                star.update()
            for star in self.layer2:
                star.update()
            # update simple particle lifetimes
            for p in self._particles:
                p['life'] = max(0, p['life'] - 16)
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

            indicator = pygame.Surface((110, 110), pygame.SRCALPHA)
            pygame.draw.circle(indicator, (filter_color[0], filter_color[1], filter_color[2], 120), (55, 55), 52)
            screen.blit(indicator, (self.width - 120, 20))

        # If a system transition is in progress, render a cinematic multi-phase sequence
        if getattr(self, 'transitioning', False):
            now = pygame.time.get_ticks()
            elapsed = now - self.transition_start

            # determine phase durations and starts
            if hasattr(self, 'phase_durations'):
                p = self.phase_durations
                starts = self.phase_starts
                total = self.total_transition_ms
            else:
                # fallback to a sensible single-phase sequence
                p = [2000, 2000, 4000, 2000, 2000]
                starts = [0, p[0], p[0] + p[1], p[0] + p[1] + p[2], p[0] + p[1] + p[2] + p[3]]
                total = sum(p)
                self.phase_durations = p
                self.phase_starts = starts
                self.total_transition_ms = total

            # swap systems at end of Phase 3 so galaxy map shows new system
            swap_time = starts[0] + p[0] + p[1] + p[2]
            if (elapsed >= swap_time) and (not getattr(self, '_swapped', False)):
                self._complete_transition()
                self._swapped = True

            # end of whole sequence
            if elapsed >= total:
                self.transitioning = False
                self._swapped = False

            # current phase index
            phase_idx = 0
            for i in range(len(p)):
                if elapsed >= starts[i] and elapsed < (starts[i] + p[i]):
                    phase_idx = i + 1
                    phase_local = elapsed - starts[i]
                    phase_t = phase_local / max(1.0, p[i])
                    break
            else:
                phase_idx = len(p)
                phase_local = max(0, elapsed - starts[-1])
                phase_t = min(1.0, phase_local / max(1.0, p[-1]))

            title_font = self.font_title
            sub_font = self.font_sub

            # Phase 1: SYSTEMWARNUNG (dim background, large red warning)
            if phase_idx == 1:
                # dim but keep background visible
                dim = int(200 * phase_t)
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, dim))
                screen.blit(overlay, (0, 0))

                # big red warning title with soft pulse
                if title_font:
                    scale = 0.9 + 0.12 * (0.5 - abs(0.5 - phase_t))
                    font_surf = title_font.render('ACHTUNG', True, (220, 50, 50))
                    w, h = font_surf.get_size()
                    s = pygame.transform.smoothscale(font_surf, (max(10, int(w * scale)), max(10, int(h * scale))))
                    rect = s.get_rect(center=(self.width // 2, self.height // 2 - 80))
                    screen.blit(s, rect)

                if sub_font:
                    lines = [
                        'GALAKTISCHE GRENZE ERREICHT',
                        'VERLASSE SYSTEM',
                        f'[{getattr(self.transition_from, "id_name", self.current_system.id_name)}]'
                    ]
                    for i, text in enumerate(lines):
                        t_surf = sub_font.render(text, True, (230, 230, 230))
                        alpha = int(255 * phase_t)
                        t_surf.set_alpha(alpha)
                        r = t_surf.get_rect(center=(self.width // 2, self.height // 2 - 8 + i * 36))
                        screen.blit(t_surf, r)

                return

            # Phase 2: HYPERRAUM VORBEREITUNG (star stretching, charge-up)
            if phase_idx == 2:
                # overlay slight darkening
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, int(160 * (0.15 + 0.85 * phase_t))))
                screen.blit(overlay, (0, 0))

                # stretched starfield effect
                streaks = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                center = (self.width // 2, self.height // 2)
                count = max(40, int(80 * (0.4 + 0.6 * phase_t)))
                max_len = int(max(self.width, self.height) * (0.6 + 1.8 * phase_t))
                for i in range(count):
                    ang = random.random() * math.tau if hasattr(math, 'tau') else random.random() * 2 * math.pi
                    l = random.uniform(max_len * 0.4, max_len)
                    x2 = int(center[0] + l * math.cos(ang))
                    y2 = int(center[1] + l * math.sin(ang))
                    a = int(100 * (0.2 + 0.8 * random.random()) * phase_t)
                    pygame.draw.aaline(streaks, (220, 220, 255, a), center, (x2, y2))
                streaks.set_alpha(200)
                screen.blit(streaks, (0, 0))

                # charging texts
                if sub_font:
                    l1 = sub_font.render('KOORDINATEN BERECHNET', True, (200, 220, 255))
                    l2 = sub_font.render('SPRUNG FREIGEGEBEN', True, (200, 220, 255))
                    a = int(255 * phase_t)
                    l1.set_alpha(a)
                    l2.set_alpha(int(a * (0.8 + 0.2 * math.sin(phase_t * math.pi))))
                    screen.blit(l1, l1.get_rect(center=(self.width // 2, self.height // 2 - 14)))
                    screen.blit(l2, l2.get_rect(center=(self.width // 2, self.height // 2 + 26)))

                # subtle grow of star stretch for use in Phase 3
                self._star_stretch = min(1.0, 0.2 + 1.8 * phase_t)
                return

            # Phase 3: HYPERRAUMSPRUNG (show Hyperraum.png, no rotation, zoom, flashes)
            if phase_idx == 3:
                # compute progress within phase
                phase_progress = phase_t

                # black background fades into hyperraum image (image not rotated)
                if self.hyper_img and self._cached_hyper_scaled is None:
                    try:
                        self._cached_hyper_scaled = pygame.transform.smoothscale(self.hyper_img, (self.width, self.height))
                    except Exception:
                        self._cached_hyper_scaled = self.hyper_img

                # easing helper
                def smoothstep(t):
                    return max(0.0, min(1.0, t * t * (3.0 - 2.0 * t)))

                # image alpha ramps up smoothly
                img_alpha = int(255 * smoothstep(phase_progress))

                # zoom effect: slight zoom-in during phase
                zoom_amount = 0.12  # up to 12% zoom
                zoom = 1.0 + zoom_amount * (0.5 + 0.5 * phase_progress)

                if self._cached_hyper_scaled:
                    try:
                        # scale = smoothscale of cached to implement zoom
                        sw = int(self.width * zoom)
                        sh = int(self.height * zoom)
                        img = pygame.transform.smoothscale(self._cached_hyper_scaled, (sw, sh))
                        img.set_alpha(max(0, min(255, int(255 * (0.6 + 0.4 * phase_progress)))))
                        r = img.get_rect(center=(self.width // 2, self.height // 2))

                        # draw a faint motion-blur by blitting slightly offset translucent copies
                        for i, off in enumerate([0, 2, -2]):
                            tmp = img.copy()
                            tmp.set_alpha(int( max(0, min(255, (180 - i*40) * phase_progress)) ))
                            screen.blit(tmp, (r.x + off, r.y + off))

                        # main blit
                        screen.blit(img, r)
                    except Exception:
                        pass
                else:
                    # fallback star streaks if image missing
                    streak_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    count = max(80, int(200 * phase_progress))
                    center = (self.width // 2, self.height // 2)
                    for i in range(count):
                        angle = random.random() * (2 * math.pi)
                        length = int(max(self.width, self.height) * (0.8 + random.random() * 1.8) * phase_progress)
                        x2 = int(center[0] + length * math.cos(angle))
                        y2 = int(center[1] + length * math.sin(angle))
                        a = int(255 * (0.2 + 0.8 * random.random()) * phase_progress)
                        pygame.draw.aaline(streak_surface, (255, 255, 255, a), center, (x2, y2))
                    screen.blit(streak_surface, (0, 0))

                # light flashes/energy particles
                for p in self._particles:
                    if p['phase'] == 3:
                        life_ratio = 1.0 - max(0.0, min(1.0, p['life'] / p['max_life']))
                        a = int(220 * (0.2 + 0.8 * life_ratio) * phase_progress)
                        radius = int(2 + p['size'] * (1.0 + 4.0 * life_ratio) * phase_progress)
                        s = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                        pygame.draw.circle(s, (255, 250, 220, a), (radius + 2, radius + 2), radius)
                        screen.blit(s, (int(p['x']) - radius, int(p['y']) - radius))

                # HUD: navigation / scanner info
                nav = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                if sub_font:
                    lbl = sub_font.render('HYPERRAUMSPRUNG AKTIV', True, (180, 240, 255))
                    nav.blit(lbl, (40, 40))

                    target = getattr(self.transition_to, 'id_name', self.current_system.id_name)
                    coord = sub_font.render(f'ZIEL: {target}', True, (220, 220, 240))
                    nav.blit(coord, (40, 78))

                    # scanner bar animation
                    bar_w = int(self.width * 0.55)
                    bar_h = 8
                    bx = (self.width - bar_w) // 2
                    by = int(self.height * 0.80)
                    progress_bar = int(bar_w * phase_progress)
                    pygame.draw.rect(nav, (40, 70, 90, 200), (bx, by, bar_w, bar_h))
                    pygame.draw.rect(nav, (120, 220, 255, 220), (bx, by, progress_bar, bar_h))

                screen.blit(nav, (0, 0))
                return

            # Phase 4: GALAXIEKARTE (animated line between systems)
            if phase_idx == 4:
                # simple map: text nodes left and right
                map_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                from_name = getattr(self.transition_from, 'id_name', '')
                to_name = getattr(self.transition_to, 'id_name', '')

                left_pos = (int(self.width * 0.30), int(self.height * 0.45))
                right_pos = (int(self.width * 0.70), int(self.height * 0.45))

                # connection progress
                conn_progress = phase_t
                steps = int(self.width * 0.35 * conn_progress)
                # draw line progressively
                pygame.draw.line(map_surf, (180, 220, 255), left_pos, (left_pos[0] + steps, left_pos[1]), 4)

                # highlight source and target
                pygame.draw.circle(map_surf, (255, 200, 80), left_pos, 12)
                pygame.draw.circle(map_surf, (80, 200, 255), right_pos, 12)

                if title_font:
                    t1 = title_font.render(from_name, True, (220, 220, 220))
                    t2 = title_font.render(to_name, True, (220, 220, 220))
                    map_surf.blit(t1, t1.get_rect(center=(left_pos[0], left_pos[1] - 40)))
                    map_surf.blit(t2, t2.get_rect(center=(right_pos[0], right_pos[1] - 40)))

                # zoom effect: scale map_surf slightly
                zoom = 1.0 + 0.08 * (0.5 + 0.5 * phase_t)
                msw = int(self.width * zoom)
                msh = int(self.height * zoom)
                map_scaled = pygame.transform.smoothscale(map_surf, (msw, msh))
                r = map_scaled.get_rect(center=(self.width // 2, self.height // 2))
                screen.blit(map_scaled, r)

                # text overlay
                if sub_font:
                    txt = sub_font.render('ZIELSYSTEM ERREICHT', True, (200, 255, 200))
                    txt2 = sub_font.render(f'[{to_name}]', True, (240, 240, 255))
                    screen.blit(txt, txt.get_rect(center=(self.width // 2, int(self.height * 0.14))))
                    screen.blit(txt2, txt2.get_rect(center=(self.width // 2, int(self.height * 0.18))))

                return

            # Phase 5: ZIELPLANET (planet preview, gentle bobbing)
            if phase_idx == 5:
                # background fade to system visuals
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 8, 16, int(220 * phase_t)))
                screen.blit(overlay, (0, 0))

                # draw target planet large
                new_sys = self.current_system
                planet_img = None
                if getattr(self, 'transition_to', None):
                    # try to select the first planet key for the target system
                    keys = getattr(self.transition_to, 'planet_keys', [])
                    if keys:
                        img = self.assets.get(f"{keys[0]}_img") or self.assets.get(keys[0])
                        if img:
                            planet_img = img
                # fallback to any planet image
                if not planet_img and self.planet_images:
                    planet_img = random.choice(self.planet_images)

                # scale planet to occupy a good portion
                if planet_img:
                    pw = int(min(self.width, self.height) * 0.45)
                    ph = pw
                    try:
                        scaled = pygame.transform.smoothscale(planet_img, (pw, ph))
                    except Exception:
                        scaled = planet_img
                    # bobbing
                    bob = int(8 * math.sin(elapsed / 180.0))
                    rect = scaled.get_rect(center=(self.width // 2, self.height // 2 - 20 + bob))

                    # subtle glow
                    glow = pygame.Surface((rect.width + 60, rect.height + 60), pygame.SRCALPHA)
                    pygame.draw.ellipse(glow, (30, 120, 200, int(80 * phase_t)), glow.get_rect())
                    screen.blit(glow, glow.get_rect(center=rect.center))

                    screen.blit(scaled, rect)

                # system text
                if title_font:
                    txt1 = title_font.render('SYSTEM BETRETEN', True, (200, 255, 200))
                    screen.blit(txt1, txt1.get_rect(center=(self.width // 2, int(self.height * 0.12))))

                    sysname = getattr(self.transition_to, 'id_name', new_sys.id_name)
                    name_txt = title_font.render(sysname, True, (255, 255, 255))
                    screen.blit(name_txt, name_txt.get_rect(center=(self.width // 2, int(self.height * 0.20))))

                if sub_font:
                    count = len(getattr(self.transition_to, 'planet_keys', [])) if getattr(self, 'transition_to', None) else len(new_sys.planet_keys)
                    txt2 = sub_font.render(f'{count} PLANET ERKANNT', True, (220, 220, 240))
                    screen.blit(txt2, txt2.get_rect(center=(self.width // 2, int(self.height * 0.28))))

                return

            return

        # when not transitioning nothing special to do here
        return

    def get_current_system_name(self) -> str:
        return self.current_system.id_name

    def get_current_level_name(self) -> str:
        return self.current_level_name

    def get_current_level_index(self) -> int:
        return self.level_index
