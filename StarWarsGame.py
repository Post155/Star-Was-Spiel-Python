import pygame,sys
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

# Bild laden
x_wing_img = pygame.image.load(
    "Pixelarts/x_wing.png"
).convert_alpha()


class Spieler:
    def __init__(self, bild, fenster_breite, fenster_hoehe):
        self.show_hitbox = False

        # Bild auf 1/4 verkleinern
        self.image = pygame.transform.scale_by(bild, 0.25)

        self.width, self.height = self.image.get_size()

        # Startposition
        self.x = fenster_breite // 2 - self.width // 2
        self.y = fenster_hoehe - self.height - 20

        self.speed = 5

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

    def draw(self, screen):

        screen.blit(
            self.image,
            (self.x, self.y)
        )

        # Hitbox zeichnen
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

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        spieler.move_left()

    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        spieler.move_right()

    if keys[pygame.K_ESCAPE]:
        running = False

    if keys[pygame.K_h]:
        spieler.show_hitbox = not spieler.show_hitbox

    screen.fill(BLACK)

    spieler.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()