import pygame
import sys
import random

pygame.init()

# Fenster
width = 800
height = 600

screen = pygame.display.set_mode((width, height))
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


class Asteroid:

    def __init__(self):

        self.scale = 0.2

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
            width - self.width
        )

        self.y = -self.height

        self.speed = random.randint(2, 8)

    def update(self):

        self.y += self.speed

        # Animation
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
            self.x,
            self.y,
            self.width,
            self.height
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
        fenster_hoehe
    ):

        self.show_hitbox = False

        self.image = pygame.transform.scale_by(
            bild,
            0.25
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

    def move_left(self):

        self.x -= self.speed

        if self.x < 0:
            self.x = 0

    def move_right(self):

        self.x += self.speed

        if self.x > width - self.width:
            self.x = width - self.width

    def get_rect(self):

        return pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def shoot(self):

        laser_list.append(
            Laser(
                self.x + (self.width * 0.87) // 5,
                self.y + self.height // 3
            )
        )

        laser_list.append(
            Laser(
                self.x + (self.width * 4.25) // 5,
                self.y + self.height // 3
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
                self.get_rect(),
                2
            )


# Spieler erzeugen
spieler = Spieler(
    x_wing_img,
    width,
    height
)

asteroid_spawn_timer = 0

running = True

while running:

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_h:
                spieler.show_hitbox = (
                    not spieler.show_hitbox
                )

            if (
                event.key == pygame.K_SPACE
                or event.key == pygame.K_w
                or event.key == pygame.K_UP
            ):
                spieler.shoot()

    # Tastatur
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

    # Asteroiden spawnen
    asteroid_spawn_timer += 1

    if asteroid_spawn_timer >= 60:

        asteroid_list.append(
            Asteroid()
        )

        asteroid_spawn_timer = 0

    # Asteroiden bewegen
    for asteroid in asteroid_list[:]:

        asteroid.update()

        if asteroid.y > height:

            asteroid_list.remove(
                asteroid
            )

    # Laser trifft Asteroid
    for asteroid in asteroid_list[:]:

        for laser in laser_list[:]:

            if asteroid.get_rect().colliderect(
                laser.rect
            ):

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
            spieler.get_rect()
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