import sys

import pygame

from game.assets import set_window_icon


def faction_selection(screen, clock, width, height, rebel_logo_img, empire_logo_img):
    """Show the faction choice and return either 'rebels' or 'empire'."""
    while True:
        card_width = int(width * 0.32)
        card_height = int(height * 0.45)
        rebel_rect = pygame.Rect(int(width * 0.15), int(height * 0.28), card_width, card_height)
        empire_rect = pygame.Rect(int(width * 0.53), int(height * 0.28), card_width, card_height)

        font = pygame.font.Font(None, max(24, int(min(width, height) * 0.05)))
        small_font = pygame.font.Font(None, max(18, int(min(width, height) * 0.035)))
        title_font = pygame.font.Font(None, max(28, int(min(width, height) * 0.08)))

        mouse_pos = pygame.mouse.get_pos()
        rebel_hover = rebel_rect.collidepoint(mouse_pos)
        empire_hover = empire_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                set_window_icon()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "rebels"
                if event.key == pygame.K_2:
                    return "empire"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rebel_rect.collidepoint(event.pos):
                    return "rebels"
                if empire_rect.collidepoint(event.pos):
                    return "empire"

        screen.fill((8, 8, 20))

        title = title_font.render("Fraktions Auswahl", True, (255, 255, 255))
        screen.blit(title, (width // 2 - title.get_width() // 2, 40))

        subtitle = small_font.render("Wähle deine Seite", True, (180, 180, 180))
        screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, 105))

        for rect, fill_color, border_color, label, accent, logo_img, logo_text in [
            (rebel_rect, (22, 58, 86), (0, 180, 255), "REBELLEN", (0, 180, 255), rebel_logo_img, "X-Wing / Millennium Falcon"),
            (empire_rect, (52, 30, 48), (200, 120, 120), "IMPERIUM", (200, 120, 120), empire_logo_img, "TIE Fighter / Battle Droid"),
        ]:
            pygame.draw.rect(screen, fill_color, rect, border_radius=22)
            pygame.draw.rect(screen, border_color if (rebel_hover if rect == rebel_rect else empire_hover) else (120, 120, 120), rect, 4, border_radius=22)

            label_text = font.render(label, True, (255, 255, 255))
            screen.blit(label_text, (rect.centerx - label_text.get_width() // 2, rect.y + 25))

            logo_scale = 0.45 if rect == rebel_rect else 0.42
            logo = pygame.transform.smoothscale_by(logo_img, logo_scale)
            screen.blit(logo, (rect.centerx - logo.get_width() // 2, rect.y + 70))

        info = small_font.render("Klicke auf eine Fraktion oder drücke 1 oder 2", True, (220, 220, 220))
        screen.blit(info, (width // 2 - info.get_width() // 2, height - 50))

        pygame.display.flip()
        clock.tick(60)
