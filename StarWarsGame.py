import pygame, random, math
pygame.init()

# Bilder laden
x_wing_img = pygame.image.load("Pixelarts/X_Wing.png")

"""
torpedo_img = pygame.image.load("Pixelarts/Torpedo.png")

explosion_img = pygame.image.load("Pixelarts/Explosion.png")

asteroid_images = [
    pygame.image.load("Pixelarts/Astroids/frame_01"),
    pygame.image.load("Pixelarts/Astroids/frame_02"),
    pygame.image.load("Pixelarts/Astroids/frame_03"),
    pygame.image.load("Pixelarts/Astroids/frame_04"),
    pygame.image.load("Pixelarts/Astroids/frame_05"),
    pygame.image.load("Pixelarts/Astroids/frame_06"),
    pygame.image.load("Pixelarts/Astroids/frame_07"),
    pygame.image.load("Pixelarts/Astroids/frame_08"),
    pygame.image.load("Pixelarts/Astroids/frame_09"),
    pygame.image.load("Pixelarts/Astroids/frame_10"),
    pygame.image.load("Pixelarts/Astroids/frame_11"),
]
"""

# Spielfläche
size = width, height = 1280, 720

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Star Wars")

clock = pygame.time.Clock()

# Farben
BLACK = (0, 0, 0)

# Spieler
original_width, original_height = x_wing_img.get_size()

PLAYER_WIDTH = original_width // 4
PLAYER_HEIGHT = original_height // 4

player_img = pygame.transform.scale(
    x_wing_img,
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

player_x = width // 2 - PLAYER_WIDTH // 2
player_y = height - PLAYER_HEIGHT - 20

speed = 10

# Spiel Logic
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tastatur abfragen
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= speed

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += speed

    # Im Fenster halten
    if player_x < 0:
        player_x = 0

    if player_x > width - PLAYER_WIDTH:
        player_x = width - PLAYER_WIDTH

    # Zeichnen
    screen.fill(BLACK)

    screen.blit(player_img, (player_x, player_y))

    # Hitbox
    if keys[pygame.K_h]:
        picture_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.draw.rect(screen, (255, 0, 0), picture_rect, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()