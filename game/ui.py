import pygame
import sys

from game.assets import set_window_icon
from game.constants import BLACK


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
            (empire_rect, (52, 30, 48), (200, 120, 120), "IMPERIUM", (200, 120, 120), empire_logo_img, "TIE Fighter / bald mehr"),
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


def ship_selection(screen, clock, width, height, faction, faction_logo_img, x_wing_img, millennium_falcon_img, tie_fighter_img):
    """Display the ship selection screen for the chosen faction and return the chosen ship key."""
    while True:
        card_width = int(width * 0.30)
        card_height = int(height * 0.50)

        card_top = int(height * 0.32)
        gap = int(width * 0.04)

        if faction == "rebels":
            xwing_rect = pygame.Rect(int(width * 0.5 - card_width - gap / 2), card_top, card_width, card_height)
            falcon_rect = pygame.Rect(int(width * 0.5 + gap / 2), card_top, card_width, card_height)
            tie_rect = None
            upcoming_rect = None
            title_text = "REBELLEN - SCHIFF AUSWÄHLEN"
            subtitle_text = "Wähle dein Schiff für die Mission"
            key_mapping = {pygame.K_1: "xwing", pygame.K_2: "milleniumfalcon"}
        else:
            xwing_rect = None
            falcon_rect = None
            tie_rect = pygame.Rect(int(width * 0.5 - card_width - gap / 2), card_top, card_width, card_height)
            upcoming_rect = pygame.Rect(int(width * 0.5 + gap / 2), card_top, card_width, card_height)
            title_text = "IMPERIUM - SCHIFF AUSWÄHLEN"
            subtitle_text = "Wähle dein Schiff für die Mission"
            key_mapping = {pygame.K_1: "tiefighter"}

        font = pygame.font.Font(None, max(24, int(min(width, height) * 0.05)))
        small_font = pygame.font.Font(None, max(18, int(min(width, height) * 0.035)))
        title_font = pygame.font.Font(None, max(26, int(min(width, height) * 0.065)))

        mouse_pos = pygame.mouse.get_pos()
        xwing_hover = xwing_rect.collidepoint(mouse_pos) if xwing_rect else False
        falcon_hover = falcon_rect.collidepoint(mouse_pos) if falcon_rect else False
        tie_hover = tie_rect.collidepoint(mouse_pos) if tie_rect else False
        upcoming_hover = upcoming_rect.collidepoint(mouse_pos) if upcoming_rect else False

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
                if event.key in key_mapping:
                    return key_mapping[event.key]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if xwing_rect and xwing_rect.collidepoint(event.pos):
                    return "xwing"
                if falcon_rect and falcon_rect.collidepoint(event.pos):
                    return "milleniumfalcon"
                if tie_rect and tie_rect.collidepoint(event.pos):
                    return "tiefighter"

        screen.fill((8, 8, 20))

        faction_logo = pygame.transform.smoothscale_by(faction_logo_img, 0.32)
        screen.blit(faction_logo, (width // 2 - faction_logo.get_width() // 2, 10))

        title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(title, (width // 2 - title.get_width() // 2, 90))

        subtitle = small_font.render(subtitle_text, True, (180, 180, 180))
        screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, 160))

        base_scale = height / 600

        if faction == "rebels":
            xwing_scale = (0.24 * base_scale if xwing_hover else 0.20 * base_scale)
            xwing_preview = pygame.transform.scale_by(x_wing_img, xwing_scale)

            pygame.draw.rect(screen, (40, 40, 70), xwing_rect, border_radius=20)
            pygame.draw.rect(screen, (0, 180, 255) if xwing_hover else (120, 120, 120), xwing_rect, 3, border_radius=20)
            screen.blit(xwing_preview, (xwing_rect.centerx - xwing_preview.get_width() // 2, xwing_rect.y + int(height * 0.08)))
            text = font.render("X-Wing", True, (255, 255, 255))
            screen.blit(text, (xwing_rect.centerx - text.get_width() // 2, xwing_rect.bottom - 70))

            falcon_scale = (0.75 * base_scale if falcon_hover else 0.65 * base_scale)
            falcon_preview = pygame.transform.scale_by(millennium_falcon_img, falcon_scale)

            pygame.draw.rect(screen, (40, 40, 70), falcon_rect, border_radius=20)
            pygame.draw.rect(screen, (255, 180, 0) if falcon_hover else (120, 120, 120), falcon_rect, 3, border_radius=20)
            screen.blit(falcon_preview, (falcon_rect.centerx - falcon_preview.get_width() // 2, falcon_rect.y + int(height * 0.02)))
            text = font.render("Millennium Falcon", True, (255, 255, 255))
            screen.blit(text, (falcon_rect.centerx - text.get_width() // 2, falcon_rect.bottom - 70))

            info = small_font.render("Klicke auf ein Schiff oder drücke 1 oder 2", True, (220, 220, 220))
            screen.blit(info, (width // 2 - info.get_width() // 2, height - 50))
        else:
            desired_width = int(card_width * (1.2 if tie_hover else 1.0))
            orig_width = tie_fighter_img.get_width()
            tie_scale = (desired_width / orig_width) if orig_width > 0 else (0.20 * base_scale)
            tie_preview = pygame.transform.scale_by(tie_fighter_img, tie_scale)

            pygame.draw.rect(screen, (40, 40, 70), tie_rect, border_radius=20)
            pygame.draw.rect(screen, (200, 100, 200) if tie_hover else (120, 120, 120), tie_rect, 3, border_radius=20)
            screen.blit(tie_preview, (tie_rect.centerx - tie_preview.get_width() // 2, tie_rect.y + int(height * 0.06)))
            text = font.render("TIE Fighter", True, (255, 255, 255))
            screen.blit(text, (tie_rect.centerx - text.get_width() // 2, tie_rect.bottom - 70))

            pygame.draw.rect(screen, (30, 30, 40), upcoming_rect, border_radius=20)
            pygame.draw.rect(screen, (120, 120, 120) if not upcoming_hover else (180, 180, 180), upcoming_rect, 3, border_radius=20)
            soon_text = font.render("Bald", True, (180, 180, 180))
            screen.blit(soon_text, (upcoming_rect.centerx - soon_text.get_width() // 2, upcoming_rect.centery - 20))
            soon_text_2 = small_font.render("verfügbar", True, (180, 180, 180))
            screen.blit(soon_text_2, (upcoming_rect.centerx - soon_text_2.get_width() // 2, upcoming_rect.centery + 25))

            info = small_font.render("Klicke auf TIE Fighter oder drücke 1", True, (220, 220, 220))
            screen.blit(info, (width // 2 - info.get_width() // 2, height - 50))

        pygame.display.flip()
        clock.tick(60)


def death_screen(screen, clock, score, WIDTH, HEIGHT):
    """Show death screen and return True to restart or False to quit."""
    while True:
        title_font = pygame.font.Font(None, int(HEIGHT * 0.16))
        score_font = pygame.font.Font(None, int(HEIGHT * 0.10))
        button_font = pygame.font.Font(None, int(HEIGHT * 0.06))
        small_font = pygame.font.Font(None, int(HEIGHT * 0.03))

        restart_rect = pygame.Rect(WIDTH // 2 - 175, 350, 350, 70)
        quit_rect = pygame.Rect(WIDTH // 2 - 175, 450, 350, 70)

        mouse_pos = pygame.mouse.get_pos()
        restart_hover = restart_rect.collidepoint(mouse_pos)
        quit_hover = quit_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                WIDTH = event.w
                HEIGHT = event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                set_window_icon()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_rect.collidepoint(event.pos):
                    return True
                if quit_rect.collidepoint(event.pos):
                    return False

        screen.fill(BLACK)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = title_font.render("GAME OVER", True, (255, 80, 80))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        score_card = pygame.Rect(WIDTH // 2 - 200, 180, 400, 120)
        pygame.draw.rect(screen, (40, 40, 70), score_card, border_radius=20)
        pygame.draw.rect(screen, (255, 180, 0), score_card, 3, border_radius=20)

        score_title = small_font.render("DEINE PUNKTZAHL", True, (180, 180, 180))
        score_text = score_font.render(str(score), True, (255, 255, 255))

        screen.blit(score_title, (WIDTH // 2 - score_title.get_width() // 2, 200))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 235))

        pygame.draw.rect(screen, (0, 180, 255) if restart_hover else (40, 40, 70), restart_rect, border_radius=20)
        pygame.draw.rect(screen, (120, 220, 255), restart_rect, 3, border_radius=20)
        restart_text = button_font.render("NEUSTART", True, (255, 255, 255))
        screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2, restart_rect.centery - restart_text.get_height() // 2))

        pygame.draw.rect(screen, (200, 60, 60) if quit_hover else (40, 40, 70), quit_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 120, 120), quit_rect, 3, border_radius=20)
        quit_text = button_font.render("BEENDEN", True, (255, 255, 255))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, quit_rect.centery - quit_text.get_height() // 2))

        hint = small_font.render("Mausklick oder R / ESC verwenden", True, (180, 180, 180))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 550))

        pygame.display.flip()
        clock.tick(60)
