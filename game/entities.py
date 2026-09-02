import pygame
import random
from game.constants import (
    PLAYER_BASE_SPEED,
    SHIP_SPEED_XWING,
    SHIP_SPEED_MILLENNIUM,
    SHIP_SPEED_TIEFIGHTER,
    SHIP_SPEED_BATTLEDROID,
    SHIP_SCALE_XWING,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_BATTLEDROID,
    ASTEROID_SPEED_RANGE,
)

# Adjustable gameplay values are defined in game.constants.py


class Asteroid:
    def __init__(self, window_width, window_height, asteroid_images):
        self.window_width = window_width
        self.window_height = window_height
        self.asteroid_images = asteroid_images

        self.scale = random.choice([0.25, 0.5, 0.75, 1.0])

        self.frame = 0
        self.frame_counter = 0
        self.frame_delay = 5

        # scale relative to base height (600)
        self.image = pygame.transform.scale_by(
            self.asteroid_images[self.frame],
            self.scale * (self.window_height / 600)
        )

        self.width, self.height = self.image.get_size()

        self.x = random.randint(
            0,
            max(0, self.window_width - self.width)
        )

        self.y = -self.height

        # asteroid speed is chosen from ASTEROID_SPEED_RANGE in constants.py
        self.speed = random.randint(ASTEROID_SPEED_RANGE[0], ASTEROID_SPEED_RANGE[1])

        # new fields for AI use: integrity and last_hit_time
        self.integrity = 1.0
        self.last_hit_time = None

    def update(self):
        self.y += self.speed
        # update center position convenience attribute
        self.position = (self.x + self.width / 2, self.y + self.height / 2)

        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame = (self.frame + 1) % len(self.asteroid_images)
            self.image = pygame.transform.scale_by(
                self.asteroid_images[self.frame],
                self.scale * (self.window_height / 600)
            )
            self.width, self.height = self.image.get_size()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(
            self.x + self.width * 0.15,
            self.y + self.height * 0.15,
            self.width * 0.7,
            self.height * 0.7
        )

    def get_points(self):
        if self.scale <= 0.5:
            return 100
        if self.scale <= 0.75:
            return 75
        return 50

    def resize(self, window_width, window_height):
        # keep center while resizing
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        self.window_width = window_width
        self.window_height = window_height

        self.image = pygame.transform.scale_by(
            self.asteroid_images[self.frame],
            self.scale * (self.window_height / 600)
        )

        self.width, self.height = self.image.get_size()

        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2
        # refresh center position
        self.position = (self.x + self.width / 2, self.y + self.height / 2)

class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 3, 20)
        self.speed = 15

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

class Torpedo:
    def __init__(self, x, y, torpedo_img):
        self.image = pygame.transform.scale_by(torpedo_img, 0.50)
        self.rect = self.image.get_rect(center=(x + 4, y + 10))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class EnemyLaser:
    """Projectile fired by enemies. Uses floating position for smoother movement and more precise collision.
    Moves in world-space according to vx, vy (floats).
    """
    def __init__(self, x, y, vx=0.0, vy=6.0, color=(255, 200, 0)):
        # floating position
        self.fx = float(x)
        self.fy = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        # rect anchored to rounded float position
        self.rect = pygame.Rect(int(self.fx) - 2, int(self.fy) - 2, 4, 12)

    def update(self):
        # update float position then sync rect
        self.fx += float(self.vx)
        self.fy += float(self.vy)
        self.rect.x = int(self.fx) - 2
        self.rect.y = int(self.fy) - 2

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Explosion:
    def __init__(self, x, y, asteroid_scale, explosion_img, window_height=None):
        self.x = x
        self.y = y
        self.asteroid_scale = asteroid_scale
        self.explosion_img = explosion_img
        self.window_height = window_height or 600

        self.image = pygame.transform.scale_by(
            self.explosion_img,
            self.asteroid_scale * 0.5
        )

        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.timer = 20

    def resize(self, window_height):
        self.window_height = window_height
        self.image = pygame.transform.scale_by(
            self.explosion_img,
            self.asteroid_scale * 0.5
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.timer -= 1
        return self.timer <= 0  # True when expired

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Spieler:
    def __init__(self, bild, fenster_breite, fenster_hoehe, scale):
        self.show_hitbox = False

        self.image = pygame.transform.scale_by(bild, scale)
        self.width, self.height = self.image.get_size()

        self.x = (fenster_breite // 2 - self.width // 2)
        self.y = (fenster_hoehe - self.height - 20)

        self.speed = PLAYER_BASE_SPEED

        # Lives and invulnerability
        self.lives = 3
        self.invulnerable_until = 0  # pygame.time.get_ticks() value until which player is invulnerable
        self.invulnerable_duration_ms = 2000  # 2 seconds of invulnerability after a hit
        self.invulnerable_blink_interval = 200  # ms blink interval while invulnerable

        hitbox_rect = self._calculate_alpha_hitbox()
        self.hitbox_offset_x = int(round(hitbox_rect.x))
        self.hitbox_offset_y = int(round(hitbox_rect.y))
        self.hitbox = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            int(round(hitbox_rect.width)),
            int(round(hitbox_rect.height)),
        )

    def _calculate_alpha_hitbox(self):
        width, height = self.image.get_size()
        pixel_data = pygame.image.tostring(self.image, "RGBA", False)
        min_x = width
        min_y = height
        max_x = -1
        max_y = -1

        for y in range(height):
            row_offset = y * width * 4
            for x in range(width):
                alpha_index = row_offset + x * 4 + 3
                if pixel_data[alpha_index] > 0:
                    if x < min_x:
                        min_x = x
                    if y < min_y:
                        min_y = y
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y

        if max_x < 0:
            return pygame.Rect(0, 0, 0, 0)

        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def update_hitbox(self):
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y

    def is_invulnerable(self):
        return pygame.time.get_ticks() < getattr(self, 'invulnerable_until', 0)

    def take_damage(self):
        """Apply damage to the player if not currently invulnerable.
        Returns True if the player has no lives left (dead), False otherwise or when hit was ignored.
        """
        now = pygame.time.get_ticks()
        if now < getattr(self, 'invulnerable_until', 0):
            # still invulnerable, ignore
            return False
        # lose one life and start invulnerability
        self.lives = max(0, self.lives - 1)
        self.invulnerable_until = now + getattr(self, 'invulnerable_duration_ms', 2000)
        return self.lives <= 0

    def resize(self, window_width, window_height):
        self.y = window_height - self.height - 20
        self.x = max(0, min(self.x, window_width - self.width))
        self.update_hitbox()

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0
        self.update_hitbox()

    def move_right(self, window_width):
        self.x += self.speed
        if self.x > window_width - self.width:
            self.x = window_width - self.width
        self.update_hitbox()

    def draw(self, screen):
        # If currently invulnerable, blink the ship by skipping draws on alternate intervals
        if self.is_invulnerable():
            blink_on = (pygame.time.get_ticks() // self.invulnerable_blink_interval) % 2 == 0
            if blink_on:
                screen.blit(self.image, (self.x, self.y))
        else:
            screen.blit(self.image, (self.x, self.y))

        if self.show_hitbox:
            pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)

class XWing(Spieler):
    def __init__(self, fenster_breite, fenster_hoehe, x_wing_img, torpedo_img=None):
        super().__init__(x_wing_img, fenster_breite, fenster_hoehe, SHIP_SCALE_XWING)
        self.speed = SHIP_SPEED_XWING
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.18, self.y + self.height * 0.3)
        l2 = Laser(self.x + self.width * 0.82, self.y + self.height * 0.3)
        return [l1, l2]

    def torpedo(self):
        if self.torpedo_img is None:
            return None
        return Torpedo(self.hitbox.centerx, self.y, self.torpedo_img)

class MillenniumFalcon(Spieler):
    def __init__(self, fenster_breite, fenster_hoehe, millennium_falcon_img, torpedo_img=None):
        super().__init__(millennium_falcon_img, fenster_breite, fenster_hoehe, SHIP_SCALE_MILLENNIUM)
        self.speed = SHIP_SPEED_MILLENNIUM
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.43, self.y + self.height * 0.06)
        l2 = Laser(self.x + self.width * 0.58, self.y + self.height * 0.06)
        return [l1, l2]

    def torpedo(self):
        return None

class Tiefighter(Spieler):
    def __init__(self, fenster_breite, fenster_hoehe, tie_fighter_img, torpedo_img=None):
        super().__init__(tie_fighter_img, fenster_breite, fenster_hoehe, SHIP_SCALE_TIEFIGHTER)
        self.speed = SHIP_SPEED_TIEFIGHTER
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.44, self.y + self.height * 0.30)
        l2 = Laser(self.x + self.width * 0.55, self.y + self.height * 0.30)
        return [l1, l2]

    def torpedo(self):
        if self.torpedo_img is None:
            return None
        return Torpedo(self.x + self.width * 0.47, self.y + self.height * 0.12, self.torpedo_img)

class BattleDroid(Spieler):
    def __init__(self, fenster_breite, fenster_hoehe, battle_droid_img, torpedo_img=None):
        super().__init__(battle_droid_img, fenster_breite, fenster_hoehe, SHIP_SCALE_BATTLEDROID)
        self.speed = SHIP_SPEED_BATTLEDROID
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.05, self.y + self.height * 0.01)
        l2 = Laser(self.x + self.width * 0.94, self.y + self.height * 0.01)
        return [l1, l2]

    def torpedo(self):
        return None


# ---------------------------
# Enemy integration (direct integration, no separate API)
# ---------------------------
from game import enemy_ai
from game.constants import ASSET_PATHS


class EnemyManager:
    """
    Spawns and manages EnemyShip instances (uses game.enemy_ai.EnemyShip).
    Preserves existing asteroid logic; spawns ships that correspond to player's chosen ship:
      - XWing -> TIE_FIGHTER
      - MillenniumFalcon -> BATTLE_DROID
    Each enemy has its own personality and stats defined in enemy_ai.DEFAULT_STATS.
    """

    PLAYER_TO_ENEMY = {
        # Keys use the same ship_choice strings produced by StarWarsGame (lowercase)
        'xwing': enemy_ai.ShipType.TIE_FIGHTER,
        # Map the Millennium Falcon selection to a tougher TIE variant for quick start
        'milleniumfalcon': enemy_ai.ShipType.TIE_DEFENDER,
        'tiefighter': enemy_ai.ShipType.TIE_INTERCEPTOR,
        'battledroid': enemy_ai.ShipType.TIE_BOMBER,
        # Fallback mapping when more player types are added
    }

    # Provide mapping from ShipType to asset key in constants.ASSET_PATHS
    SHIPTYPE_TO_ASSET_KEY = {
        enemy_ai.ShipType.TIE_FIGHTER: 'tie_fighter',
        enemy_ai.ShipType.TIE_INTERCEPTOR: 'tie_fighter',
        enemy_ai.ShipType.TIE_BOMBER: 'tie_fighter',
        enemy_ai.ShipType.TIE_DEFENDER: 'tie_fighter',
        enemy_ai.ShipType.ELITE_BOSS: 'tie_fighter',
    }

    def __init__(self, window_width: int, window_height: int, asset_loader=None):
        self.window_width = window_width
        self.window_height = window_height
        self.enemies: list[enemy_ai.EnemyShip] = []
        self.enemy_sprites: dict[int, any] = {}  # instance_id -> pygame.Surface
        self.asset_loader = asset_loader  # function to load images, if None use pygame.image.load
        # AI debug visualization
        self.debug_ai = True
        try:
            self._debug_font = pygame.font.Font(None, 14)
        except Exception:
            self._debug_font = None
        # simple perf stats for update_all (when debug_ai True)
        self._perf_frame = 0
        self._perf_acc_ms = 0.0
        self._perf_report_frames = 120  # report average every N frames when many enemies

    def _load_image_for_ship(self, ship_type: enemy_ai.ShipType):
        key = self.SHIPTYPE_TO_ASSET_KEY.get(ship_type)
        if key is None:
            return None
        path = ASSET_PATHS.get(key)
        if path is None:
            return None
        try:
            if self.asset_loader:
                img = self.asset_loader(path)
            else:
                img = pygame.image.load(path).convert_alpha()
            return img
        except Exception:
            return None

    def spawn_enemy_for_player(self, player_ship_name: str, count: int = 1):
        # Map player ship name to enemy type; default to TIE_FIGHTER
        enemy_type = self.PLAYER_TO_ENEMY.get(player_ship_name, enemy_ai.ShipType.TIE_FIGHTER)
        for _ in range(count):
            # spawn at random x, above screen
            x = random.uniform(0, self.window_width)
            y = -random.uniform(50, 300)
            heading = random.uniform(0, 360)
            # choose personality preset by ship type for more consistent behavior
            if enemy_type == enemy_ai.ShipType.TIE_INTERCEPTOR:
                personality = enemy_ai.Personality.random_variant('aggressive')
            elif enemy_type == enemy_ai.ShipType.TIE_BOMBER:
                personality = enemy_ai.Personality.random_variant('cautious')
            elif enemy_type == enemy_ai.ShipType.TIE_DEFENDER:
                personality = enemy_ai.Personality.random_variant('aggressive')
            else:
                personality = enemy_ai.Personality.random_variant()

            ship = enemy_ai.EnemyShip(enemy_type, position=(x, y), heading=heading, personality=personality)
            # set mode to hybrid by default (utility + optional RL)
            ship.mode = 'hybrid'
            # Configure steering & state presets per ship type for better behavior
            try:
                from game.ai.state_machine import AIState
                # interceptor: aggressive pursuer
                if enemy_type == enemy_ai.ShipType.TIE_INTERCEPTOR and getattr(ship, 'steering', None) is not None:
                    ship.steering.behavior_weights.update({'pursuit': 1.0, 'separation': 0.6, 'obstacle_avoid': 1.0, 'cohesion': 0.2})
                    if getattr(ship, 'state_machine', None) is not None:
                        ship.state_machine.change_state(AIState.ATTACK)
                # bomber: slower, prefers to find a position and drop bombs/take cover
                if enemy_type == enemy_ai.ShipType.TIE_BOMBER and getattr(ship, 'steering', None) is not None:
                    ship.steering.behavior_weights.update({'arrive': 0.7, 'separation': 0.4, 'obstacle_avoid': 1.0, 'cohesion': 0.1})
                    if getattr(ship, 'state_machine', None) is not None:
                        ship.state_machine.change_state(AIState.PATROL)
                # fighter: balanced pursuit + separation
                if enemy_type == enemy_ai.ShipType.TIE_FIGHTER and getattr(ship, 'steering', None) is not None:
                    ship.steering.behavior_weights.update({'pursuit': 0.8, 'separation': 0.7, 'obstacle_avoid': 1.0, 'cohesion': 0.4})
                    if getattr(ship, 'state_machine', None) is not None:
                        ship.state_machine.change_state(AIState.ATTACK)
                # defender: stay near formation, protect others
                if enemy_type == enemy_ai.ShipType.TIE_DEFENDER and getattr(ship, 'steering', None) is not None:
                    ship.steering.behavior_weights.update({'seek': 0.3, 'separation': 0.6, 'cohesion': 0.8, 'obstacle_avoid': 1.0})
                    if getattr(ship, 'state_machine', None) is not None:
                        ship.state_machine.change_state(AIState.GUARD_LEADER)
            except Exception:
                pass

            self.enemies.append(ship)
            # load sprite (if available)
            img = self._load_image_for_ship(enemy_type)
            if img is not None:
                self.enemy_sprites[ship.instance_id] = img

    def update_all(self, dt: float, player_state: dict[str, any], other_world: dict[str, any] = None):
        """
        Update all enemies. Returns a list of projectile dicts created by enemies during their updates.
        Each projectile dict has keys: type, pos (x,y), vel (vx,vy), damage, source_id
        """
        projectiles: list[dict[str, any]] = []
        # other_world can include nearest asteroid distances etc.
        world_state = {'player': player_state}
        if other_world:
            world_state.update(other_world)

        # Build spatial grid for neighbor/asteroid queries to improve performance
        try:
            from game.ai.spatial_grid import SpatialGrid
            grid = SpatialGrid((0, 0, self.window_width, self.window_height), cell_size=300)
            # insert asteroids if provided in other_world
            asteroids = other_world.get('asteroids') if other_world and other_world.get('asteroids') is not None else []
            for a in asteroids:
                pos = getattr(a, 'position', (getattr(a, 'x', 0) + getattr(a, 'width', 0)/2, getattr(a, 'y', 0) + getattr(a, 'height', 0)/2))
                grid.insert(('asteroid', a), pos)
            # insert enemies into grid
            for e in self.enemies:
                grid.insert(('enemy', e), (e.position[0], e.position[1]))
        except Exception:
            grid = None
            asteroids = other_world.get('asteroids') if other_world and other_world.get('asteroids') is not None else []

        # prepare a player_agent proxy for steering functions that expect .position/.velocity
        class _AgentProxy:
            def __init__(self, pos, vel):
                self.position = pos
                self.velocity = vel
        player_agent = _AgentProxy(player_state.get('position'), player_state.get('velocity'))

        # include a simplified player_profile if available
        # profiling start (only when debug_ai and many enemies)
        import time
        start_time = None
        if self.debug_ai and len(self.enemies) > 30:
            start_time = time.perf_counter()

        for e in list(self.enemies):
            # prepare neighbor list from grid
            neighbors = []
            if grid is not None:
                raw = grid.query_radius((e.position[0], e.position[1]), 400)
                for tag_obj, pos in raw:
                    tag, obj = tag_obj
                    if tag == 'enemy' and getattr(obj, 'instance_id', None) != e.instance_id:
                        neighbors.append(obj)
            # build world state for this enemy
            per_enemy_world = dict(world_state)
            per_enemy_world['neighbors'] = neighbors
            per_enemy_world['asteroids'] = asteroids
            per_enemy_world['player_agent'] = player_agent

            e.update(dt, per_enemy_world)
            # collect any projectiles the enemy created
            while getattr(e, 'pending_projectiles', None):
                projectiles.append(e.pending_projectiles.pop(0))
            # remove if off-screen too far below
            if e.position[1] > self.window_height + 500:
                try:
                    self.enemies.remove(e)
                    if e.instance_id in self.enemy_sprites:
                        del self.enemy_sprites[e.instance_id]
                except ValueError:
                    pass

        # profiling end
        if start_time is not None:
            end = time.perf_counter()
            delta_ms = (end - start_time) * 1000.0
            self._perf_frame += 1
            self._perf_acc_ms += delta_ms
            if self._perf_frame >= self._perf_report_frames:
                avg = self._perf_acc_ms / max(1, self._perf_frame)
                print(f"[AI PERF] update_all avg ms over {self._perf_frame} frames: {avg:.2f} ms (enemies={len(self.enemies)})")
                self._perf_frame = 0
                self._perf_acc_ms = 0.0
        return projectiles

    def draw_all(self, screen):
        for e in self.enemies:
            img = self.enemy_sprites.get(e.instance_id)
            if img is not None:
                # scale according to ship type constants if defined
                key = self.SHIPTYPE_TO_ASSET_KEY.get(e.ship_type)
                scale = 0.3
                try:
                    if key and key in ASSET_PATHS:
                        # pick a reasonable default scale from constants if available
                        from game.constants import SHIP_SCALE_TIEFIGHTER
                        scale = SHIP_SCALE_TIEFIGHTER
                except Exception:
                    scale = 0.3
                img_scaled = pygame.transform.scale_by(img, scale)
                rect = img_scaled.get_rect(center=(int(e.position[0]), int(e.position[1])))
                screen.blit(img_scaled, rect)
            else:
                # fallback: draw simple circle
                pygame.draw.circle(screen, (255, 0, 0), (int(e.position[0]), int(e.position[1])), 10)

            # draw collision rect for debugging
            try:
                r = e.get_rect()
                pygame.draw.rect(screen, (0,255,0), r, 1)
                # red highlight if recently hit
                try:
                    now = pygame.time.get_ticks()
                    if getattr(e, '_hit_flash_time', 0) and (now - e._hit_flash_time) < 250:
                        pygame.draw.rect(screen, (255,0,0), r, 3)
                except Exception:
                    pass
            except Exception:
                pass

            # Debug overlays: steering vector, predicted lead point, state label
            if self.debug_ai:
                # steering vector
                try:
                    if getattr(e, 'last_desired_velocity', None) is not None:
                        lv = e.last_desired_velocity
                        sx = int(e.position[0])
                        sy = int(e.position[1])
                        ex = int(sx + lv[0])
                        ey = int(sy + lv[1])
                        pygame.draw.line(screen, (0, 100, 255), (sx, sy), (ex, ey), 2)
                except Exception:
                    pass
                # lead point
                try:
                    if getattr(e, 'last_lead_point', None) is not None:
                        lp = e.last_lead_point
                        pygame.draw.circle(screen, (255, 200, 0), (int(lp[0]), int(lp[1])), 4)
                except Exception:
                    pass
                # state label
                try:
                    st = getattr(e, 'state_machine', None)
                    if st is not None and getattr(st, 'current_enum', None) is not None and self._debug_font is not None:
                        label = self._debug_font.render(st.current_enum.name, True, (255,255,255))
                        screen.blit(label, (int(e.position[0]) + 10, int(e.position[1]) - 10))
                except Exception:
                    pass

    def clear(self):
        self.enemies.clear()
        self.enemy_sprites.clear()
    