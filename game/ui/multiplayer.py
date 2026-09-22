"""Pygame menus for LAN multiplayer."""
from __future__ import annotations

import pygame

from game.network import LAN_PORT


def _draw_button(screen, rect, text, font, hover=False, enabled=True):
    fill = (0, 150, 220) if hover and enabled else (36, 42, 62)
    border = (120, 220, 255) if enabled else (90, 90, 90)
    text_color = (255, 255, 255) if enabled else (130, 130, 130)
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, 2, border_radius=14)
    label = font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))


def _input_field(screen, rect, text, font, active):
    pygame.draw.rect(screen, (20, 24, 40), rect, border_radius=10)
    pygame.draw.rect(screen, (0, 180, 255) if active else (100, 110, 130), rect, 2, border_radius=10)
    label = font.render(text or "", True, (240, 240, 245))
    screen.blit(label, (rect.x + 12, rect.centery - label.get_height() // 2))


def main_menu(screen, clock, width, height):
    """Return singleplayer, multiplayer, pvp_duel or quit."""
    font = pygame.font.Font(None, max(28, int(min(width, height) * 0.055)))
    title_font = pygame.font.Font(None, max(42, int(min(width, height) * 0.10)))
    buttons = [
        (pygame.Rect(width // 2 - 180, int(height * 0.32), 360, 64), "Einzelspieler", "singleplayer"),
        (pygame.Rect(width // 2 - 180, int(height * 0.43), 360, 64), "LAN Multiplayer", "multiplayer"),
        (pygame.Rect(width // 2 - 180, int(height * 0.54), 360, 64), "PvP-Duell", "pvp_duel"),
        (pygame.Rect(width // 2 - 180, int(height * 0.65), 360, 64), "Beenden", "quit"),
    ]
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
                if event.key == pygame.K_1:
                    return "singleplayer"
                if event.key == pygame.K_2:
                    return "multiplayer"
                if event.key == pygame.K_3:
                    return "pvp_duel"
                if event.key == pygame.K_ESCAPE:
                    return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, _, value in buttons:
                    if rect.collidepoint(event.pos):
                        return value

        screen.fill((7, 8, 20))
        title = title_font.render("STAR WARS", True, (255, 255, 255))
        subtitle = font.render("KI-RAUMSCHIFFKAMPF", True, (150, 190, 220))
        screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.18))))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.27))))
        for rect, text, _ in buttons:
            _draw_button(screen, rect, text, font, rect.collidepoint(mouse))
        hint = pygame.font.Font(None, 22).render("1 = Einzelspieler   2 = LAN   3 = PvP-Duell   ESC = Beenden", True, (150, 155, 170))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 34)))
        pygame.display.flip()
        clock.tick(60)


def lan_menu(screen, clock, width, height):
    """Return {'action': 'host'/'join', 'name': ..., 'ip': ...} or None."""
    font = pygame.font.Font(None, 34)
    title_font = pygame.font.Font(None, max(38, int(min(width, height) * 0.08)))
    small_font = pygame.font.Font(None, 24)
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
        screen.blit(pygame.font.Font(None, 24).render(f"Port: {LAN_PORT}", True, (150, 160, 180)), (width // 2 - 45, 125))

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
    font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, max(42, int(min(width, height) * 0.08)))
    small_font = pygame.font.Font(None, 24)
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
        subtitle = small_font.render("Zwei Spieler • keine KI • identische Asteroidenwelt", True, (165, 185, 215))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.27))))
        for rect, text, _ in buttons:
            _draw_button(screen, rect, text, font, rect.collidepoint(mouse))
        hint = small_font.render("1 = Letzter Überlebender   2 = Punktekampf", True, (145, 150, 165))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 34)))
        pygame.display.flip()
        clock.tick(60)


def pvp_lan_menu(screen, clock, width, height, duel_mode):
    """LAN host/join menu for the PvP duel."""
    font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, max(40, int(min(width, height) * 0.075)))
    small_font = pygame.font.Font(None, 24)
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
        title = title_font.render(f"PvP-DUELL – {mode_name}", True, (255, 255, 255))
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
    font = pygame.font.Font(None, 30)
    title_font = pygame.font.Font(None, max(42, int(min(width, height) * 0.085)))
    small_font = pygame.font.Font(None, 24)
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
