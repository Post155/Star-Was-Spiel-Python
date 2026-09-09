import sys

import pygame

from game.assets import load_assets, set_window_icon
from game.background import BackgroundManager
from game.constants import (
    ASTEROID_SPAWN_INTERVAL,
    BLACK,
    HEIGHT,
    SCREEN_TITLE,
    WIDTH,
)
from game.enemies import EnemyManager
from game.entities.asteroid import Asteroid
from game.entities.explosion import Explosion
from game.entities.ships import BattleDroid, MillenniumFalcon, Tiefighter, XWing
from game.ui import death_screen, faction_selection, ship_selection


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
set_window_icon()
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

assets = load_assets()
background = BackgroundManager(WIDTH, HEIGHT, assets)

x_wing_img = assets["x_wing_img"]
millennium_falcon_img = assets["millennium_falcon_img"]
tiefighter_img = assets["tie_fighter_img"]
battle_droid_img = assets["battle_droid_img"]
rebel_logo_img = assets["rebel_logo_img"]
empire_logo_img = assets["empire_logo_img"]
asteroid_images = assets["asteroid_images"]
torpedo_img = assets["torpedo_img"]
explosion_img = assets["explosion_img"]

font = pygame.font.Font(None, 40)
lightsaber_blue_img = assets.get("lightsaber_blue_img")
lightsaber_red_img = assets.get("lightsaber_red_img")


def draw_lives(screen, lives, faction="rebels", size=24, padding=8):
    """Draw the faction-specific lightsaber sprite as the life indicator."""
    saber_img = lightsaber_blue_img if faction == "rebels" else lightsaber_red_img
    if saber_img is None:
        return

    target_height = max(14, size)
    scale = target_height / saber_img.get_height()
    scaled_width = max(60, int(saber_img.get_width() * scale))
    scaled_saber = pygame.transform.smoothscale(
        saber_img, (scaled_width, target_height)
    )

    start_x = 6
    start_y = 30
    for i in range(lives):
        screen.blit(
            scaled_saber,
            (start_x, start_y + i * (target_height + padding)),
        )


def create_player(ship_choice, width, height):
    """Create the selected player ship."""
    if ship_choice == "xwing":
        return XWing(width, height, x_wing_img, torpedo_img)
    if ship_choice == "milleniumfalcon":
        return MillenniumFalcon(width, height, millennium_falcon_img, torpedo_img)
    if ship_choice == "tiefighter":
        return Tiefighter(width, height, tiefighter_img, torpedo_img)
    if ship_choice == "battledroid":
        return BattleDroid(width, height, battle_droid_img, torpedo_img)
    raise ValueError(f"Unbekannte Schiffsauswahl: {ship_choice}")


def faction_for_player(player):
    return "rebels" if isinstance(player, (XWing, MillenniumFalcon)) else "empire"


def create_asteroid(width, height):
    """Create an asteroid using the original animated asteroid system."""
    if not asteroid_images:
        return None

    return Asteroid(width, height, asteroid_images)


def destroy_asteroid(asteroid, explosion_list):
    """Remove an asteroid and create its visual explosion."""
    explosion_list.append(
        Explosion(
            asteroid.x + asteroid.width // 2,
            asteroid.y + asteroid.height // 2,
            asteroid.scale,
            explosion_img,
            asteroid.window_height,
        )
    )


while True:
    faction_choice, WIDTH, HEIGHT = faction_selection(
        screen,
        clock,
        WIDTH,
        HEIGHT,
        rebel_logo_img,
        empire_logo_img,
    )
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    set_window_icon()

    faction_logo_img = (
        rebel_logo_img if faction_choice == "rebels" else empire_logo_img
    )
    ship_choice, WIDTH, HEIGHT = ship_selection(
        screen,
        clock,
        WIDTH,
        HEIGHT,
        faction_choice,
        faction_logo_img,
        x_wing_img,
        millennium_falcon_img,
        tiefighter_img,
        battle_droid_img,
    )
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    set_window_icon()

    spieler = create_player(ship_choice, WIDTH, HEIGHT)
    enemy_manager = EnemyManager(WIDTH, HEIGHT, assets, spieler)

    score = 0
    asteroid_spawn_timer = 0
    laser_list = []
    torpedo_list = []
    asteroid_list = []
    explosion_list = []
    running = True

    try:
        background.notify_score_anchor(score)
    except Exception:
        pass

    while running:
        # The AI system uses seconds, while the original asteroid/player
        # systems remain frame based to preserve their existing game feel.
        dt = min(0.05, clock.tick(60) / 1000.0)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                WIDTH = max(480, event.w)
                HEIGHT = max(360, event.h)
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                set_window_icon()

                spieler.resize(WIDTH, HEIGHT)
                enemy_manager.resize(WIDTH, HEIGHT)
                background.resize(WIDTH, HEIGHT)

                for asteroid in asteroid_list:
                    asteroid.resize(WIDTH, HEIGHT)
                for explosion in explosion_list:
                    explosion.resize(HEIGHT)

            elif event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    spieler.show_hitbox = not spieler.show_hitbox

                # Original quick ship switch/debug controls.
                new_ship_choice = None
                if event.key == pygame.K_1:
                    new_ship_choice = "xwing"
                elif event.key == pygame.K_2:
                    new_ship_choice = "milleniumfalcon"
                elif event.key == pygame.K_3:
                    new_ship_choice = "tiefighter"
                elif event.key == pygame.K_4:
                    new_ship_choice = "battledroid"

                if new_ship_choice is not None:
                    spieler = create_player(new_ship_choice, WIDTH, HEIGHT)
                    laser_list.clear()
                    torpedo_list.clear()
                    enemy_manager.set_player(spieler, clear_existing=True)

                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    new_lasers = spieler.shoot()
                    if new_lasers:
                        laser_list.extend(new_lasers)

                if event.key in (pygame.K_s, pygame.K_DOWN):
                    torpedo = spieler.torpedo()
                    if torpedo:
                        torpedo_list.append(torpedo)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            spieler.move_left()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            spieler.move_right(WIDTH)
        if keys[pygame.K_ESCAPE]:
            running = False

        # ------------------------------------------------------------
        # PLAYER PROJECTILES
        # ------------------------------------------------------------
        for laser in laser_list[:]:
            laser.update()
            if laser.rect.bottom < 0 and laser in laser_list:
                laser_list.remove(laser)

        for current_torpedo in torpedo_list[:]:
            current_torpedo.update()
            if current_torpedo.rect.bottom < 0 and current_torpedo in torpedo_list:
                torpedo_list.remove(current_torpedo)

        # ------------------------------------------------------------
        # ASTEROID SYSTEM
        # Runs independently of the enemy AI system.
        # ------------------------------------------------------------
        difficulty = background.get_current_difficulty()
        system_difficulty = int(difficulty.get("level", 1))

        asteroid_speed_multiplier = float(
            difficulty.get("asteroid_speed_multiplier", 1.0)
        )
        asteroid_interval = max(
            10,
            int(ASTEROID_SPAWN_INTERVAL / max(1.0, asteroid_speed_multiplier)),
        )

        asteroid_spawn_timer += 1
        if asteroid_spawn_timer >= asteroid_interval:
            asteroid = create_asteroid(WIDTH, HEIGHT)
            if asteroid is not None:
                asteroid.speed = max(
                    2,
                    int(asteroid.speed * asteroid_speed_multiplier),
                )
                asteroid_list.append(asteroid)
            asteroid_spawn_timer = 0

        for asteroid in asteroid_list[:]:
            asteroid.update()
            if asteroid.y > HEIGHT:
                asteroid_list.remove(asteroid)

        # Player shots vs. asteroids. This is deliberately handled before the
        # enemy manager so a projectile removed by an asteroid cannot also hit
        # an enemy in the same frame.
        for asteroid in asteroid_list[:]:
            asteroid_rect = asteroid.get_rect()

            hit_projectile = None
            for laser in laser_list[:]:
                if asteroid_rect.colliderect(laser.rect):
                    hit_projectile = laser
                    break

            if hit_projectile is None:
                for current_torpedo in torpedo_list[:]:
                    if asteroid_rect.colliderect(current_torpedo.rect):
                        hit_projectile = current_torpedo
                        break

            if hit_projectile is not None:
                score += asteroid.get_points()
                destroy_asteroid(asteroid, explosion_list)

                if asteroid in asteroid_list:
                    asteroid_list.remove(asteroid)
                if hit_projectile in laser_list:
                    laser_list.remove(hit_projectile)
                if hit_projectile in torpedo_list:
                    torpedo_list.remove(hit_projectile)

        # Asteroids vs. player.
        for asteroid in asteroid_list[:]:
            if asteroid.get_rect().colliderect(spieler.hitbox):
                if getattr(spieler, "is_invulnerable", lambda: False)():
                    continue

                died = spieler.take_damage()
                destroy_asteroid(asteroid, explosion_list)

                if asteroid in asteroid_list:
                    asteroid_list.remove(asteroid)

                if died:
                    running = False
                break

        # ------------------------------------------------------------
        # INTELLIGENT ENEMY SYSTEM
        # Runs in the SAME frame/update as the asteroid system.
        # ------------------------------------------------------------
        enemy_result = enemy_manager.update(
            dt=dt,
            score=score,
            system_difficulty=system_difficulty,
            player_lasers=laser_list,
            player_torpedoes=torpedo_list,
        )
        score += enemy_result.score_delta

        if enemy_result.player_dead or spieler.lives <= 0:
            running = False

        # ------------------------------------------------------------
        # RENDERING
        # ------------------------------------------------------------
        screen.fill(BLACK)
        background.update(score)
        background.draw(screen)

        # Draw enemies and their projectiles.
        enemy_manager.draw(screen, show_hitboxes=spieler.show_hitbox)

        # Draw player.
        spieler.draw(screen)

        # Draw player weapons.
        for laser in laser_list:
            laser.draw(screen)
        for current_torpedo in torpedo_list:
            current_torpedo.draw(screen)

        # Draw asteroids.
        for asteroid in asteroid_list:
            asteroid.draw(screen)

        # Draw asteroid explosions.
        for explosion in explosion_list[:]:
            expired = explosion.update()
            explosion.draw(screen)
            if expired and explosion in explosion_list:
                explosion_list.remove(explosion)

        score_text = font.render(f"Punkte: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        draw_lives(screen, getattr(spieler, "lives", 0), faction_for_player(spieler))

        pygame.display.flip()

    restart = death_screen(screen, clock, score, WIDTH, HEIGHT)
    if not restart:
        break

pygame.quit()
sys.exit()
