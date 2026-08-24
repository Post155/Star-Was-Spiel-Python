import pygame
import sys
import random

pygame.init()

# Fenster
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Wars")

clock = pygame.time.Clock()

# Farben
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Listen
laser_list = []
asteroid_list = []
torpedo_list = []

# Bilder laden
x_wing_img = pygame.image.load(
    "Pixelarts/x_wing.png"
).convert_alpha()

millennium_falcon_img = pygame.image.load(
    "Pixelarts/millennium.png"
).convert_alpha()

asteroid_images = [
    pygame.image.load(f"Pixelarts/Astroids/frame_{i:02d}.png").convert_alpha()
    for i in range(12)
]

torpedo_img = pygame.image.load(
    "Pixelarts/Torpedo.png"
).convert_alpha()


class Asteroid:

    def __init__(self):

        self.scale = random.choice([0.25, 0.5, 0.75, 1.0])

        self.frame = 0
        self.frame_counter = 0
        self.frame_delay = 5

        self.image = pygame.transform.scale_by(
            asteroid_images[self.frame],
            self.scale
        )

        self.width, self.height = self.image.get_size()

        self.x = random.randint(
            0,
            WIDTH - self.width
        )

        self.y = -self.height

        self.speed = random.randint(2, 8)

    def update(self):

        self.y += self.speed

        self.frame_counter += 1

        if self.frame_counter >= self.frame_delay:

            self.frame_counter = 0

            self.frame = (
                self.frame + 1
            ) % len(asteroid_images)

            self.image = pygame.transform.scale_by(
                asteroid_images[self.frame],
                self.scale
            )

    def draw(self, screen):

        screen.blit(
            self.image,
            (self.x, self.y)
        )

    def get_rect(self):

        return pygame.Rect(
            self.x + self.width * 0.15,
            self.y + self.height * 0.15,
            self.width * 0.7,
            self.height * 0.7
        )


class Laser:

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            x,
            y,
            3,
            20
        )

        self.speed = 15

    def update(self):

        self.rect.y -= self.speed

    def draw(self, screen):

        pygame.draw.rect(
            screen,
            RED,
            self.rect
        )

class Torpedo:

    def __init__(self, x, y):

        self.image = pygame.transform.scale_by(
            torpedo_img,
            0.50
        )

        self.rect = self.image.get_rect(
            center=(x + 4, y + 10)
        )

        self.speed = 10

    def update(self):

        self.rect.y -= self.speed

    def draw(self, screen):

        screen.blit(
            self.image,
            self.rect
        )

class Spieler:

    def __init__(
        self,
        bild,
        fenster_breite,
        fenster_hoehe,
        scale
    ):

        self.show_hitbox = False

        self.image = pygame.transform.scale_by(
            bild,
            scale
        )

        self.width, self.height = self.image.get_size()

        self.x = (
            fenster_breite // 2
            - self.width // 2
        )

        self.y = (
            fenster_hoehe
            - self.height
            - 20
        )

        self.speed = 10

        self.hitbox_offset_x = 0
        self.hitbox_offset_y = 0

    def update_hitbox(self):

        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y

    def move_left(self):

        self.x -= self.speed

        if self.x < 0:
            self.x = 0

        self.update_hitbox()

    def move_right(self):

        self.x += self.speed

        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

        self.update_hitbox()

    def draw(self, screen):

        screen.blit(
            self.image,
            (self.x, self.y)
        )

        if self.show_hitbox:

            pygame.draw.rect(
                screen,
                RED,
                self.hitbox,
                2
            )


class XWing(Spieler):

    def __init__(self, fenster_breite, fenster_hoehe):

        super().__init__(
            x_wing_img,
            fenster_breite,
            fenster_hoehe,
            0.20      # eigener Scale
        )

        self.speed = 12

        self.hitbox_offset_x = self.width * 0.35
        self.hitbox_offset_y = self.height * 0.15

        self.hitbox = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.width * 0.30,
            self.height * 0.70
        )

    def shoot(self):
            laser_list.append(
                Laser(
                    self.x + self.width * 0.18,
                    self.y + self.height * 0.3
                )
            )
        
            laser_list.append(
                Laser(
                    self.x + self.width * 0.82,
                    self.y + self.height * 0.3
                )
            )

    def torpedo(self):

        torpedo_list.append(
            Torpedo(
                self.hitbox.centerx,
                self.y
            )
        )
            
class MillenniumFalcon(Spieler):

    def __init__(self, fenster_breite, fenster_hoehe):

        super().__init__(
            millennium_falcon_img,
            fenster_breite,
            fenster_hoehe,
            0.75      # eigener Scale
        )

        self.speed = 8

        self.hitbox_offset_x = self.width * 0.15
        self.hitbox_offset_y = self.height * 0.15

        self.hitbox = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.width * 0.70,
            self.height * 0.70
        )

    def shoot(self):
        
            laser_list.append(
                Laser(
                    self.x + self.width * 0.43,
                    self.y + self.height * 0.06
                )
            )
        
            laser_list.append(
                Laser(
                    self.x + self.width * 0.58,
                    self.y + self.height * 0.06
                )
            )

    def torpedo(self):
        None  # Placeholder for torpedo functionality for Millennium Falcon 

running = True

# =========================
# Schiffsauswahl
# =========================

spieler = None
running = False
schiffauswahl = True

font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 70)

# Karten
xwing_rect = pygame.Rect(80, 140, 280, 320)
falcon_rect = pygame.Rect(440, 140, 280, 320)

while schiffauswahl:

    mouse_pos = pygame.mouse.get_pos()

    xwing_hover = xwing_rect.collidepoint(mouse_pos)
    falcon_hover = falcon_rect.collidepoint(mouse_pos)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Tastatur
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                spieler = XWing(WIDTH, HEIGHT)
                schiffauswahl = False
                running = True

            elif event.key == pygame.K_2:
                spieler = MillenniumFalcon(WIDTH, HEIGHT)
                schiffauswahl = False
                running = True

        # Maus
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                if xwing_rect.collidepoint(event.pos):
                    spieler = XWing(WIDTH, HEIGHT)
                    schiffauswahl = False
                    running = True

                elif falcon_rect.collidepoint(event.pos):
                    spieler = MillenniumFalcon(WIDTH, HEIGHT)
                    schiffauswahl = False
                    running = True

    # =========================
    # Hintergrund
    # =========================

    screen.fill((8, 8, 20))

    # Titel
    titel = title_font.render(
        "SCHIFF AUSWÄHLEN",
        True,
        (255, 255, 255)
    )

    screen.blit(
        titel,
        (
            WIDTH // 2 - titel.get_width() // 2,
            40
        )
    )

    subtitle = small_font.render(
        "Wähle dein Schiff für die Mission",
        True,
        (180, 180, 180)
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2 - subtitle.get_width() // 2,
            105
        )
    )

    # =========================
    # X-WING
    # =========================

    xwing_scale = 0.24 if xwing_hover else 0.20

    xwing_preview = pygame.transform.scale_by(
        x_wing_img,
        xwing_scale
    )

    card_color = (40, 40, 70)

    pygame.draw.rect(
        screen,
        card_color,
        xwing_rect,
        border_radius=20
    )

    pygame.draw.rect(
        screen,
        (0, 180, 255) if xwing_hover else (120, 120, 120),
        xwing_rect,
        3,
        border_radius=20
    )

    screen.blit(
        xwing_preview,
        (
            xwing_rect.centerx - xwing_preview.get_width() // 2,
            xwing_rect.y + 60
        )
    )

    text = font.render(
        "X-Wing",
        True,
        (255, 255, 255)
    )

    screen.blit(
        text,
        (
            xwing_rect.centerx - text.get_width() // 2,
            xwing_rect.bottom - 70
        )
    )

    # =========================
    # FALCON
    # =========================

    falcon_scale = 0.75 if falcon_hover else 0.65

    falcon_preview = pygame.transform.scale_by(
        millennium_falcon_img,
        falcon_scale
    )

    pygame.draw.rect(
        screen,
        card_color,
        falcon_rect,
        border_radius=20
    )

    pygame.draw.rect(
        screen,
        (255, 180, 0) if falcon_hover else (120, 120, 120),
        falcon_rect,
        3,
        border_radius=20
    )

    screen.blit(
        falcon_preview,
        (
            falcon_rect.centerx - falcon_preview.get_width() // 2,
            falcon_rect.y + 10
        )
    )

    text = font.render(
        "Millennium Falcon",
        True,
        (255, 255, 255)
    )

    screen.blit(
        text,
        (
            falcon_rect.centerx - text.get_width() // 2,
            falcon_rect.bottom - 70
        )
    )

    # =========================
    # Hinweis
    # =========================

    info = small_font.render(
        "Klicke auf ein Schiff oder drücke 1 bzw. 2",
        True,
        (220, 220, 220)
    )

    screen.blit(
        info,
        (
            WIDTH // 2 - info.get_width() // 2,
            HEIGHT - 50
        )
    )

    pygame.display.flip()
    clock.tick(60)

asteroid_spawn_timer = 0

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_h:
                spieler.show_hitbox = not spieler.show_hitbox
    
            if event.key == pygame.K_1:
                spieler = XWing(WIDTH, HEIGHT)
                schiffauswahl = False
                running = True

            elif event.key == pygame.K_2:
                spieler = MillenniumFalcon(WIDTH, HEIGHT)
                schiffauswahl = False
                running = True

            if event.key in (
                pygame.K_SPACE,
                pygame.K_w,
                pygame.K_UP
            ):
                spieler.shoot()

            if event.key in (
                pygame.K_s,
                pygame.K_DOWN
            ):
                spieler.torpedo()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        spieler.move_left()

    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        spieler.move_right()

    if keys[pygame.K_ESCAPE]:
        running = False

    # Laser bewegen
    for laser in laser_list[:]:

        laser.update()

        if laser.rect.bottom < 0:
            laser_list.remove(laser)

    # Torpedo bewegen
    for torpedo in torpedo_list[:]:

        torpedo.update()

        if torpedo.rect.bottom < 0:
            torpedo_list.remove(torpedo)

    # Asteroiden erzeugen
    asteroid_spawn_timer += 1

    if asteroid_spawn_timer >= 60:

        asteroid_list.append(
            Asteroid()
        )

        asteroid_spawn_timer = 0

    # Asteroiden bewegen
    for asteroid in asteroid_list[:]:

        asteroid.update()

        if asteroid.y > HEIGHT:
            asteroid_list.remove(asteroid)

    # Laser trifft Asteroid
    for asteroid in asteroid_list[:]:

        for laser in laser_list[:]:

            if asteroid.get_rect().colliderect(
                laser.rect
            ):

                if asteroid in asteroid_list:
                    asteroid_list.remove(
                        asteroid
                    )

                if laser in laser_list:
                    laser_list.remove(
                        laser
                    )

                break

    for asteroid in asteroid_list[:]:

        for torpedo in torpedo_list[:]:

            if asteroid.get_rect().colliderect(
                torpedo.rect
            ):

                asteroid_list.remove(asteroid)
                torpedo_list.remove(torpedo)

                break

    # Asteroid trifft Spieler
    for asteroid in asteroid_list[:]:

        if asteroid.get_rect().colliderect(
            spieler.hitbox
        ):

            print("GAME OVER")
            running = False

    # Zeichnen
    screen.fill(BLACK)

    spieler.draw(screen)

    for laser in laser_list:
        laser.draw(screen)

    for torpedo in torpedo_list:
        torpedo.draw(screen)

    for asteroid in asteroid_list:
        asteroid.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()