import sys

import pygame
from game.assets import get_font

from game.assets import set_window_icon
from game.constants import BLACK
from game.highscore import load_highscore, save_highscore


def death_screen(screen, clock, score, WIDTH, HEIGHT):
    """Show death screen and return True to restart or False to quit.

    The function loads the personal highscore from disk, updates it if the
    current score is higher and persists the new record. The death screen
    displays the current points and the personal record.
    """
    personal_record = load_highscore()
    new_record = False
    if score > personal_record:
        personal_record = score
        try:
            save_highscore(personal_record)
            new_record = True
        except Exception:
            new_record = False

    while True:
        title_font = get_font(int(HEIGHT * 0.16))
        score_font = get_font(int(HEIGHT * 0.10))
        button_font = get_font(int(HEIGHT * 0.06))
        small_font = get_font(max(14, int(HEIGHT * 0.035)))

        # Alle Positionen relativ zur Fenstergroesse (funktioniert auch bei kleinen Fenstern)
        button_width = min(350, WIDTH - 40)
        card_width = min(400, WIDTH - 40)
        restart_rect = pygame.Rect(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.62), button_width, int(HEIGHT * 0.10))
        quit_rect = pygame.Rect(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.75), button_width, int(HEIGHT * 0.10))
        score_card = pygame.Rect(WIDTH // 2 - card_width // 2, int(HEIGHT * 0.29), card_width, int(HEIGHT * 0.30))

        mouse_pos = pygame.mouse.get_pos()
        restart_hover = restart_rect.collidepoint(mouse_pos)
        quit_hover = quit_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                WIDTH = max(480, event.w)
                HEIGHT = max(360, event.h)
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

        title = title_font.render("GAME OVER", True, (255, 80, 80))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.06)))

        pygame.draw.rect(screen, (40, 40, 70), score_card, border_radius=20)
        pygame.draw.rect(screen, (255, 180, 0), score_card, 3, border_radius=20)

        score_title = small_font.render("DEINE PUNKTZAHL", True, (180, 180, 180))
        score_text = score_font.render(str(score), True, (255, 255, 255))

        record_title = small_font.render("PERSÖNLICHER REKORD", True, (180, 180, 180))
        record_text = small_font.render(str(personal_record), True, (255, 255, 255))

        screen.blit(score_title, (WIDTH // 2 - score_title.get_width() // 2, score_card.y + int(HEIGHT * 0.02)))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, score_card.y + int(HEIGHT * 0.06)))

        screen.blit(record_title, (WIDTH // 2 - record_title.get_width() // 2, score_card.y + int(HEIGHT * 0.17)))
        screen.blit(record_text, (WIDTH // 2 - record_text.get_width() // 2, score_card.y + int(HEIGHT * 0.215)))

        if new_record:
            badge = small_font.render("NEUER REKORD!", True, (255, 200, 0))
            screen.blit(badge, (WIDTH // 2 - badge.get_width() // 2, score_card.y + int(HEIGHT * 0.26)))

        pygame.draw.rect(screen, (0, 180, 255) if restart_hover else (40, 40, 70), restart_rect, border_radius=20)
        pygame.draw.rect(screen, (120, 220, 255), restart_rect, 3, border_radius=20)
        restart_text = button_font.render("NEUSTART", True, (255, 255, 255))
        screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2, restart_rect.centery - restart_text.get_height() // 2))

        pygame.draw.rect(screen, (200, 60, 60) if quit_hover else (40, 40, 70), quit_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 120, 120), quit_rect, 3, border_radius=20)
        quit_text = button_font.render("BEENDEN", True, (255, 255, 255))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, quit_rect.centery - quit_text.get_height() // 2))

        hint = small_font.render("Mausklick oder R / ESC verwenden", True, (180, 180, 180))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, int(HEIGHT * 0.92)))

        pygame.display.flip()
        clock.tick(60)
