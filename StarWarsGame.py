import pygame
import sys
import random
import os

pygame.init()

score = 0
asteroid_spawn_timer = 0

# Fenster
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.RESIZABLE
)

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
explosion_list = []

# Bilder laden
x_wing_img = pygame.image.load(
    "Pixelarts/x_wing.png"
).convert_alpha()

millennium_falcon_img = pygame.image.load(
    "Pixelarts/millennium.png"
).convert_alpha()

asteroid_images = [
    pygame.image.load("Pixelarts/Astroids/frame_00.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_01.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_02.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_03.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_04.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_05.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_06.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_07.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_08.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_09.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_10.png").convert_alpha(),
    pygame.image.load("Pixelarts/Astroids/frame_11.png").convert_alpha()
]

torpedo_img = pygame.image.load(
    "Pixelarts/Torpedo.png"
).convert_alpha()

Explosion_img = pygame.image.load(
    "Pixelarts/Explosion.png"
).convert_alpha()

class Asteroid:
    base_scale = HEIGHT / 600

    def __init__(self):

        self.scale = random.choice([0.25, 0.5, 0.75, 1.0])

        self.frame = 0
        self.frame_counter = 0
        self.frame_delay = 5

        self.image = pygame.transform.scale_by(
            asteroid_images[self.frame],
            self.scale * (HEIGHT / 600)
        )

        self.width, self.height = self.image.get_size()

        self.x = random.randint(
            0,
            max(0, WIDTH - self.width)
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
    
    def resize(self):

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        self.image = pygame.transform.scale_by(
            asteroid_images[self.frame],
            self.scale * (HEIGHT / 600)
        )

        self.width, self.height = self.image.get_size()

        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2

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

class Explosion:

    def __init__(self, x, y, asteroid_scale):

        self.x = x
        self.y = y

        self.asteroid_scale = asteroid_scale

        self.image = pygame.transform.scale_by(
            Explosion_img,
            self.asteroid_scale * 0.5
        )

        self.rect = self.image.get_rect(
            center=(self.x, self.y)
        )

        self.timer = 20

    def resize(self):

        self.image = pygame.transform.scale_by(
            Explosion_img,
            self.asteroid_scale * 0.5
        )

        self.rect = self.image.get_rect(
            center=(self.x, self.y)
        )

    def update(self):

        self.timer -= 1

        if self.timer <= 0:

            if self in explosion_list:
                explosion_list.remove(self)

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

    def resize(self):
        self.y = HEIGHT - self.height - 20
        self.x = max(
            0,
            min(
                self.x,
                WIDTH - self.width
            )
        )
        self.update_hitbox()

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
        None  # Platzhalter

def death_screen(score):
    global WIDTH
    global HEIGHT
    global screen

    while True:

        title_font = pygame.font.Font(
            None,
            int(HEIGHT * 0.16)
        )

        score_font = pygame.font.Font(
            None,
            int(HEIGHT * 0.10)
        )

        button_font = pygame.font.Font(
            None,
            int(HEIGHT * 0.06)
        )

        small_font = pygame.font.Font(
            None,
            int(HEIGHT * 0.03)
        )

        restart_rect = pygame.Rect(
            WIDTH // 2 - 175,
            350,
            350,
            70
        )

        quit_rect = pygame.Rect(
            WIDTH // 2 - 175,
            450,
            350,
            70
        )

        mouse_pos = pygame.mouse.get_pos()

        restart_hover = restart_rect.collidepoint(mouse_pos)
        quit_hover = quit_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    WIDTH = event.w
                    HEIGHT = event.h

                    screen = pygame.display.set_mode(
                        (WIDTH, HEIGHT),
                        pygame.RESIZABLE
                    )


                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_r:
                        return True

                    if event.key == pygame.K_ESCAPE:
                        return False

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        if restart_rect.collidepoint(event.pos):
                            return True

                        if quit_rect.collidepoint(event.pos):
                            return False

        # Hintergrund
        screen.fill((8, 8, 20))

        # Overlay
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Titel
        title = title_font.render(
            "GAME OVER",
            True,
            (255, 80, 80)
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                60
            )
        )

        # Karte für Punkte
        score_card = pygame.Rect(
            WIDTH // 2 - 200,
            180,
            400,
            120
        )

        pygame.draw.rect(
            screen,
            (40, 40, 70),
            score_card,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            (255, 180, 0),
            score_card,
            3,
            border_radius=20
        )

        score_title = small_font.render(
            "DEINE PUNKTZAHL",
            True,
            (180, 180, 180)
        )

        score_text = score_font.render(
            str(score),
            True,
            (255, 255, 255)
        )

        screen.blit(
            score_title,
            (
                WIDTH // 2 - score_title.get_width() // 2,
                200
            )
        )

        screen.blit(
            score_text,
            (
                WIDTH // 2 - score_text.get_width() // 2,
                235
            )
        )

        # Neustart Button
        pygame.draw.rect(
            screen,
            (0, 180, 255) if restart_hover else (40, 40, 70),
            restart_rect,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            (120, 220, 255),
            restart_rect,
            3,
            border_radius=20
        )

        restart_text = button_font.render(
            "NEUSTART",
            True,
            (255, 255, 255)
        )

        screen.blit(
            restart_text,
            (
                restart_rect.centerx - restart_text.get_width() // 2,
                restart_rect.centery - restart_text.get_height() // 2
            )
        )

        # Beenden Button
        pygame.draw.rect(
            screen,
            (200, 60, 60) if quit_hover else (40, 40, 70),
            quit_rect,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            (255, 120, 120),
            quit_rect,
            3,
            border_radius=20
        )

        quit_text = button_font.render(
            "BEENDEN",
            True,
            (255, 255, 255)
        )

        screen.blit(
            quit_text,
            (
                quit_rect.centerx - quit_text.get_width() // 2,
                quit_rect.centery - quit_text.get_height() // 2
            )
        )

        hint = small_font.render(
            "Mausklick oder R / ESC verwenden",
            True,
            (180, 180, 180)
        )

        screen.blit(
            hint,
            (
                WIDTH // 2 - hint.get_width() // 2,
                550
            )
        )

        pygame.display.flip()
        clock.tick(60)

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

while schiffauswahl:
    card_width = int(WIDTH * 0.30)
    card_height = int(HEIGHT * 0.50)

    xwing_rect = pygame.Rect(
        int(WIDTH * 0.10),
        int(HEIGHT * 0.25),
        card_width,
        card_height
    )

    falcon_rect = pygame.Rect(
        int(WIDTH * 0.60),
        int(HEIGHT * 0.25),
        card_width,
        card_height
    )

    font = pygame.font.Font(
        None,
        int(HEIGHT * 0.05)
    )

    small_font = pygame.font.Font(
        None,
        int(HEIGHT * 0.035)
    )

    title_font = pygame.font.Font(
        None,
        int(HEIGHT * 0.12)
    )

    font = pygame.font.Font(
        None,
        int(HEIGHT * 0.05)
    )

    small_font = pygame.font.Font(
        None,
        int(HEIGHT * 0.035)
    )

    title_font = pygame.font.Font(
        None,
        int(HEIGHT * 0.12)
    )

    mouse_pos = pygame.mouse.get_pos()

    xwing_hover = xwing_rect.collidepoint(mouse_pos)
    falcon_hover = falcon_rect.collidepoint(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:

            WIDTH = event.w
            HEIGHT = event.h

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.RESIZABLE
            )   


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

    base_scale = HEIGHT / 600

    xwing_scale = (
        0.24 * base_scale
        if xwing_hover
        else 0.20 * base_scale
    )

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
            xwing_rect.y + int(HEIGHT * 0.08)
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

    falcon_scale = (
    0.75 * base_scale
    if falcon_hover
    else 0.65 * base_scale
    )

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
            falcon_rect.y + int(HEIGHT * 0.02)
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

while running:

    for event in pygame.event.get():

        if event.type == pygame.VIDEORESIZE:

            WIDTH = event.w
            HEIGHT = event.h

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.RESIZABLE
            )

            if spieler:
                spieler.resize()

            for asteroid in asteroid_list:
                asteroid.resize()

            for explosion in explosion_list:
                explosion.resize()

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
                score += int(asteroid.scale * 100)
                explosion_list.append(
                    Explosion(
                        asteroid.x + asteroid.width // 2,
                        asteroid.y + asteroid.height // 2,
                        asteroid.scale
                    )
                )

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

                score += int(asteroid.scale * 100)

                explosion_list.append(
                    Explosion(
                        asteroid.x + asteroid.width // 2,
                        asteroid.y + asteroid.height // 2,
                        asteroid.scale
                    )
                )

                asteroid_list.remove(asteroid)
                torpedo_list.remove(torpedo)

                break

    # Asteroid trifft Spieler
    for asteroid in asteroid_list[:]:

        if asteroid.get_rect().colliderect(
            spieler.hitbox
        ):
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
    
    for explosion in explosion_list[:]:
        explosion.update()
        explosion.draw(screen)

    score_text = font.render(
        f"Punkte: {score}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        score_text,
        (10, 10)
    )

    pygame.display.flip()

    clock.tick(60)

restart = death_screen(score)

if restart:

    laser_list.clear()
    asteroid_list.clear()
    torpedo_list.clear()
    explosion_list.clear()

    score = 0

    python = sys.executable
    os.execl(
        python,
        python,
        *sys.argv
    )

pygame.quit()
sys.exit()