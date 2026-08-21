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

# Listen
laser_list = []
asteroid_list = []

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

    # Schiff auswählen
    # spieler = XWing(WIDTH, HEIGHT)

    spieler = MillenniumFalcon(WIDTH, HEIGHT)

asteroid_spawn_timer = 0

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_h:
                spieler.show_hitbox = not spieler.show_hitbox

            if event.key in (
                pygame.K_SPACE,
                pygame.K_w,
                pygame.K_UP
            ):
                spieler.shoot()

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

    for asteroid in asteroid_list:
        asteroid.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()