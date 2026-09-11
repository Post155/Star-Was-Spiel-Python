import sys
import pygame
from game.assets import set_window_icon


DIFFICULTIES = [
    ("easy", "Einfach", "Weniger und langsamere Gegner"),
    ("normal", "Normal", "Ausgewogene Herausforderung"),
    ("hard", "Schwer", "Stärkere und aggressivere Gegner"),
    ("expert", "Experte", "Für erfahrene Spieler"),
]


def difficulty_selection(screen, clock, width, height, default="normal"):
    """Select the game difficulty before the ship selection."""
    selected = next((i for i, item in enumerate(DIFFICULTIES) if item[0] == default), 1)

    while True:
        font = pygame.font.Font(None, max(28, int(min(width, height) * 0.055)))
        small = pygame.font.Font(None, max(20, int(min(width, height) * 0.033)))
        title = pygame.font.Font(None, max(34, int(min(width, height) * 0.075)))

        cards = []
        card_w = int(width * 0.19)
        card_h = int(height * 0.42)
        gap = int(width * 0.025)
        total = 4 * card_w + 3 * gap
        start_x = (width - total) // 2
        y = int(height * 0.30)

        mouse = pygame.mouse.get_pos()
        for i in range(4):
            rect = pygame.Rect(start_x + i * (card_w + gap), y, card_w, card_h)
            cards.append(rect)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                width = max(480, event.w)
                height = max(360, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                set_window_icon()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    selected = event.key - pygame.K_1
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return DIFFICULTIES[selected][0], width, height
                elif event.key == pygame.K_ESCAPE:
                    return DIFFICULTIES[selected][0], width, height
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(cards):
                    if rect.collidepoint(event.pos):
                        selected = i
                        return DIFFICULTIES[selected][0], width, height

        screen.fill((8, 8, 20))
        t = title.render("SCHWIERIGKEIT AUSWÄHLEN", True, (255, 255, 255))
        screen.blit(t, (width // 2 - t.get_width() // 2, 45))

        sub = small.render("Die Schwierigkeit beeinflusst Gegner und Asteroiden.", True, (180, 180, 180))
        screen.blit(sub, (width // 2 - sub.get_width() // 2, 115))

        for i, (key, name, description) in enumerate(DIFFICULTIES):
            rect = cards[i]
            hover = rect.collidepoint(mouse)
            active = i == selected
            fill = (40, 55, 80) if active else (28, 28, 42)
            border = (80, 190, 255) if active else ((150, 150, 160) if hover else (90, 90, 100))
            pygame.draw.rect(screen, fill, rect, border_radius=18)
            pygame.draw.rect(screen, border, rect, 4 if active else 2, border_radius=18)

            n = font.render(str(i + 1), True, (255, 255, 255))
            screen.blit(n, n.get_rect(center=(rect.centerx, rect.y + 48)))

            label = font.render(name, True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(rect.centerx, rect.y + rect.height * 0.48)))

            # Wrap description into two short lines.
            words = description.split()
            lines, line = [], ""
            for word in words:
                test = (line + " " + word).strip()
                if small.size(test)[0] <= rect.width - 20:
                    line = test
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
            for j, text in enumerate(lines[:3]):
                d = small.render(text, True, (190, 190, 200))
                screen.blit(d, d.get_rect(center=(rect.centerx, rect.y + rect.height * 0.68 + j * 25)))

        info = small.render("1–4 auswählen  •  ENTER bestätigen  •  Klicken zum Starten", True, (220, 220, 220))
        screen.blit(info, info.get_rect(center=(width // 2, height - 45)))

        pygame.display.flip()
        clock.tick(60)
