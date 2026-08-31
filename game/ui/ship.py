import sys

import pygame

from game.assets import set_window_icon


def ship_selection(screen, clock, width, height, faction, faction_logo_img, x_wing_img, millennium_falcon_img, tie_fighter_img, battle_droid_img):
    """Display the ship selection screen for the chosen faction and return the chosen ship key plus the active window size."""
    while True:
        card_width = int(width * 0.30)
        card_height = int(height * 0.50)

        card_top = int(height * 0.32)
        gap = int(width * 0.04)

        if faction == "rebels":
            xwing_rect = pygame.Rect(int(width * 0.5 - card_width - gap / 2), card_top, card_width, card_height)
            falcon_rect = pygame.Rect(int(width * 0.5 + gap / 2), card_top, card_width, card_height)
            tie_rect = None
            battle_rect = None
            title_text = "REBELLEN - SCHIFF AUSWÄHLEN"
            subtitle_text = "Wähle dein Schiff für die Mission"
            key_mapping = {pygame.K_1: "xwing", pygame.K_2: "milleniumfalcon"}
        else:
            xwing_rect = None
            falcon_rect = None
            tie_rect = pygame.Rect(int(width * 0.5 - card_width - gap / 2), card_top, card_width, card_height)
            battle_rect = pygame.Rect(int(width * 0.5 + gap / 2), card_top, card_width, card_height)
            title_text = "IMPERIUM - SCHIFF AUSWÄHLEN"
            subtitle_text = "Wähle dein Schiff für die Mission"
            key_mapping = {pygame.K_1: "tiefighter", pygame.K_2: "battledroid"}

        font = pygame.font.Font(None, max(24, int(min(width, height) * 0.05)))
        small_font = pygame.font.Font(None, max(18, int(min(width, height) * 0.035)))
        title_font = pygame.font.Font(None, max(26, int(min(width, height) * 0.065)))

        mouse_pos = pygame.mouse.get_pos()
        xwing_hover = xwing_rect.collidepoint(mouse_pos) if xwing_rect else False
        falcon_hover = falcon_rect.collidepoint(mouse_pos) if falcon_rect else False
        tie_hover = tie_rect.collidepoint(mouse_pos) if tie_rect else False
        battle_hover = battle_rect.collidepoint(mouse_pos) if battle_rect else False

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
                    return key_mapping[event.key], width, height

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if xwing_rect and xwing_rect.collidepoint(event.pos):
                    return "xwing", width, height
                if falcon_rect and falcon_rect.collidepoint(event.pos):
                    return "milleniumfalcon", width, height
                if tie_rect and tie_rect.collidepoint(event.pos):
                    return "tiefighter", width, height
                if battle_rect and battle_rect.collidepoint(event.pos):
                    return "battledroid", width, height

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

            desired_width = int(card_width * (0.50 if battle_hover else 0.40))
            orig_width = battle_droid_img.get_width()
            droid_scale = (desired_width / orig_width) if orig_width > 0 else (0.30 * base_scale)
            droid_preview = pygame.transform.scale_by(battle_droid_img, droid_scale)

            pygame.draw.rect(screen, (30, 30, 40), battle_rect, border_radius=20)
            pygame.draw.rect(screen, (180, 120, 80) if battle_hover else (120, 120, 120), battle_rect, 3, border_radius=20)
            screen.blit(droid_preview, (battle_rect.centerx - droid_preview.get_width() // 2, battle_rect.y + int(height * 0.05)))
            droid_text = font.render("Battle Droid", True, (255, 255, 255))
            screen.blit(droid_text, (battle_rect.centerx - droid_text.get_width() // 2, battle_rect.bottom - 70))

            info = small_font.render("Klicke auf ein Schiff oder drücke 1 oder 2", True, (220, 220, 220))
            screen.blit(info, (width // 2 - info.get_width() // 2, height - 50))

        pygame.display.flip()
        clock.tick(60)
