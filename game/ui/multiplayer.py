"""Pygame menus for LAN multiplayer."""
from __future__ import annotations

import math

import pygame
from game.assets import get_font, load_assets
from game.background import BackgroundManager

from game.network import LAN_PORT

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
    """Render the cinematic space background from the existing background system."""
    background.resize(width, height)
    background.starfield.update()
    background.planet_manager.maybe_spawn(True)
    background.planet_manager.update()
    background.starfield.draw(screen)
    background.planet_manager.draw(screen)

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((3, 7, 20, 65))
    screen.blit(overlay, (0, 0))

    inner_vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(14, 0, -1):
        radius = max(20, width // 7 + i * 18)
        pygame.draw.circle(inner_vignette, (0, 0, 0, max(0, 90 - i * 4)), (width // 2, height // 2), radius)
    screen.blit(inner_vignette, (0, 0))


def _draw_faction_badge(screen, image, rect, accent_color, label=None):
    glow = pygame.Surface((rect.width + 58, rect.height + 58), pygame.SRCALPHA)
    glow_rect = glow.get_rect(center=rect.center)
    pygame.draw.ellipse(glow, accent_color + (72,), glow.get_rect().inflate(-12, -12))
    screen.blit(glow, glow_rect)

    scaled = pygame.transform.smoothscale(image, (rect.width, rect.height))
    screen.blit(scaled, scaled.get_rect(center=rect.center))

    frame = rect.inflate(8, 8)
    pygame.draw.rect(screen, accent_color, frame, 2, border_radius=20)
    if label:
        label_surf = get_font(max(16, int(rect.height * 0.14)), "sci_fi").render(label, True, (245, 247, 255))
        screen.blit(label_surf, label_surf.get_rect(midbottom=(rect.centerx, rect.bottom + 24)))


def main_menu(screen, clock, width, height):
    """Show the cinematic main menu with faction-led styling and four actions."""
    background = BackgroundManager(width, height, MENU_ASSETS)
    font = get_font(max(26, int(min(width, height) * 0.052)), "sci_fi")
    title_font = get_font(max(54, int(min(width, height) * 0.12)), "sci_fi")
    subtitle_font = get_font(max(18, int(min(width, height) * 0.028)), "sci_fi")

    button_y = int(height * 0.56)
    buttons = [
        (pygame.Rect(width // 2 - 220, button_y, 440, 64), "Einzelspieler", "singleplayer", (66, 153, 255)),
        (pygame.Rect(width // 2 - 220, button_y + 80, 440, 64), "Mehrspieler", "multiplayer", (228, 72, 72)),
        (pygame.Rect(width // 2 - 220, button_y + 160, 440, 64), "Einstellungen", "settings", (72, 178, 255)),
        (pygame.Rect(width // 2 - 220, button_y + 240, 440, 64), "Beenden", "quit", (164, 172, 186)),
    ]
    settings_open = False

    while True:
        mouse = pygame.mouse.get_pos()

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
                    continue
                if event.key == pygame.K_1:
                    return "singleplayer"
                if event.key == pygame.K_2:
                    return "multiplayer"
                if event.key == pygame.K_3:
                    settings_open = True
                if event.key == pygame.K_4 or event.key == pygame.K_ESCAPE:
                    return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if settings_open:
                    panel = pygame.Rect(width // 2 - 260, height // 2 - 120, 520, 240)
                    close_rect = pygame.Rect(width // 2 + 120, height // 2 + 50, 120, 42)
                    if close_rect.collidepoint(event.pos):
                        settings_open = False
                    continue

                for rect, _, value, _ in buttons:
                    if rect.collidepoint(event.pos):
                        if value == "settings":
                            settings_open = True
                            break
                        return value

        _draw_menu_background(screen, width, height, background)

        logo_w = max(150, int(width * 0.18))
        logo_h = max(110, int(height * 0.22))
        rebel_rect = pygame.Rect(int(width * 0.19) - logo_w // 2, int(height * 0.18), logo_w, logo_h)
        empire_rect = pygame.Rect(int(width * 0.81) - logo_w // 2, int(height * 0.18), logo_w, logo_h)
        rebel_logo = MENU_ASSETS.get("rebel_logo_img")
        empire_logo = MENU_ASSETS.get("empire_logo_img")
        if rebel_logo:
            _draw_faction_badge(screen, rebel_logo, rebel_rect, (66, 153, 255), "REBELLEN")
        if empire_logo:
            _draw_faction_badge(screen, empire_logo, empire_rect, (255, 80, 80), "IMPERIUM")

        pulse = 1.0 + 0.04 * math.sin(pygame.time.get_ticks() / 350.0)
        title_surface = title_font.render("STAR WARS", True, (245, 248, 255))
        scaled_title = pygame.transform.smoothscale(
            title_surface,
            (
                max(120, int(title_surface.get_width() * pulse)),
                max(40, int(title_surface.get_height() * pulse)),
            ),
        )
        title_rect = scaled_title.get_rect(center=(width // 2, int(height * 0.19)))
        screen.blit(scaled_title, title_rect)

        subtitle = subtitle_font.render("KI-RAUMSCHIFFKAMPF", True, (180, 205, 227))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.31))))

        if settings_open:
            panel = pygame.Rect(width // 2 - 260, height // 2 - 120, 520, 240)
            panel_surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (10, 15, 24, 220), panel_surface.get_rect(), border_radius=20)
            pygame.draw.rect(panel_surface, (90, 150, 255, 160), panel_surface.get_rect(), 2, border_radius=20)
            screen.blit(panel_surface, panel.topleft)

            title = get_font(26, "sci_fi").render("EINSTELLUNGEN", True, (235, 240, 255))
            screen.blit(title, title.get_rect(midtop=(width // 2, height // 2 - 90)))
            audio = get_font(20, "sci_fi").render("Audio: Aktiviert", True, (180, 220, 255))
            screen.blit(audio, audio.get_rect(midtop=(width // 2, height // 2 - 46)))
            graphics = get_font(20, "sci_fi").render("Grafik: Hoch", True, (255, 170, 170))
            screen.blit(graphics, graphics.get_rect(midtop=(width // 2, height // 2 - 10)))
            close_rect = pygame.Rect(width // 2 + 120, height // 2 + 50, 120, 42)
            _draw_button(screen, close_rect, "Zurück", get_font(20, "sci_fi"), close_rect.collidepoint(mouse), accent=(90, 180, 255))
        else:
            for rect, text, _, accent in buttons:
                _draw_button(screen, rect, text, font, rect.collidepoint(mouse), accent=accent, glow_scale=1.04)

        hint = get_font(20, "sci_fi").render(
            "1 = EINZELSPIELER   2 = MEHRSPIELER   3 = EINSTELLUNGEN   4 = BEENDEN",
            True,
            (168, 180, 198),
        )
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 36)))
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
