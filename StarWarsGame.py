import sys

import pygame

from game.assets import load_assets, set_window_icon
from game.background import BackgroundManager
from game.constants import BLACK, HEIGHT, SCREEN_TITLE, WIDTH
from game.enemies import EnemyManager
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
torpedo_img = assets["torpedo_img"]

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
    scaled_saber = pygame.transform.smoothscale(saber_img, (scaled_width, target_height))

    start_x = 6
    start_y = 30
    for i in range(lives):
        screen.blit(scaled_saber, (start_x, start_y + i * (target_height + padding)))


def create_player(ship_choice, width, height):
    """Create the selected player ship while keeping one central mapping."""
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

    faction_logo_img = rebel_logo_img if faction_choice == "rebels" else empire_logo_img
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
    laser_list = []
    torpedo_list = []
    running = True

    # Anchor background system timers/score for this run.
    try:
        background.notify_score_anchor(score)
    except Exception:
        pass

    while running:
        # Delta time is capped at 60 FPS and powers the new AI. Existing player
        # movement/projectiles stay frame based so the old game feel is preserved.
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

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    spieler.show_hitbox = not spieler.show_hitbox

                # Debug/quick ship switch from the original project. Existing
                # enemies are cleared so the "never same ship" rule can never
                # be violated after a live switch.
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

        # ---------------- Player projectiles ----------------
        for laser in laser_list[:]:
            laser.update()
            if laser.rect.bottom < 0:
                laser_list.remove(laser)

        for current_torpedo in torpedo_list[:]:
            current_torpedo.update()
            if current_torpedo.rect.bottom < 0:
                torpedo_list.remove(current_torpedo)

        # ---------------- Intelligent enemy system ----------------
        difficulty = background.get_current_difficulty()
        system_difficulty = int(difficulty.get("level", 1))
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

        # ---------------- Rendering ----------------
        screen.fill(BLACK)
        background.update(score)
        background.draw(screen)

        enemy_manager.draw(screen, show_hitboxes=spieler.show_hitbox)
        spieler.draw(screen)

        for laser in laser_list:
            laser.draw(screen)
        for current_torpedo in torpedo_list:
            current_torpedo.draw(screen)

        score_text = font.render(f"Punkte: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        draw_lives(screen, getattr(spieler, "lives", 0), faction_for_player(spieler))

        pygame.display.flip()

    restart = death_screen(screen, clock, score, WIDTH, HEIGHT)
    if not restart:
        break

pygame.quit()
sys.exit()
