import pygame
import random
import math

pygame.init()

# Fenster
WIDTH = 1600
HEIGHT = 1200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Wars")

clock = pygame.time.Clock()

# Farben
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)

# Player
PLAYER_WIDTH = 300
PLAYER_HEIGHT = 200
PLAYER_SPEED = 15

player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - 250

# Munition
bullet_count = 50
torpedo_count = 10

bullets = []
torpedos = []

# Punkte
score = 0
highscore = 0

game_over = False

font = pygame.font.SysFont("Arial", 36)
big_font = pygame.font.SysFont("Arial", 72)

# --------------------------------------------------
# Klassen
# --------------------------------------------------

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 6, 30)

    def update(self):
        self.rect.y -= 30

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


class Torpedo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 80)

    def update(self):
        self.rect.y -= 15

    def draw(self):
        pygame.draw.rect(screen, YELLOW, self.rect)


class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.ttl = 18

    def update(self):
        self.ttl -= 1

    def draw(self):
        pygame.draw.circle(
            screen,
            ORANGE,
            (int(self.x), int(self.y)),
            int(self.size)
        )


class Asteroid:
    def __init__(self):

        r = random.random()

        if r < 0.80:
            self.scale = random.uniform(0.30, 0.55)
            self.hp = 5
            self.points = 3
        elif r < 0.95:
            self.scale = random.uniform(0.65, 0.95)
            self.hp = 3
            self.points = 2
        else:
            self.scale = random.uniform(1.20, 1.70)
            self.hp = 2
            self.points = 1

        self.size = int(200 / self.scale)

        self.x = random.randint(0, WIDTH)
        self.y = -100

        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(2.5, 8)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self):
        pygame.draw.circle(
            screen,
            (120, 120, 120),
            (int(self.x), int(self.y)),
            self.size // 2
        )

    def radius(self):
        return self.size * 0.2


# --------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------

asteroids = []
explosions = []


def circle_rect_collision(cx, cy, radius, rect):

    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))

    dx = cx - closest_x
    dy = cy - closest_y

    return dx * dx + dy * dy <= radius * radius


def spawn_asteroid():
    asteroids.append(Asteroid())


for _ in range(5):
    spawn_asteroid()


def restart_game():
    global score
    global bullet_count
    global torpedo_count
    global player_x
    global game_over

    asteroids.clear()
    bullets.clear()
    torpedos.clear()
    explosions.clear()

    score = 0
    bullet_count = 50
    torpedo_count = 10

    player_x = WIDTH // 2 - PLAYER_WIDTH // 2

    for _ in range(5):
        spawn_asteroid()

    game_over = False


# --------------------------------------------------
# Hauptschleife
# --------------------------------------------------

running = True

while running:

    clock.tick(60)

    # Eingaben
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_over:

                if event.key == pygame.K_r:
                    restart_game()

                continue

            if event.key == pygame.K_UP and bullet_count > 0:

                bullets.append(Bullet(player_x + 48, player_y))
                bullets.append(Bullet(player_x + 250, player_y))

                bullet_count -= 1

            if event.key == pygame.K_DOWN and torpedo_count > 0:

                torpedos.append(
                    Torpedo(player_x + 130, player_y)
                )

                torpedo_count -= 1

    keys = pygame.key.get_pressed()

    if not game_over:

        if keys[pygame.K_LEFT]:
            player_x -= PLAYER_SPEED

        if keys[pygame.K_RIGHT]:
            player_x += PLAYER_SPEED

        player_x = max(
            0,
            min(player_x, WIDTH - PLAYER_WIDTH)
        )

    # Asteroiden erzeugen
    if not game_over and random.random() < 0.01:
        spawn_asteroid()

    # Bullets
    for bullet in bullets[:]:

        bullet.update()

        if bullet.rect.bottom < 0:
            bullets.remove(bullet)
            continue

        for asteroid in asteroids[:]:

            if circle_rect_collision(
                asteroid.x,
                asteroid.y,
                asteroid.radius(),
                bullet.rect
            ):

                asteroid.hp -= 1

                if bullet in bullets:
                    bullets.remove(bullet)

                if asteroid.hp <= 0:

                    score += asteroid.points

                    explosions.append(
                        Explosion(
                            asteroid.x,
                            asteroid.y,
                            asteroid.size // 2
                        )
                    )

                    asteroids.remove(asteroid)

                break

    # Torpedos
    for torpedo in torpedos[:]:

        torpedo.update()

        if torpedo.rect.bottom < 0:
            torpedos.remove(torpedo)
            continue

        for asteroid in asteroids[:]:

            if circle_rect_collision(
                asteroid.x,
                asteroid.y,
                asteroid.radius(),
                torpedo.rect
            ):

                asteroid.hp -= 3

                if torpedo in torpedos:
                    torpedos.remove(torpedo)

                if asteroid.hp <= 0:

                    score += asteroid.points

                    explosions.append(
                        Explosion(
                            asteroid.x,
                            asteroid.y,
                            asteroid.size // 2
                        )
                    )

                    asteroids.remove(asteroid)

                break

    # Asteroiden
    player_rect = pygame.Rect(
        player_x,
        player_y,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )

    for asteroid in asteroids[:]:

        asteroid.update()

        if asteroid.y > HEIGHT + 100:
            asteroids.remove(asteroid)
            continue

        if circle_rect_collision(
            asteroid.x,
            asteroid.y,
            asteroid.radius(),
            player_rect
        ):

            game_over = True

            if score > highscore:
                highscore = score

    # Explosionen
    for ex in explosions[:]:

        ex.update()

        if ex.ttl <= 0:
            explosions.remove(ex)

    # Zeichnen
    screen.fill((0, 0, 25))

    pygame.draw.rect(
        screen,
        (50, 150, 255),
        player_rect
    )

    for bullet in bullets:
        bullet.draw()

    for torpedo in torpedos:
        torpedo.draw()

    for asteroid in asteroids:
        asteroid.draw()

    for ex in explosions:
        ex.draw()

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    ammo_text = font.render(
        f"Bullets: {bullet_count}",
        True,
        WHITE
    )

    torpedo_text = font.render(
        f"Torpedos: {torpedo_count}",
        True,
        WHITE
    )

    screen.blit(score_text, (20, 20))
    screen.blit(ammo_text, (20, 60))
    screen.blit(torpedo_text, (20, 100))

    if game_over:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)

        screen.blit(overlay, (0, 0))

        txt1 = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        txt2 = font.render(
            f"Score: {score}",
            True,
            WHITE
        )

        txt3 = font.render(
            f"Highscore: {highscore}",
            True,
            YELLOW
        )

        txt4 = font.render(
            "R = Neustart",
            True,
            WHITE
        )

        screen.blit(txt1, (WIDTH/2-220, 350))
        screen.blit(txt2, (WIDTH/2-80, 500))
        screen.blit(txt3, (WIDTH/2-100, 560))
        screen.blit(txt4, (WIDTH/2-90, 650))

    pygame.display.flip()

pygame.quit()