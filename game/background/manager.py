import random
from typing import List, Optional

import pygame
import math

from game.constants import HEIGHT as DEFAULT_HEIGHT
from game.constants import WIDTH as DEFAULT_WIDTH
from game.constants import SYSTEM_SWITCH_POINTS, SYSTEM_SWITCH_TIME_MS
from game.constants import HYPERSPACE_DURATION_MS

from .objects import ForegroundObject
from .planet_manager import PlanetManager
from .starfield import StarField
from .system_manager import SystemManager
from .transition_manager import TransitionManager


class BackgroundManager:
    """Coordinator that composes smaller background subsystems.

    Responsibilities:
    - Coordinate StarField, PlanetManager, TransitionManager and SystemManager
    - Keep a small orchestration surface and expose the previous public API
    """

    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT, assets: Optional[dict] = None,
                 switch_points: int = SYSTEM_SWITCH_POINTS, switch_time_ms: int = SYSTEM_SWITCH_TIME_MS) -> None:
        self.width = width
        self.height = height
        self.assets = assets or {}

        # subsystems
        self.systems = SystemManager(self.assets)
        current = self.systems.current_system()
        density = getattr(current, 'star_density', 1.0) if current else 1.0
        tint = getattr(current, 'star_tint', None) if current else None
        self.starfield = StarField(self.width, self.height, density=density, tint=tint)
        self.planet_manager = PlanetManager(self.width, self.height, self.assets)
        self.transition_manager = TransitionManager(self.width, self.height, self.assets)

        # foreground objects
        self.layer4_objects: List[ForegroundObject] = []
        self.near_images = self.assets.get('asteroid_images', []) if self.assets else []
        self.foreground_spawn_cooldown = 0

        # switching/timers
        self.switch_points = switch_points
        self.switch_time_ms = switch_time_ms
        self.last_switch_time = pygame.time.get_ticks()
        self.last_score_at_switch = 0

        # system entry/exit delays
        self.system_enter_time = pygame.time.get_ticks()
        self.system_entry_delay_ms = 10000
        self.system_exit_delay_ms = 10000

        # transition config
        self.transition_duration = HYPERSPACE_DURATION_MS

        # fonts
        try:
            self.font_title = pygame.font.Font(None, 64)
            self.font_sub = pygame.font.Font(None, 36)
        except Exception:
            self.font_title = None
            self.font_sub = None

        # initialize visuals for current system
        self._apply_system_visuals()

    # --- Public API kept for compatibility ---
    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.starfield.resize(width, height)
        self.planet_manager.resize(width, height)
        self.transition_manager.resize(width, height)
        # resize existing foreground objects
        for o in self.layer4_objects:
            o.width = width
            o.height = height

    def notify_score_anchor(self, score: int) -> None:
        self.last_score_at_switch = score
        self.last_switch_time = pygame.time.get_ticks()

    def get_current_difficulty(self):
        return {
            'level': self.systems.get_current_difficulty(),
            'planet_max_visible': self.planet_manager.planet_max_visible,
            'asteroid_speed_multiplier': getattr(self.systems.current_system(), 'asteroid_speed_mul', 1.0),
            'asteroid_spawn_interval': max(18, int(60 / max(1, self.systems.get_current_difficulty()))),
        }

    def get_current_system_name(self) -> str:
        return self.systems.get_current_system_id()

    def get_current_level_name(self) -> str:
        return self.systems.current_level_name()

    def get_current_level_index(self) -> int:
        return self.systems.current_level_index()

    # --- internal helpers ---
    def _apply_system_visuals(self) -> None:
        sys = self.systems.current_system()
        if not sys:
            return
        # star visuals
        self.starfield.set_visuals(density=getattr(sys, 'star_density', 1.0), tint=getattr(sys, 'star_tint', None))

        # choose assets for system
        planets = []
        fore = []
        nebula = []
        for key in getattr(sys, 'planet_keys', []):
            img = self.assets.get(f"{key}_img") or self.assets.get(key)
            if img:
                planets.append(img)
        if not planets:
            # fallback to discovered planets (if any)
            planets = self.assets.get('planet_images', [])[:]

        for key in getattr(sys, 'foreground_keys', []):
            img = self.assets.get(f"{key}_img") or self.assets.get(key)
            if img:
                fore.append(img)
        for key in getattr(sys, 'nebula_keys', []):
            img = self.assets.get(f"{key}_img") or self.assets.get(key)
            if img:
                nebula.append(img)

        self.planet_manager.set_system_planet_settings(planets, 1, (500, 1000), (0.6, 1.6), (1200, 2200))
        if fore:
            self.near_images = fore

    # --- Switching orchestration ---
    def request_switch_if_needed(self, current_score: int = 0) -> None:
        now = pygame.time.get_ticks()
        time_elapsed = now - self.last_switch_time
        score_diff = current_score - self.last_score_at_switch

        if self.transition_manager.is_active():
            return

        if score_diff >= self.switch_points or time_elapsed >= self.switch_time_ms:
            # start transition
            next_idx = self.systems.next_index()
            transition_to = self.systems.target_system()
            transition_from = self.systems.current_system()

            # mark planets to exit quickly
            self.planet_manager.start_exit_all()

            # prepare transition manager
            map_dur = int(getattr(__import__('game.constants', fromlist=['GALAXY_MAP_DURATION_MS']), 'GALAXY_MAP_DURATION_MS'))
            self.transition_manager.transition_from_planets = self.systems.get_available_planet_keys(transition_from, self.assets)
            self.transition_manager.transition_to_planets = self.systems.get_available_planet_keys(transition_to, self.assets)
            self.transition_manager.start_transition(transition_from, transition_to, next_idx, map_dur)

    def _complete_transition(self) -> None:
        # mark visited and advance system index
        self.systems.mark_visited_current()
        self.systems.advance_to_index(self.transition_manager.target_order_index)

        # update visuals and reset planet manager
        self._apply_system_visuals()
        self.planet_manager.clear_all()
        self.layer4_objects.clear()

        self.last_switch_time = pygame.time.get_ticks()
        self.system_enter_time = pygame.time.get_ticks()

    # --- Update / Draw ---
    def update(self, current_score: int = 0) -> None:
        # possibly start transition
        self.request_switch_if_needed(current_score)

        # update stars
        self.starfield.update()

        # decide whether planets are allowed
        system_time = pygame.time.get_ticks() - self.system_enter_time
        time_until_switch = (self.switch_time_ms - (pygame.time.get_ticks() - self.last_switch_time))
        allow_planets = (system_time > self.system_entry_delay_ms) and (time_until_switch > self.system_exit_delay_ms)

        # planets
        self.planet_manager.maybe_spawn(allow_planets)
        self.planet_manager.update()

        # foreground objects
        if self.foreground_spawn_cooldown <= 0 and self.near_images and random.random() < 0.18:
            obj = ForegroundObject(random.choice(self.near_images), self.width, self.height)
            self.layer4_objects.append(obj)
            self.foreground_spawn_cooldown = random.randint(60, 240)
        else:
            self.foreground_spawn_cooldown = max(0, self.foreground_spawn_cooldown - 1)

        for o in self.layer4_objects[:]:
            o.update()
            if o.expired():
                try:
                    self.layer4_objects.remove(o)
                except ValueError:
                    pass

    def draw(self, screen: pygame.Surface) -> None:
        # draw base star layers
        self.starfield.draw(screen)
        # draw planets
        self.planet_manager.draw(screen)
        # draw foreground objects
        for o in self.layer4_objects:
            o.draw(screen)

        # apply system visual filter
        sys = self.systems.current_system()
        filter_color = getattr(sys, 'visual_filter', (0, 0, 0, 0))
        if filter_color and filter_color != (0, 0, 0, 0):
            filter_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            filter_surface.fill((filter_color[0], filter_color[1], filter_color[2], filter_color[3]))
            screen.blit(filter_surface, (0, 0))

        # if transition active, render and complete when done
        if self.transition_manager.is_active():
            completed = self.transition_manager.render(screen, self.assets)
            if completed:
                self._complete_transition()
