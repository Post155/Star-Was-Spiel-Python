"""Multiplayer live scoreboard overlay."""
from __future__ import annotations

import pygame


def draw_scoreboard(screen: pygame.Surface, players: list[dict], local_id: str | None) -> None:
    width, height = screen.get_size()
    row_h = max(30, int(min(width, height) * 0.055))
    header_h = row_h + 16
    max_rows = min(len(players), 10)
    panel_w = min(width - 60, max(480, int(width * 0.70)))
    panel_h = header_h + (max_rows + 1) * row_h + 20
    panel = pygame.Rect((width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h)

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, (17, 20, 35), panel, border_radius=18)
    pygame.draw.rect(screen, (120, 210, 255), panel, 2, border_radius=18)

    title_font = pygame.font.Font(None, max(28, int(height * 0.055)))
    text_font = pygame.font.Font(None, max(22, int(height * 0.036)))
    small_font = pygame.font.Font(None, max(18, int(height * 0.028)))

    title = title_font.render("MULTIPLAYER SCORE", True, (255, 255, 255))
    screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 14))

    top = panel.y + header_h
    pygame.draw.line(screen, (100, 120, 150), (panel.x + 18, top), (panel.right - 18, top), 1)

    columns = [panel.x + 24, panel.x + 82, panel.x + int(panel_w * 0.52), panel.right - 96]
    headers = [("#", columns[0]), ("Spieler", columns[1]), ("Punkte", columns[2]), ("Status", columns[3])]
    for text, x in headers:
        surface = small_font.render(text, True, (170, 185, 205))
        screen.blit(surface, (x, top + 8))

    for index, player in enumerate(players[:max_rows], start=1):
        y = top + row_h + (index - 1) * row_h
        is_local = str(player.get("id")) == str(local_id)
        if is_local:
            highlight = pygame.Surface((panel_w - 32, row_h - 3), pygame.SRCALPHA)
            highlight.fill((0, 150, 255, 35))
            screen.blit(highlight, (panel.x + 16, y - 2))

        name = str(player.get("name") or "Spieler")[:22]
        score = f"{max(0, int(player.get('score', 0))):,}".replace(",", ".")
        alive = bool(player.get("alive", True))
        status = "LIVE" if alive else "GAME OVER"
        text_color = (255, 255, 255) if alive else (160, 165, 175)
        if is_local:
            text_color = (170, 235, 255)

        values = [
            (str(index), columns[0], text_color),
            (name, columns[1], text_color),
            (score, columns[2], text_color),
            (status, columns[3], (120, 240, 150) if alive else (255, 145, 145)),
        ]
        for value, x, color in values:
            surface = text_font.render(value, True, color)
            screen.blit(surface, (x, y))
