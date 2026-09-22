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
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
    ASTEROID_MIN_SPAWN_INTERVAL,
)
from game.enemies import EnemyManager
from game.entities.asteroid import Asteroid
from game.entities.explosion import Explosion
from game.entities.ships import BattleDroid, MillenniumFalcon, Tiefighter, XWing
from game.multiplayer import MultiplayerSession
from game.network import NETWORK_DEBUG
from game.scoreboard import draw_scoreboard
from game.ui import death_screen, faction_selection, ship_selection
from game.ui.difficulty import difficulty_selection
from game.ui.multiplayer import (
    lan_menu,
    lobby_screen,
    local_pvp_player_prompt,
    main_menu,
    multiplayer_menu,
    pvp_lan_menu,
    pvp_mode_menu,
)
from game.pvp_duel import PvPDuelSession
from game.local_pvp import LocalPvPDuelSession
from game.points_fight import LocalPointsFightSession, PointsPlayerConfig
from game.constants import (
    PVP_MAX_PLAYERS,
    LOCAL_PVP_PLAYER1_NAME,
    LOCAL_PVP_PLAYER2_NAME,
)


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
set_window_icon()
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

assets = load_assets()

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


SHIP_NAME_BY_KEY = {
    "xwing": "X-Wing",
    "milleniumfalcon": "Millennium Falcon",
    "tiefighter": "TIE Fighter",
    "battledroid": "Battle Droid",
}


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


def create_asteroid(width, height, size_multiplier=1.0, speed_multiplier=1.0):
    """Create a balanced asteroid. All multipliers come from constants.py."""
    if not asteroid_images:
        return None
    return Asteroid(
        width,
        height,
        asteroid_images,
        size_multiplier=size_multiplier,
        speed_multiplier=speed_multiplier,
    )


def draw_enemy_warning(screen, text, width, height, remaining_ms):
    """Large but short warning before a newly unlocked enemy tier appears."""
    if not text:
        return

    pulse = 1.0 + 0.04 * pygame.math.Vector2(1, 0).rotate(
        (remaining_ms / 80.0) % 360
    ).x
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((120, 0, 0, 95))
    screen.blit(overlay, (0, 0))

    warning_font = pygame.font.Font(None, max(44, int(min(width, height) * 0.075 * pulse)))
    sub_font = pygame.font.Font(None, max(24, int(min(width, height) * 0.038)))

    title = warning_font.render("!!! WARNUNG !!!", True, (255, 235, 120))
    message = sub_font.render(text, True, (255, 255, 255))

    screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.40))))
    screen.blit(message, message.get_rect(center=(width // 2, int(height * 0.50))))


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


def run_game_session(faction_choice, difficulty_choice, ship_choice, multiplayer=None):
    """Run the existing local game simulation, optionally with LAN overlays."""
    global screen, WIDTH, HEIGHT

    spieler = create_player(ship_choice, WIDTH, HEIGHT)
    enemy_manager = EnemyManager(WIDTH, HEIGHT, assets, spieler, difficulty=difficulty_choice)
    background = BackgroundManager(WIDTH, HEIGHT, assets)

    score = 0
    asteroid_spawn_timer = 0
    laser_list = []
    torpedo_list = []
    asteroid_list = []
    explosion_list = []
    running = True
    local_dead = False
    host_disconnected = False
    show_scoreboard = False

    try:
        background.notify_score_anchor(score)
    except Exception:
        pass

    if multiplayer is not None:
        multiplayer.poll(WIDTH, HEIGHT)
        multiplayer.update_local_state(spieler, ship_choice, score, WIDTH, HEIGHT, background.get_current_system_name())

    while running:
        # The AI system uses seconds, while the original asteroid/player
        # systems remain frame based to preserve their existing game feel.
        dt = min(0.05, clock.tick(60) / 1000.0)

        if multiplayer is not None:
            events = multiplayer.poll(WIDTH, HEIGHT)
            for network_event in events:
                if network_event.get("type") == "server_stopped":
                    host_disconnected = True
                    running = False

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

                if new_ship_choice is not None and not (multiplayer is not None and local_dead):
                    spieler = create_player(new_ship_choice, WIDTH, HEIGHT)
                    ship_choice = new_ship_choice
                    laser_list.clear()
                    torpedo_list.clear()
                    enemy_manager.set_player(spieler, clear_existing=True)

                if not local_dead:
                    if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        new_lasers = spieler.shoot()
                        if new_lasers:
                            laser_list.extend(new_lasers)

                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        torpedo = spieler.torpedo()
                        if torpedo:
                            torpedo_list.append(torpedo)

                if multiplayer is not None and event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if not local_dead:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                spieler.move_left()
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                spieler.move_right(WIDTH)
            if keys[pygame.K_ESCAPE]:
                running = False

        # ------------------------------------------------------------
        # PLAYER PROJECTILES
        # ------------------------------------------------------------
        if not local_dead:
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
            # Difficulty + current star system both affect density, speed and size.
            # ------------------------------------------------------------
            difficulty = background.get_current_difficulty()
            system_index = int(difficulty.get("system_index", 0))
            system_bonus = float(difficulty.get("system_bonus", 0.0))
            profile = DIFFICULTY_SETTINGS[difficulty_choice]

            asteroid_speed_multiplier = (
                float(difficulty.get("asteroid_speed_multiplier", 1.0))
                * profile["asteroid_speed"]
                * (1.0 + system_bonus * 0.70)
            )
            asteroid_density = (
                profile["asteroid_density"]
                * (1.0 + system_bonus * 0.80)
            )

            asteroid_interval = max(
                ASTEROID_MIN_SPAWN_INTERVAL,
                int(ASTEROID_SPAWN_INTERVAL / max(0.35, asteroid_density)),
            )

            asteroid_spawn_timer += 1
            if asteroid_spawn_timer >= asteroid_interval:
                asteroid = create_asteroid(
                    WIDTH,
                    HEIGHT,
                    size_multiplier=profile["asteroid_size"] * (1.0 + system_bonus * 0.18),
                    speed_multiplier=asteroid_speed_multiplier,
                )
                if asteroid is not None:
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
                        local_dead = True
                    break

            # ------------------------------------------------------------
            # INTELLIGENT ENEMY SYSTEM
            # Runs in the SAME frame/update as the asteroid system.
            # ------------------------------------------------------------
            enemy_result = enemy_manager.update(
                dt=dt,
                score=score,
                system_difficulty=system_index,
                player_lasers=laser_list,
                player_torpedoes=torpedo_list,
            )
            score += enemy_result.score_delta

            if enemy_result.player_dead or spieler.lives <= 0:
                local_dead = True

        # ------------------------------------------------------------
        # RENDERING
        # ------------------------------------------------------------
        screen.fill(BLACK)
        background.update(score)
        background.draw(screen)

        # Enemy manager remains local.  A dead local player simply stops updating
        # while the network view and scoreboard continue to run.
        try:
            if 'enemy_result' in locals() and enemy_result.warning_text and not local_dead:
                draw_enemy_warning(
                    screen,
                    enemy_result.warning_text,
                    WIDTH,
                    HEIGHT,
                    enemy_manager.warning_timer_ms,
                )
        except Exception:
            pass

        enemy_manager.draw(screen, show_hitboxes=spieler.show_hitbox)

        if not local_dead:
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

        if multiplayer is not None:
            multiplayer.draw_remote_players(screen, assets)

        score_text = font.render(f"Punkte: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        draw_lives(screen, getattr(spieler, "lives", 0), faction_for_player(spieler))

        if multiplayer is not None:
            if local_dead:
                dead_font = pygame.font.Font(None, max(34, int(min(WIDTH, HEIGHT) * 0.055)))
                dead_text = dead_font.render("GAME OVER – ESC zum Verlassen", True, (255, 120, 120))
                screen.blit(dead_text, dead_text.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.72))))
            elif not multiplayer.connected:
                net_text = pygame.font.Font(None, 28).render("Netzwerkverbindung verloren", True, (255, 160, 100))
                screen.blit(net_text, net_text.get_rect(center=(WIDTH // 2, 30)))

            # TAB is intentionally a hold-to-show overlay, so it never pauses the game.
            show_scoreboard = keys[pygame.K_TAB]
            if show_scoreboard:
                draw_scoreboard(screen, multiplayer.get_scoreboard_rows(), multiplayer.local_id)

            multiplayer.update_local_state(spieler, ship_choice, score, WIDTH, HEIGHT, background.get_current_system_name())

        pygame.display.flip()

        if multiplayer is None and local_dead:
            running = False

    if multiplayer is not None:
        multiplayer.set_final_local_state(spieler, ship_choice, score, WIDTH, HEIGHT, background.get_current_system_name())

    return {
        "score": score,
        "host_disconnected": host_disconnected,
        "local_dead": local_dead,
    }


def wait_for_multiplayer_start(session, width, height):
    """Wait without blocking the Pygame loop until the synchronized game starts."""
    global screen
    title_font = pygame.font.Font(None, max(42, int(min(width, height) * 0.09)))
    small_font = pygame.font.Font(None, 28)

    while True:
        events = session.poll(width, height)
        game_started = any(event.get("type") == "game_started" for event in events)
        server_stopped = any(event.get("type") == "server_stopped" for event in events)
        if server_stopped:
            return False
        if game_started or session.phase == "game":
            return True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                session.stop()
                pygame.quit()
                raise SystemExit
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        screen.fill((5, 6, 18))
        title = title_font.render("3  2  1  GO!", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width // 2, height // 2 - 50)))

        import time
        remaining = max(0.0, session.client.started_at - time.time())
        if session.phase == "countdown" and remaining > 0:
            number = str(max(1, int(remaining) + 1))
            count_font = pygame.font.Font(None, max(70, int(min(width, height) * 0.18)))
            surface = count_font.render(number, True, (120, 220, 255))
            screen.blit(surface, surface.get_rect(center=(width // 2, height // 2 + 30)))
        else:
            message = small_font.render("Warte auf die anderen Spieler...", True, (170, 180, 195))
            screen.blit(message, message.get_rect(center=(width // 2, height // 2 + 45)))

        pygame.display.flip()
        clock.tick(60)


def run_singleplayer_flow():
    global screen
    while True:
        faction_choice, new_width, new_height = faction_selection(
            screen,
            clock,
            WIDTH,
            HEIGHT,
            rebel_logo_img,
            empire_logo_img,
        )
        set_dimensions(new_width, new_height)

        difficulty_choice, new_width, new_height = difficulty_selection(
            screen,
            clock,
            WIDTH,
            HEIGHT,
            DEFAULT_DIFFICULTY,
        )
        set_dimensions(new_width, new_height)

        faction_logo_img = rebel_logo_img if faction_choice == "rebels" else empire_logo_img
        ship_choice, new_width, new_height = ship_selection(
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
        set_dimensions(new_width, new_height)

        result = run_game_session(faction_choice, difficulty_choice, ship_choice)
        restart = death_screen(screen, clock, result["score"], WIDTH, HEIGHT)
        if not restart:
            return "menu"


def set_dimensions(width, height):
    global WIDTH, HEIGHT, screen
    WIDTH = max(480, int(width))
    HEIGHT = max(360, int(height))
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    set_window_icon()


def run_multiplayer_flow(config, game_mode="points"):
    global screen
    session = MultiplayerSession(debug=NETWORK_DEBUG, game_mode=game_mode, max_players=10)

    try:
        if config["action"] == "host":
            session.host(config["name"])
        else:
            session.join(config["ip"], config["name"])

        # Lobby is non-blocking from the network perspective.  A failed connect
        # becomes an on-screen message and can be cancelled with ESC.
        lobby_result = lobby_screen(screen, clock, session, WIDTH, HEIGHT)
        if lobby_result == "back":
            return "menu"
        if lobby_result == "host_disconnected":
            return "menu"

        # Every player keeps the original faction/difficulty/ship selection.
        # The server waits until everyone has sent READY before starting the
        # synchronized countdown, so local menus may take different amounts of time.
        faction_choice, new_width, new_height = faction_selection(
            screen,
            clock,
            WIDTH,
            HEIGHT,
            rebel_logo_img,
            empire_logo_img,
        )
        set_dimensions(new_width, new_height)

        difficulty_choice, new_width, new_height = difficulty_selection(
            screen,
            clock,
            WIDTH,
            HEIGHT,
            DEFAULT_DIFFICULTY,
        )
        set_dimensions(new_width, new_height)

        faction_logo_img = rebel_logo_img if faction_choice == "rebels" else empire_logo_img
        ship_choice, new_width, new_height = ship_selection(
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
        set_dimensions(new_width, new_height)

        session.send_ready(ship_choice, difficulty_choice)
        if not wait_for_multiplayer_start(session, WIDTH, HEIGHT):
            return "menu"

        result = run_game_session(
            faction_choice,
            difficulty_choice,
            ship_choice,
            multiplayer=session,
        )

        if result["host_disconnected"]:
            # A client should return directly to the LAN menu after a host stop.
            return "menu"

        return "menu"
    finally:
        session.stop()



def run_local_points_flow():
    """Run two completely independent single-player simulations side-by-side."""
    global screen
    configs = []

    for player_number, player_name in ((1, LOCAL_PVP_PLAYER1_NAME), (2, LOCAL_PVP_PLAYER2_NAME)):
        if local_pvp_player_prompt(screen, clock, WIDTH, HEIGHT, player_number) is None:
            return "menu"

        faction_choice, new_width, new_height = faction_selection(
            screen, clock, WIDTH, HEIGHT, rebel_logo_img, empire_logo_img
        )
        set_dimensions(new_width, new_height)

        difficulty_choice, new_width, new_height = difficulty_selection(
            screen, clock, WIDTH, HEIGHT, DEFAULT_DIFFICULTY
        )
        set_dimensions(new_width, new_height)

        faction_logo_img = rebel_logo_img if faction_choice == "rebels" else empire_logo_img
        ship_choice, new_width, new_height = ship_selection(
            screen, clock, WIDTH, HEIGHT, faction_choice, faction_logo_img,
            x_wing_img, millennium_falcon_img, tiefighter_img, battle_droid_img
        )
        set_dimensions(new_width, new_height)

        configs.append(PointsPlayerConfig(
            name=player_name,
            ship=ship_choice,
            faction=faction_choice,
            difficulty=difficulty_choice,
        ))

    session = LocalPointsFightSession(configs, assets)
    result = session.run(screen, clock)
    if result.get("quit"):
        return "menu"
    return "menu"


def run_local_pvp_flow(duel_mode):
    """Start a local two-player PvP duel without creating a network connection."""
    global screen

    for player_number, player_name in ((1, LOCAL_PVP_PLAYER1_NAME), (2, LOCAL_PVP_PLAYER2_NAME)):
        if local_pvp_player_prompt(screen, clock, WIDTH, HEIGHT, player_number) is None:
            return "menu"

        faction_choice, new_width, new_height = faction_selection(
            screen,
            clock,
            WIDTH,
            HEIGHT,
            rebel_logo_img,
            empire_logo_img,
        )
        set_dimensions(new_width, new_height)

        faction_logo_img = rebel_logo_img if faction_choice == "rebels" else empire_logo_img
        ship_choice, new_width, new_height = ship_selection(
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
        set_dimensions(new_width, new_height)

        if player_number == 1:
            player1 = {
                "name": player_name,
                "faction": faction_choice,
                "ship": ship_choice,
            }
        else:
            player2 = {
                "name": player_name,
                "faction": faction_choice,
                "ship": ship_choice,
            }

    duel = LocalPvPDuelSession(player1, player2, assets, mode=duel_mode)
    result = duel.run(screen, clock)
    if result.get("quit"):
        return "menu"
    return "menu"


def run_pvp_flow(config, duel_mode):
    global screen
    session = MultiplayerSession(debug=NETWORK_DEBUG, game_mode="pvp", max_players=PVP_MAX_PLAYERS)

    try:
        if config["action"] == "host":
            session.host(config["name"])
        else:
            session.join(config["ip"], config["name"])

        lobby_result = lobby_screen(
            screen,
            clock,
            session,
            WIDTH,
            HEIGHT,
            title_text="STAR WARS – PvP-DUELL LOBBY",
            max_players=PVP_MAX_PLAYERS,
            start_requires_full=True,
        )
        if lobby_result != "start":
            return "menu"

        faction_choice, new_width, new_height = faction_selection(
            screen,
            clock,
            WIDTH,
            HEIGHT,
            rebel_logo_img,
            empire_logo_img,
        )
        set_dimensions(new_width, new_height)

        faction_logo_img = rebel_logo_img if faction_choice == "rebels" else empire_logo_img
        ship_choice, new_width, new_height = ship_selection(
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
        set_dimensions(new_width, new_height)

        # Difficulty stays shared and neutral in PvP; the selected duel rule
        # is carried to the server so the host rule becomes authoritative.
        session.send_ready(ship_choice, DEFAULT_DIFFICULTY, game_rule=duel_mode)
        if not wait_for_multiplayer_start(session, WIDTH, HEIGHT):
            return "menu"

        duel = PvPDuelSession(session, assets, mode=duel_mode, debug=NETWORK_DEBUG)
        result = duel.run(screen, clock)
        if result.get("quit"):
            return "menu"
        return "menu"
    finally:
        session.stop()


def main():
    global screen, WIDTH, HEIGHT

    while True:
        mode = main_menu(screen, clock, WIDTH, HEIGHT)
        current_surface = pygame.display.get_surface()
        if current_surface is not None:
            screen = current_surface
            WIDTH, HEIGHT = screen.get_size()
        if mode == "quit":
            break

        if mode == "singleplayer":
            run_singleplayer_flow()
            continue

        if mode == "multiplayer":
            multiplayer_mode = multiplayer_menu(screen, clock, WIDTH, HEIGHT)
            current_surface = pygame.display.get_surface()
            if current_surface is not None:
                screen = current_surface
                WIDTH, HEIGHT = screen.get_size()
            if multiplayer_mode == "back":
                continue

            if multiplayer_mode in {"lan_pvp", "local_pvp"}:
                duel_mode = pvp_mode_menu(screen, clock, WIDTH, HEIGHT)
                current_surface = pygame.display.get_surface()
                if current_surface is not None:
                    screen = current_surface
                    WIDTH, HEIGHT = screen.get_size()
                if duel_mode is None:
                    continue

                if multiplayer_mode == "local_pvp":
                    if duel_mode == "points":
                        run_local_points_flow()
                    else:
                        run_local_pvp_flow(duel_mode)
                else:
                    config = pvp_lan_menu(screen, clock, WIDTH, HEIGHT, duel_mode)
                    current_surface = pygame.display.get_surface()
                    if current_surface is not None:
                        screen = current_surface
                        WIDTH, HEIGHT = screen.get_size()
                    if config is not None:
                        if duel_mode == "points":
                            run_multiplayer_flow(config, game_mode="points")
                        else:
                            run_pvp_flow(config, duel_mode)
                continue

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
