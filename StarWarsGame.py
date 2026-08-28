import os
import sys

import pygame

from game.assets import load_assets, set_window_icon
from game.constants import ASTEROID_SPAWN_INTERVAL, BLACK, HEIGHT, SCREEN_TITLE, WIDTH
from game.entities import Asteroid, BattleDroid, Explosion, MillenniumFalcon, XWing, Tiefighter
from game.ui import death_screen, faction_selection, ship_selection
from game.background import BackgroundManager

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
set_window_icon()
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

assets = load_assets()

background = BackgroundManager(WIDTH, HEIGHT, assets)

x_wing_img = assets['x_wing_img']
millennium_falcon_img = assets['millennium_falcon_img']
tiefighter_img = assets['tie_fighter_img']
battle_droid_img = assets['battle_droid_img']
rebel_logo_img = assets['rebel_logo_img']
empire_logo_img = assets['empire_logo_img']
asteroid_images = assets['asteroid_images']
torpedo_img = assets['torpedo_img']
explosion_img = assets['explosion_img']

font = pygame.font.Font(None, 40)


def draw_lives(screen, lives, size=28, padding=8):
    """Draw simple heart icons for the player's remaining lives at top-left."""
    # small helper to draw a heart-shaped icon onto the main screen
    for i in range(lives):
        x = 10 + i * (size + padding)
        y = 50
        heart = pygame.Surface((size, size), pygame.SRCALPHA)
        r = max(2, size // 4)
        # left circle
        pygame.draw.circle(heart, (255, 0, 0), (r + 1, r + 1), r)
        # right circle
        pygame.draw.circle(heart, (255, 0, 0), (size - r - 1, r + 1), r)
        # bottom triangle/polygon
        pygame.draw.polygon(heart, (255, 0, 0), [(0, r), (size, r), (size // 2, size)])
        screen.blit(heart, (x, y))


while True:
    faction_choice = faction_selection(screen, clock, WIDTH, HEIGHT, rebel_logo_img, empire_logo_img)
    if faction_choice == 'rebels':
        faction_logo_img = rebel_logo_img
    else:
        faction_logo_img = empire_logo_img
    ship_choice = ship_selection(screen, clock, WIDTH, HEIGHT, faction_choice, faction_logo_img, x_wing_img, millennium_falcon_img, tiefighter_img, battle_droid_img)

    if ship_choice == 'xwing':
        spieler = XWing(WIDTH, HEIGHT, x_wing_img, torpedo_img)
    elif ship_choice == 'milleniumfalcon':
        spieler = MillenniumFalcon(WIDTH, HEIGHT, millennium_falcon_img, torpedo_img)
    elif ship_choice == 'tiefighter':
        spieler = Tiefighter(WIDTH, HEIGHT, tiefighter_img, torpedo_img)
    elif ship_choice == 'battledroid':
        spieler = BattleDroid(WIDTH, HEIGHT, battle_droid_img, torpedo_img)

    score = 0
    asteroid_spawn_timer = 0
    laser_list = []
    asteroid_list = []
    torpedo_list = []
    explosion_list = []
    running = True

    # anchor background system timers/score for this run
    try:
        background.notify_score_anchor(score)
    except Exception:
        pass

    while running:
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                WIDTH = event.w
                HEIGHT = event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                set_window_icon()

                if spieler:
                    spieler.resize(WIDTH, HEIGHT)

                for asteroid in asteroid_list:
                    asteroid.resize(WIDTH, HEIGHT)

                for explosion in explosion_list:
                    explosion.resize(HEIGHT)

                # resize background layers to match new window
                background.resize(WIDTH, HEIGHT)

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    spieler.show_hitbox = not spieler.show_hitbox

                if event.key == pygame.K_1:
                    spieler = XWing(WIDTH, HEIGHT, x_wing_img, torpedo_img)
                elif event.key == pygame.K_2:
                    spieler = MillenniumFalcon(WIDTH, HEIGHT, millennium_falcon_img, torpedo_img)
                elif event.key == pygame.K_3:
                    spieler = Tiefighter(WIDTH, HEIGHT, tiefighter_img, torpedo_img)
                elif event.key == pygame.K_4:
                    spieler = BattleDroid(WIDTH, HEIGHT, battle_droid_img, torpedo_img)

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

        for laser in laser_list[:]:
            laser.update()
            if laser.rect.bottom < 0:
                laser_list.remove(laser)

        for current_torpedo in torpedo_list[:]:
            current_torpedo.update()
            if current_torpedo.rect.bottom < 0:
                torpedo_list.remove(current_torpedo)

        asteroid_spawn_timer += 1
        if asteroid_spawn_timer >= ASTEROID_SPAWN_INTERVAL:
            asteroid_list.append(Asteroid(WIDTH, HEIGHT, asteroid_images))
            asteroid_spawn_timer = 0

        for asteroid in asteroid_list[:]:
            asteroid.update()
            if asteroid.y > HEIGHT:
                asteroid_list.remove(asteroid)

        for asteroid in asteroid_list[:]:
            for laser in laser_list[:]:
                if asteroid.get_rect().colliderect(laser.rect):
                    score += int(asteroid.scale * 100)
                    explosion_list.append(
                        Explosion(
                            asteroid.x + asteroid.width // 2,
                            asteroid.y + asteroid.height // 2,
                            asteroid.scale,
                            explosion_img,
                            HEIGHT,
                        )
                    )
                    if asteroid in asteroid_list:
                        asteroid_list.remove(asteroid)
                    if laser in laser_list:
                        laser_list.remove(laser)
                    break

        for asteroid in asteroid_list[:]:
            for current_torpedo in torpedo_list[:]:
                if asteroid.get_rect().colliderect(current_torpedo.rect):
                    score += int(asteroid.scale * 100)
                    explosion_list.append(
                        Explosion(
                            asteroid.x + asteroid.width // 2,
                            asteroid.y + asteroid.height // 2,
                            asteroid.scale,
                            explosion_img,
                            HEIGHT,
                        )
                    )
                    asteroid_list.remove(asteroid)
                    torpedo_list.remove(current_torpedo)
                    break

        for asteroid in asteroid_list[:]:
            if asteroid.get_rect().colliderect(spieler.hitbox):
                # Ignore collision while player is invulnerable
                if getattr(spieler, 'is_invulnerable', lambda: False)():
                    continue

                # Apply damage; take_damage returns True when player has no lives left
                died = spieler.take_damage()

                # spawn explosion at collision point
                explosion_list.append(
                    Explosion(
                        asteroid.x + asteroid.width // 2,
                        asteroid.y + asteroid.height // 2,
                        asteroid.scale,
                        explosion_img,
                        HEIGHT,
                    )
                )

                if asteroid in asteroid_list:
                    asteroid_list.remove(asteroid)

                if died:
                    running = False
                break

        screen.fill(BLACK)
        background.update(score)
        background.draw(screen)
        spieler.draw(screen)

        for laser in laser_list:
            laser.draw(screen)
        for current_torpedo in torpedo_list:
            current_torpedo.draw(screen)
        for asteroid in asteroid_list:
            asteroid.draw(screen)

        for explosion in explosion_list[:]:
            expired = explosion.update()
            explosion.draw(screen)
            if expired and explosion in explosion_list:
                explosion_list.remove(explosion)

        score_text = font.render(f"Punkte: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        # draw hearts for lives
        if spieler:
            draw_lives(screen, getattr(spieler, 'lives', 0))

        pygame.display.flip()
        clock.tick(60)

    restart = death_screen(screen, clock, score, WIDTH, HEIGHT)
    if not restart:
        break

pygame.quit()
sys.exit()
