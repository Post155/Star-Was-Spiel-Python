"""TransitionManager: handle system transitions (galaxy map / hyperdrive animations).

Responsibility:
- Track transition timing and phases
- Render the map-only transition sequence used by the game
- Provide a simple API to start a transition and indicate completion
"""
from typing import List, Optional, Dict
import pygame
import math
import random

from .systems import StarSystem


class TransitionManager:
    def __init__(self, width: int, height: int, assets: Optional[dict] = None) -> None:
        self.width = width
        self.height = height
        self.assets = assets or {}

        self.transitioning: bool = False
        self.transition_start: int = 0
        self.transition_from: Optional[StarSystem] = None
        self.transition_to: Optional[StarSystem] = None
        self.target_order_index: int = 0

        # map-only sequence defaults
        self.phase_durations: List[int] = []
        self.phase_starts: List[int] = []
        self._map_only_mode: bool = True

        self._particles: List[Dict] = []

        try:
            self.font_title = pygame.font.Font(None, 64)
            self.font_sub = pygame.font.Font(None, 36)
        except Exception:
            self.font_title = None
            self.font_sub = None

    def start_transition(self, current_system: StarSystem, target_system: StarSystem, target_index: int, map_duration_ms: int) -> None:
        self.transitioning = True
        self.transition_start = pygame.time.get_ticks()
        self.transition_from = current_system
        self.transition_to = target_system
        self.target_order_index = target_index
        self._swapped = False

        self.phase_durations = [map_duration_ms]
        self.phase_starts = [0]
        self._map_only_mode = True
        self._particles = self._create_particles(60)

    def is_active(self) -> bool:
        return self.transitioning

    def _create_particles(self, count: int):
        ps = []
        for _ in range(count):
            ps.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'life': random.randint(40, 120),
                'max_life': random.randint(60, 160),
                'size': random.uniform(1, 6),
            })
        return ps

    def render(self, screen: pygame.Surface, assets: dict) -> bool:
        """Render the transition sequence. Returns True when transition completed."""
        if not self.transitioning:
            return False

        now = pygame.time.get_ticks()
        elapsed = now - self.transition_start
        # currently only map-only mode implemented (keeps behaviour)
        if self._map_only_mode:
            dur = self.phase_durations[0]
            phase_t = min(1.0, max(0.0, elapsed / max(1.0, dur)))

            dim_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            dim_overlay.fill((0, 0, 0, int(180 * (0.6 * phase_t))))
            screen.blit(dim_overlay, (0, 0))

            map_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            from_name = getattr(self.transition_from, 'id_name', '')
            to_name = getattr(self.transition_to, 'id_name', '')

            left_pos = (int(self.width * 0.30), int(self.height * 0.45))
            right_pos = (int(self.width * 0.70), int(self.height * 0.45))

            def ease(t):
                return t * t * (3 - 2 * t)

            conn_progress = ease(phase_t)
            end_x = left_pos[0] + int((right_pos[0] - left_pos[0]) * conn_progress)
            pygame.draw.line(map_surf, (120, 200, 255, 220), left_pos, (end_x, left_pos[1]), 6)

            pulse = 1.0 + 0.25 * math.sin(phase_t * math.pi * 2.0)
            pygame.draw.circle(map_surf, (255, 210, 100), left_pos, int(12 * pulse))
            pygame.draw.circle(map_surf, (100, 210, 255), right_pos, int(12 * (0.7 + 0.3 * conn_progress)))

            if self.font_title:
                t1 = self.font_title.render(from_name, True, (220, 220, 220))
                t2 = self.font_title.render(to_name, True, (220, 220, 220))
                map_surf.blit(t1, t1.get_rect(center=(left_pos[0], left_pos[1] - 48)))
                map_surf.blit(t2, t2.get_rect(center=(right_pos[0], right_pos[1] - 48)))

            # show thumbnails during early phase
            early_t = 0.35
            if phase_t <= early_t:
                thumb_alpha = int(255 * ease(min(1.0, phase_t / early_t)))
                left_keys = getattr(self, 'transition_from_planets', [])
                for idx, key in enumerate(left_keys[:3]):
                    img = assets.get(f"{key}_img") or assets.get(key)
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
                right_keys = getattr(self, 'transition_to_planets', [])
                for idx, key in enumerate(right_keys[:3]):
                    img = assets.get(f"{key}_img") or assets.get(key)
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

            zoom = 1.0 + 0.08 * conn_progress
            msw = int(self.width * zoom)
            msh = int(self.height * zoom)
            map_scaled = pygame.transform.smoothscale(map_surf, (msw, msh))
            r = map_scaled.get_rect(center=(self.width // 2, self.height // 2))
            screen.blit(map_scaled, r)

            if self.font_sub:
                txt = self.font_sub.render('ZIELSYSTEM ERREICHT', True, (200, 255, 200))
                txt2 = self.font_sub.render(f'[{to_name}]', True, (240, 240, 255))
                alpha = int(255 * phase_t)
                txt.set_alpha(alpha)
                txt2.set_alpha(alpha)
                screen.blit(txt, txt.get_rect(center=(self.width // 2, int(self.height * 0.14))))
                screen.blit(txt2, txt2.get_rect(center=(self.width // 2, int(self.height * 0.18))))

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

            if elapsed >= dur:
                # signal completion to coordinator by returning True
                self.transitioning = False
                return True

        return False

    def capture_transition_planet_lists(self, assets: dict) -> None:
        """Helper to capture planets available for current/from systems prior to rendering.

        This should be set by coordinator when starting a transition so the
        transition display can show thumbnails.
        """
        # coordinator is expected to set attributes transition_from_planets and transition_to_planets
        # Keep empty default
        self.transition_from_planets = getattr(self, 'transition_from_planets', [])
        self.transition_to_planets = getattr(self, 'transition_to_planets', [])

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        # re-create particles for new size
        self._particles = self._create_particles(len(self._particles) or 60)
