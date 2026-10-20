"""Pygame menus for LAN multiplayer."""
from __future__ import annotations

import math

import pygame
from game.assets import get_font, load_assets
from game.background import BackgroundManager

from game.network import LAN_PORT
from game.settings import load_settings, save_settings
from game.constants import DIFFICULTY_SETTINGS

MENU_ASSETS = load_assets()


def _draw_button(screen, rect, text, font, hover=False, enabled=True, accent=(76, 175, 255), glow_scale=1.0):
    if hover and enabled:
        fill = (22, 31, 52)
        border = accent
        text_color = (245, 247, 255)
        glow = pygame.Surface((int(rect.width * 1.12), int(rect.height * 1.22)), pygame.SRCALPHA)
        glow_rect = glow.get_rect(center=rect.center)
        glow_box = glow.get_rect().inflate(-12, -12)
        pygame.draw.rect(glow, accent + (70,), glow_box, border_radius=18)
        screen.blit(glow, glow_rect)
        draw_rect = rect.inflate(int(rect.width * 0.12 * glow_scale), int(rect.height * 0.18 * glow_scale))
    else:
        fill = (22, 27, 39)
        border = accent if enabled else (90, 90, 90)
        text_color = (240, 242, 246) if enabled else (130, 130, 130)
        draw_rect = rect

    pygame.draw.rect(screen, fill, draw_rect, border_radius=16)
    pygame.draw.rect(screen, border, draw_rect, 2, border_radius=16)
    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=draw_rect.center)
    screen.blit(label, label_rect)


def _input_field(screen, rect, text, font, active):
    pygame.draw.rect(screen, (20, 24, 40), rect, border_radius=10)
    pygame.draw.rect(screen, (0, 180, 255) if active else (100, 110, 130), rect, 2, border_radius=10)
    label = font.render(text or "", True, (240, 240, 245))
    screen.blit(label, (rect.x + 12, rect.centery - label.get_height() // 2))


def _draw_menu_background(screen, width, height, background):
    """Render a cinematic space battle backdrop with parallax motion and nebulae."""
    background.resize(width, height)
    background.starfield.update()
    background.planet_manager.maybe_spawn(True)
    background.planet_manager.update()

    t = pygame.time.get_ticks() * 0.001

    # Deep-space base and parallax star layers
    sky = pygame.Surface((width, height), pygame.SRCALPHA)
    sky.fill((6, 10, 22, 180))
    background.starfield.draw(sky)
    screen.blit(sky, (0, 0))

    # Left blue nebula and right red nebula create the faction split
    nebula = pygame.Surface((width, height), pygame.SRCALPHA)
    left_center = (int(width * 0.16), int(height * 0.55))
    right_center = (int(width * 0.84), int(height * 0.52))
    pygame.draw.ellipse(nebula, (38, 110, 255, 95), (left_center[0] - 260, left_center[1] - 180, 520, 360))
    pygame.draw.ellipse(nebula, (255, 80, 80, 90), (right_center[0] - 260, right_center[1] - 180, 520, 360))
    screen.blit(nebula, (0, 0))

    # Distant planet in the upper-right corner
    planet_center = (int(width * 0.82), int(height * 0.22))
    planet_radius = max(80, int(min(width, height) * 0.13))
    pygame.draw.circle(screen, (70, 78, 105), planet_center, planet_radius)
    pygame.draw.circle(screen, (120, 140, 190), planet_center, int(planet_radius * 0.82), 2)
    pygame.draw.arc(screen, (180, 210, 255, 150), (planet_center[0] - planet_radius, planet_center[1] - planet_radius, planet_radius * 2, planet_radius * 2), 0.8, 2.3, 2)

    # Asteroid field crossing diagonally
    for i in range(14):
        x = (i * 110 + int(t * 70)) % (width + 200) - 100
        y = (i * 72 + int(t * 30)) % (height + 140) - 70
        points = [
            (x, y),
            (x + 12, y + 8),
            (x + 28, y + 2),
            (x + 18, y + 18),
            (x + 2, y + 14),
        ]
        pygame.draw.polygon(screen, (120, 130, 155, 140), points)
        pygame.draw.lines(screen, (180, 200, 230, 80), True, points, 1)

    # Distant battleground silhouettes
    for i in range(3):
        ship_y = int(height * (0.20 + i * 0.16))
        x1 = -40 + i * 240 + int(t * 18) % 100
        x2 = width + 30 + i * 160 - int(t * 12) % 100
        pygame.draw.line(screen, (115, 145, 180, 90), (x1, ship_y), (x1 + 100, ship_y - 10), 2)
        pygame.draw.line(screen, (115, 145, 180, 90), (x2, ship_y + 15), (x2 - 100, ship_y + 5), 2)

    # Laser streaks and engine glows
    for i in range(8):
        offset = (i * 163 + int(t * 180)) % (width + 300)
        yline = int(height * (0.34 + (i % 4) * 0.12))
        alpha = 90 + (i % 3) * 20
        if i % 2 == 0:
            pygame.draw.line(screen, (110, 195, 255, alpha), (offset - 220, yline), (offset, yline - 20), 2)
        else:
            pygame.draw.line(screen, (255, 110, 110, alpha), (offset, yline + 8), (offset - 220, yline - 12), 2)

    # Center darkening so the menu hierarchy remains readable
    center_vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(18, 0, -1):
        radius = max(120, width // 2 + i * 22)
        pygame.draw.circle(center_vignette, (0, 0, 0, max(0, 110 - i * 4)), (width // 2, height // 2), radius)
    screen.blit(center_vignette, (0, 0))

    # Small accent logos only, not dominant as oversized focal points
    rebel_small = MENU_ASSETS.get("rebel_logo_img")
    empire_small = MENU_ASSETS.get("empire_logo_img")
    if rebel_small:
        rebel_surf = pygame.transform.smoothscale(rebel_small, (64, 64))
        screen.blit(rebel_surf, (width * 0.18 - 32, height * 0.12))
    if empire_small:
        empire_surf = pygame.transform.smoothscale(empire_small, (64, 64))
        screen.blit(empire_surf, (width * 0.82 - 32, height * 0.12))


def _draw_faction_badge(screen, image, rect, accent_color, label=None):
    glow = pygame.Surface((rect.width + 58, rect.height + 58), pygame.SRCALPHA)
    glow_rect = glow.get_rect(center=rect.center)
    pygame.draw.ellipse(glow, accent_color + (80,), glow.get_rect().inflate(-6, -6))
    screen.blit(glow, glow_rect)

    scaled = pygame.transform.smoothscale(image, (rect.width, rect.height))
    screen.blit(scaled, scaled.get_rect(center=rect.center))

    if label:
        label_surf = get_font(max(12, int(rect.height * 0.16)), "sci_fi").render(label, True, (240, 244, 255))
        screen.blit(label_surf, label_surf.get_rect(midbottom=(rect.centerx, rect.bottom + 18)))


def _draw_menu_button(screen, rect, text, font, hover=False, accent=(76, 175, 255), halo=(100, 200, 255)):
    if hover:
        draw_rect = rect.inflate(12, 10)
        fill = (12, 18, 30)
        border = accent
        text_color = (245, 247, 255)
        glow = pygame.Surface((draw_rect.width + 26, draw_rect.height + 26), pygame.SRCALPHA)
        glow_rect = glow.get_rect(center=draw_rect.center)
        pygame.draw.rect(glow, accent + (90,), glow.get_rect().inflate(-12, -12), border_radius=18)
        screen.blit(glow, glow_rect)
    else:
        draw_rect = rect
        fill = (12, 18, 30)
        border = accent
        text_color = (232, 236, 246)

    pygame.draw.rect(screen, fill, draw_rect, border_radius=18)
    pygame.draw.rect(screen, border, draw_rect, 2, border_radius=18)
    label = font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=draw_rect.center))


def main_menu(screen, clock, width, height):
    """Show a cinematic star-war menu composition with strong central hierarchy."""
    background = BackgroundManager(width, height, MENU_ASSETS)
    title_font = get_font(max(62, int(min(width, height) * 0.13)), "sci_fi")
    subtitle_font = get_font(max(18, int(min(width, height) * 0.028)), "sci_fi")
    button_font = get_font(max(22, int(min(width, height) * 0.04)), "sci_fi")

    settings_open = False
    settings = load_settings()
    button_panel_rect = pygame.Rect(width // 2 - 180, int(height * 0.52), 360, 220)

    while True:
        mouse = pygame.mouse.get_pos()
        buttons = [
            (pygame.Rect(button_panel_rect.x + 30, button_panel_rect.y + 28, 300, 54), "Einzelspieler", "singleplayer", (66, 153, 255)),
            (pygame.Rect(button_panel_rect.x + 30, button_panel_rect.y + 92, 300, 54), "Mehrspieler", "multiplayer", (228, 72, 72)),
            (pygame.Rect(button_panel_rect.x + 30, button_panel_rect.y + 156, 300, 54), "Einstellungen", "settings", (72, 178, 255)),
        ]

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return main_menu(screen, clock, width, height)

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if settings_open:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        settings_open = False
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        settings["difficulty"] = ("easy", "normal", "hard", "expert")[event.key - pygame.K_1]
                        save_settings(settings)
                    continue
                if event.key == pygame.K_1:
                    return "singleplayer"
                if event.key == pygame.K_2:
                    return "multiplayer"
                if event.key == pygame.K_3:
                    settings_open = True
                if event.key == pygame.K_ESCAPE:
                    return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if settings_open:
                    panel = pygame.Rect(width // 2 - min(390, width // 2 - 24), height // 2 - 190, min(780, width - 48), 380)
                    card_w = max(110, (panel.width - 60) // 4)
                    cards_y = panel.y + 105
                    card_h = 100
                    for i, key in enumerate(("easy", "normal", "hard", "expert")):
                        card = pygame.Rect(panel.x + 12 + i * (card_w + 8), cards_y, card_w, card_h)
                        if card.collidepoint(event.pos):
                            settings["difficulty"] = key
                            save_settings(settings)
                    fullscreen_rect = pygame.Rect(panel.x + 28, panel.y + 245, panel.width - 56, 44)
                    fps_rect = pygame.Rect(panel.x + 28, panel.y + 298, panel.width - 56, 38)
                    close_rect = pygame.Rect(panel.right - 142, panel.bottom - 52, 120, 36)
                    if fullscreen_rect.collidepoint(event.pos):
                        settings["fullscreen"] = not settings["fullscreen"]
                        flags = pygame.FULLSCREEN if settings["fullscreen"] else pygame.RESIZABLE
                        screen = pygame.display.set_mode((width, height), flags)
                        width, height = screen.get_size()
                        save_settings(settings)
                        return main_menu(screen, clock, width, height)
                    elif fps_rect.collidepoint(event.pos):
                        settings["show_fps"] = not settings["show_fps"]
                        save_settings(settings)
                    elif close_rect.collidepoint(event.pos):
                        settings_open = False
                    continue

                for rect, _, value, _ in buttons:
                    if rect.collidepoint(event.pos):
                        if value == "settings":
                            settings_open = True
                            break
                        return value

        _draw_menu_background(screen, width, height, background)

        # Title with metallic glow and pulse
        pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 280.0)
        title_base = title_font.render("STAR WARS", True, (245, 248, 255))
        title_glow = pygame.Surface((int(title_base.get_width() * pulse), int(title_base.get_height() * pulse)), pygame.SRCALPHA)
        title_glow.blit(title_base, (0, 0))
        title_rect = title_base.get_rect(center=(width // 2, int(height * 0.18)))
        for dx, dy, color in [(-3, 0, (35, 118, 255)), (3, 0, (255, 76, 76)), (0, -2, (255, 255, 255))]:
            shadow = title_base.copy()
            shadow.fill(color + (120,), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(shadow, (title_rect.x + dx, title_rect.y + dy))
        screen.blit(title_base, title_rect)

        subtitle = subtitle_font.render("REBELLION VS EMPIRE", True, (200, 214, 240))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.29))))

        # Small faction accents left and right of the menu
        accent_rect_left = pygame.Rect(width // 2 - 260, int(height * 0.18), 80, 80)
        accent_rect_right = pygame.Rect(width // 2 + 180, int(height * 0.18), 80, 80)
        rebel_logo = MENU_ASSETS.get("rebel_logo_img")
        empire_logo = MENU_ASSETS.get("empire_logo_img")
        if rebel_logo:
            _draw_faction_badge(screen, rebel_logo, accent_rect_left, (66, 153, 255), "REBELLION")
        if empire_logo:
            _draw_faction_badge(screen, empire_logo, accent_rect_right, (255, 85, 85), "EMPIRE")

        panel_surface = pygame.Surface((button_panel_rect.width, button_panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (10, 16, 28, 165), panel_surface.get_rect(), border_radius=24)
        pygame.draw.rect(panel_surface, (96, 148, 255, 140), panel_surface.get_rect(), 2, border_radius=24)
        screen.blit(panel_surface, button_panel_rect.topleft)

        for rect, text, _, accent in buttons:
            hovered = rect.collidepoint(mouse)
            _draw_menu_button(screen, rect, text, button_font, hover=hovered, accent=accent)

        if settings_open:
            shade = pygame.Surface((width, height), pygame.SRCALPHA)
            shade.fill((0, 0, 8, 185))
            screen.blit(shade, (0, 0))
            panel = pygame.Rect(width // 2 - min(390, width // 2 - 24), height // 2 - 190, min(780, width - 48), 380)
            panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (8, 15, 30, 248), panel_surface.get_rect(), border_radius=22)
            pygame.draw.rect(panel_surface, (78, 166, 255, 220), panel_surface.get_rect(), 2, border_radius=22)
            screen.blit(panel_surface, panel.topleft)

            heading = get_font(30, "sci_fi").render("SYSTEMEINSTELLUNGEN", True, (236, 244, 255))
            screen.blit(heading, heading.get_rect(center=(panel.centerx, panel.y + 38)))
            section = get_font(18, "sci_fi").render("SCHWIERIGKEIT  ·  gilt für neue Spielrunden", True, (150, 205, 255))
            screen.blit(section, section.get_rect(center=(panel.centerx, panel.y + 76)))

            card_w = max(110, (panel.width - 60) // 4)
            cards_y = panel.y + 105
            descriptions = {
                "easy": "Weniger Druck", "normal": "Ausgewogen",
                "hard": "Aggressivere Gegner", "expert": "Maximale Herausforderung",
            }
            for i, key in enumerate(("easy", "normal", "hard", "expert")):
                card = pygame.Rect(panel.x + 12 + i * (card_w + 8), cards_y, card_w, 100)
                active = settings["difficulty"] == key
                hover = card.collidepoint(mouse)
                pygame.draw.rect(screen, (22, 48, 75) if active else (16, 24, 40), card, border_radius=12)
                pygame.draw.rect(screen, (74, 190, 255) if active else ((100, 135, 175) if hover else (58, 76, 100)), card, 2 if active else 1, border_radius=12)
                label = get_font(20, "sci_fi").render(DIFFICULTY_SETTINGS[key]["name"].upper(), True, (245, 249, 255))
                screen.blit(label, label.get_rect(center=(card.centerx, card.y + 32)))
                desc_font = get_font(13, "sci_fi")
                desc = desc_font.render(descriptions[key], True, (170, 187, 210))
                screen.blit(desc, desc.get_rect(center=(card.centerx, card.y + 66)))
                if active:
                    marker = get_font(13, "sci_fi").render("AKTIV", True, (90, 210, 255))
                    screen.blit(marker, marker.get_rect(center=(card.centerx, card.y + 86)))

            fullscreen_rect = pygame.Rect(panel.x + 28, panel.y + 220, panel.width - 56, 42)
            fps_rect = pygame.Rect(panel.x + 28, panel.y + 270, panel.width - 56, 38)
            _draw_menu_button(screen, fullscreen_rect, "Vollbild: " + ("AN" if settings["fullscreen"] else "AUS"), get_font(17, "sci_fi"), fullscreen_rect.collidepoint(mouse), accent=(80, 175, 255))
            _draw_menu_button(screen, fps_rect, "FPS-Anzeige: " + ("AN" if settings["show_fps"] else "AUS"), get_font(16, "sci_fi"), fps_rect.collidepoint(mouse), accent=(130, 150, 190))
            close_rect = pygame.Rect(panel.right - 142, panel.bottom - 48, 120, 34)
            _draw_menu_button(screen, close_rect, "FERTIG", get_font(16, "sci_fi"), close_rect.collidepoint(mouse), accent=(80, 200, 150))
            footer = get_font(13, "sci_fi").render("1–4: Schwierigkeit   ·   ENTER / ESC: Schließen", True, (150, 165, 188))
            screen.blit(footer, footer.get_rect(midleft=(panel.x + 24, panel.bottom - 28)))

        hint = get_font(16, "sci_fi").render("1 = EINZELSPIELER   2 = MEHRSPIELER   3 = EINSTELLUNGEN   ESC = BEENDEN", True, (178, 188, 204))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 26)))

        pygame.display.flip()
        clock.tick(60)


def multiplayer_menu(screen, clock, width, height):
    """Choose local multiplayer or LAN multiplayer.

    The old standalone LAN/PvP entries are intentionally hidden here.
    LAN access is only possible through the LAN Multiplayer entry below,
    while the local mode never creates a network connection.
    """
    font = get_font(max(28, int(min(width, height) * 0.050)))
    title_font = get_font(max(40, int(min(width, height) * 0.085)))

    buttons = [
        (
            pygame.Rect(width // 2 - 230, int(height * 0.34), 460, 68),
            "Lokaler Multiplayer",
            "local_pvp",
        ),
        (
            pygame.Rect(width // 2 - 230, int(height * 0.47), 460, 68),
            "LAN Multiplayer",
            "lan_pvp",
        ),
        (
            pygame.Rect(width // 2 - 230, int(height * 0.64), 460, 62),
            "Zurück",
            "back",
        ),
    ]

    while True:
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return multiplayer_menu(screen, clock, width, height)

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "local_pvp"
                if event.key == pygame.K_2:
                    return "lan_pvp"
                if event.key == pygame.K_ESCAPE:
                    return "back"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, _, value in buttons:
                    if rect.collidepoint(event.pos):
                        return value

        screen.fill((7, 8, 20))
        title = title_font.render("MEHRSPIELER", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.18))))

        subtitle = get_font(24).render(
            "Offline auf einem PC oder gemeinsam über das LAN",
            True,
            (165, 185, 215),
        )
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.27))))

        for rect, text, _ in buttons:
            _draw_button(screen, rect, text, font, rect.collidepoint(mouse))

        hint = get_font(22).render(
            "1 = Lokal   2 = LAN   ESC = Zurück",
            True,
            (150, 155, 170),
        )
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 34)))
        pygame.display.flip()
        clock.tick(60)


def lan_menu(screen, clock, width, height):
    """Return {'action': 'host'/'join', 'name': ..., 'ip': ...} or None."""
    font = get_font(34)
    title_font = get_font(max(38, int(min(width, height) * 0.08)))
    small_font = get_font(24)
    name = "Spieler"
    ip = ""
    active = "name"
    error = ""

    while True:
        name_rect = pygame.Rect(width // 2 - 180, 175, 360, 52)
        ip_rect = pygame.Rect(width // 2 - 180, 265, 360, 52)
        host_rect = pygame.Rect(width // 2 - 180, 355, 170, 60)
        join_rect = pygame.Rect(width // 2 + 10, 355, 170, 60)
        back_rect = pygame.Rect(width // 2 - 180, 440, 360, 60)
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return lan_menu(screen, clock, width, height)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_TAB:
                    active = "ip" if active == "name" else "name"
                elif event.key == pygame.K_BACKSPACE:
                    if active == "name":
                        name = name[:-1]
                    else:
                        ip = ip[:-1]
                elif event.key == pygame.K_RETURN:
                    if active == "name":
                        active = "ip"
                    elif ip.strip():
                        return {"action": "join", "name": name.strip() or "Spieler", "ip": ip.strip()}
                else:
                    char = event.unicode
                    if char and char.isprintable():
                        if active == "name" and len(name) < 20:
                            name += char
                        elif active == "ip" and len(ip) < 45 and (char.isdigit() or char == "."):
                            ip += char
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if name_rect.collidepoint(event.pos):
                    active = "name"
                elif ip_rect.collidepoint(event.pos):
                    active = "ip"
                elif host_rect.collidepoint(event.pos):
                    return {"action": "host", "name": name.strip() or "Host", "ip": ""}
                elif join_rect.collidepoint(event.pos):
                    if ip.strip():
                        return {"action": "join", "name": name.strip() or "Spieler", "ip": ip.strip()}
                    error = "Bitte die IP-Adresse des Hosts eingeben."
                elif back_rect.collidepoint(event.pos):
                    return None

        screen.fill((7, 8, 20))
        title = title_font.render("LAN MULTIPLAYER", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width // 2, 90)))
        screen.blit(get_font(24).render(f"Port: {LAN_PORT}", True, (150, 160, 180)), (width // 2 - 45, 125))

        screen.blit(small_font.render("Spielername", True, (190, 200, 215)), (name_rect.x, name_rect.y - 28))
        _input_field(screen, name_rect, name, font, active == "name")
        screen.blit(small_font.render("IP-Adresse des Hosts (nur beim Beitreten)", True, (190, 200, 215)), (ip_rect.x, ip_rect.y - 28))
        _input_field(screen, ip_rect, ip or "z. B. 192.168.178.20", font, active == "ip")

        _draw_button(screen, host_rect, "Spiel erstellen", font, host_rect.collidepoint(mouse))
        _draw_button(screen, join_rect, "Spiel beitreten", font, join_rect.collidepoint(mouse))
        _draw_button(screen, back_rect, "Zurück", font, back_rect.collidepoint(mouse))

        info = small_font.render("TAB wechselt das Eingabefeld • ENTER bestätigt die IP", True, (150, 155, 170))
        screen.blit(info, info.get_rect(center=(width // 2, height - 66)))
        if error:
            error_surface = small_font.render(error, True, (255, 130, 130))
            screen.blit(error_surface, error_surface.get_rect(center=(width // 2, height - 30)))

        pygame.display.flip()
        clock.tick(60)


def pvp_mode_menu(screen, clock, width, height):
    """Choose the PvP rule set before opening the LAN lobby."""
    font = get_font(32)
    title_font = get_font(max(42, int(min(width, height) * 0.08)))
    small_font = get_font(24)
    buttons = [
        (pygame.Rect(width // 2 - 220, int(height * 0.36), 440, 64), "Letzter Überlebender", "last_survivor"),
        (pygame.Rect(width // 2 - 220, int(height * 0.48), 440, 64), "Punktekampf", "points"),
        (pygame.Rect(width // 2 - 220, int(height * 0.64), 440, 64), "Zurück", "back"),
    ]

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return pvp_mode_menu(screen, clock, width, height)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_1:
                    return "last_survivor"
                if event.key == pygame.K_2:
                    return "points"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, _, value in buttons:
                    if rect.collidepoint(event.pos):
                        return None if value == "back" else value

        screen.fill((7, 8, 20))
        title = title_font.render("PvP-DUELL", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.18))))
        subtitle = small_font.render("Punktekampf = eigene Einzelspieler-Welt • Letzter Überlebender = echtes PvP", True, (165, 185, 215))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.27))))
        for rect, text, _ in buttons:
            _draw_button(screen, rect, text, font, rect.collidepoint(mouse))
        hint = small_font.render("1 = Letzter Überlebender   2 = Punktekampf", True, (145, 150, 165))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 34)))
        pygame.display.flip()
        clock.tick(60)


def pvp_lan_menu(screen, clock, width, height, duel_mode):
    """LAN host/join menu for the PvP duel."""
    font = get_font(32)
    title_font = get_font(max(40, int(min(width, height) * 0.075)))
    small_font = get_font(24)
    name = "Spieler"
    ip = ""
    active = "name"
    error = ""
    mode_name = "Letzter Überlebender" if duel_mode == "last_survivor" else "Punktekampf"

    while True:
        name_rect = pygame.Rect(width // 2 - 180, 175, 360, 52)
        ip_rect = pygame.Rect(width // 2 - 180, 265, 360, 52)
        host_rect = pygame.Rect(width // 2 - 180, 355, 170, 60)
        join_rect = pygame.Rect(width // 2 + 10, 355, 170, 60)
        back_rect = pygame.Rect(width // 2 - 180, 440, 360, 60)
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return pvp_lan_menu(screen, clock, width, height, duel_mode)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_TAB:
                    active = "ip" if active == "name" else "name"
                elif event.key == pygame.K_BACKSPACE:
                    if active == "name":
                        name = name[:-1]
                    else:
                        ip = ip[:-1]
                elif event.key == pygame.K_RETURN:
                    if active == "name":
                        active = "ip"
                    elif ip.strip():
                        return {"action": "join", "name": name.strip() or "Spieler", "ip": ip.strip(), "duel_mode": duel_mode}
                else:
                    char = event.unicode
                    if char and char.isprintable():
                        if active == "name" and len(name) < 20:
                            name += char
                        elif active == "ip" and len(ip) < 45 and (char.isdigit() or char == "."):
                            ip += char
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if name_rect.collidepoint(event.pos):
                    active = "name"
                elif ip_rect.collidepoint(event.pos):
                    active = "ip"
                elif host_rect.collidepoint(event.pos):
                    return {"action": "host", "name": name.strip() or "Host", "ip": "", "duel_mode": duel_mode}
                elif join_rect.collidepoint(event.pos):
                    if ip.strip():
                        return {"action": "join", "name": name.strip() or "Spieler", "ip": ip.strip(), "duel_mode": duel_mode}
                    error = "Bitte die IP-Adresse des Hosts eingeben."
                elif back_rect.collidepoint(event.pos):
                    return None

        screen.fill((7, 8, 20))
        title = title_font.render(f"LAN MULTIPLAYER – {mode_name}", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width // 2, 90)))
        screen.blit(small_font.render(f"LAN • 2 Spieler • Port {LAN_PORT}", True, (150, 160, 180)), (width // 2 - 125, 125))
        screen.blit(small_font.render("Spielername", True, (190, 200, 215)), (name_rect.x, name_rect.y - 28))
        _input_field(screen, name_rect, name, font, active == "name")
        screen.blit(small_font.render("IP-Adresse des Hosts (nur beim Beitreten)", True, (190, 200, 215)), (ip_rect.x, ip_rect.y - 28))
        _input_field(screen, ip_rect, ip or "z. B. 192.168.178.20", font, active == "ip")
        _draw_button(screen, host_rect, "Spiel erstellen", font, host_rect.collidepoint(mouse))
        _draw_button(screen, join_rect, "Spiel beitreten", font, join_rect.collidepoint(mouse))
        _draw_button(screen, back_rect, "Zurück", font, back_rect.collidepoint(mouse))
        info = small_font.render("TAB wechselt das Eingabefeld • ENTER bestätigt die IP", True, (150, 155, 170))
        screen.blit(info, info.get_rect(center=(width // 2, height - 66)))
        if error:
            error_surface = small_font.render(error, True, (255, 130, 130))
            screen.blit(error_surface, error_surface.get_rect(center=(width // 2, height - 30)))
        pygame.display.flip()
        clock.tick(60)


def lobby_screen(screen, clock, session, width, height, title_text="STAR WARS – LAN LOBBY", max_players=10, start_requires_full=False):
    """Show a shared lobby. Returns start/back/host_disconnected."""
    font = get_font(30)
    title_font = get_font(max(42, int(min(width, height) * 0.085)))
    small_font = get_font(24)
    status = "Verbinde..."

    while True:
        events = session.poll(width, height)
        for event in events:
            if event.get("type") == "error":
                status = str(event.get("reason") or "Netzwerkfehler")
            elif event.get("type") == "server_stopped":
                return "host_disconnected"
            elif event.get("type") == "setup_started":
                return "start"

        if session.connected:
            status = "Verbunden"
        elif session.connecting:
            status = "Verbinde mit LAN..."
        elif session.error:
            status = session.error

        players = list(session.players.values())
        players.sort(key=lambda p: 0 if str(p.get("id")) == str(session.host_id) else 1)
        back_rect = pygame.Rect(width // 2 - 170, height - 82, 140, 52)
        start_rect = pygame.Rect(width // 2 + 30, height - 82, 140, 52)
        can_start = session.is_host() and session.connected and session.phase == "lobby" and (not start_requires_full or len(players) == max_players)
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                session.stop()
                pygame.quit()
                raise SystemExit
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                if event.key == pygame.K_RETURN and can_start:
                    session.request_start()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "back"
                if start_rect.collidepoint(event.pos) and can_start:
                    session.request_start()

        screen.fill((7, 8, 20))
        title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width // 2, 72)))

        panel = pygame.Rect(width // 2 - 300, 125, 600, min(height - 225, 390))
        pygame.draw.rect(screen, (17, 20, 35), panel, border_radius=18)
        pygame.draw.rect(screen, (80, 100, 130), panel, 2, border_radius=18)

        y = panel.y + 28
        header = font.render(f"Verbunden: {len(players)} / {max_players}", True, (160, 200, 230))
        screen.blit(header, (panel.x + 24, y))
        y += 44

        for index, player in enumerate(players, start=1):
            row = pygame.Rect(panel.x + 20, y, panel.width - 40, 42)
            if str(player.get("id")) == str(session.local_id):
                pygame.draw.rect(screen, (0, 130, 200, 55), row, border_radius=8)
            name = str(player.get("name") or "Spieler")
            host_text = "  HOST" if str(player.get("id")) == str(session.host_id) else ""
            ready_text = "  • bereit" if session.phase == "setup" and player.get("ready") else ""
            label = font.render(f"{index}. {name}{host_text}{ready_text}", True, (235, 235, 240))
            screen.blit(label, (row.x + 12, row.centery - label.get_height() // 2))
            y += 50
            if y > panel.bottom - 45:
                break

        status_surface = small_font.render(status, True, (180, 190, 205))
        screen.blit(status_surface, status_surface.get_rect(center=(width // 2, panel.bottom - 22)))

        _draw_button(screen, back_rect, "Zurück", font, back_rect.collidepoint(mouse))
        _draw_button(screen, start_rect, "START", font, start_rect.collidepoint(mouse), enabled=can_start)
        if not session.is_host():
            hint = small_font.render("Der Host startet das Spiel." if not start_requires_full or len(players) == max_players else f"Warte auf {max_players - len(players)} weiteren Spieler.", True, (160, 165, 180))
            screen.blit(hint, hint.get_rect(center=(width // 2, height - 102)))

        pygame.display.flip()
        clock.tick(60)


def local_pvp_player_prompt(screen, clock, width, height, player_number):
    """Explain which local player is selecting before faction/ship menus."""
    font = get_font(max(30, int(min(width, height) * 0.055)))
    title_font = get_font(max(46, int(min(width, height) * 0.09)))
    small_font = get_font(max(22, int(min(width, height) * 0.032)))
    if player_number == 1:
        title = "SPIELER 1"
        controls = "A / D = Bewegen     W = Laser     S = Torpedo"
        accent = (120, 220, 255)
    else:
        title = "SPIELER 2"
        controls = "← / → = Bewegen     ↑ = Laser     ↓ = Torpedo"
        accent = (255, 170, 170)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return True

        screen.fill((7, 8, 20))
        title_surface = title_font.render(title, True, accent)
        screen.blit(title_surface, title_surface.get_rect(center=(width // 2, int(height * 0.30))))
        subtitle = font.render("Wähle danach Fraktion und Schiff", True, (235, 240, 248))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.45))))
        control_surface = small_font.render(controls, True, (190, 200, 220))
        screen.blit(control_surface, control_surface.get_rect(center=(width // 2, int(height * 0.56))))
        hint = small_font.render("ENTER / LEERTASTE = Auswahl starten    ESC = Zurück", True, (150, 160, 175))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 45)))
        pygame.display.flip()
        clock.tick(60)
