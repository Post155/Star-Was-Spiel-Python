import os
import random

import pygame

from game.constants import WIDTH as DEFAULT_WIDTH, HEIGHT as DEFAULT_HEIGHT


# ============================================================
# STAR
# ============================================================

class Star:
    """
    Einzelner Stern im Hintergrund.

    Layer:
        1 = weit entfernt
        2 = mittlere Entfernung
        3 = nicht für normale Sterne vorgesehen
    """

    def __init__(self, width, height, layer=1):
        self.width = width
        self.height = height
        self.layer = layer

        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

        # ----------------------------------------------------
        # Eigenschaften abhängig von der Entfernung
        # ----------------------------------------------------

        if layer == 1:
            self.size = random.choice([1, 1, 1, 1])
            self.base_speed = 12.0
            self.brightness_min = 80
            self.brightness_max = 190
            self.twinkle_chance = 0.15

        elif layer == 2:
            self.size = random.choice([1, 2, 2, 3])
            self.base_speed = 30.0
            self.brightness_min = 120
            self.brightness_max = 240
            self.twinkle_chance = 0.25

        else:
            self.size = random.choice([2, 3, 4])
            self.base_speed = 55.0
            self.brightness_min = 160
            self.brightness_max = 255
            self.twinkle_chance = 0.35

        # ----------------------------------------------------
        # Individuelle Geschwindigkeit
        # ----------------------------------------------------

        self.speed = (
            self.base_speed
            * (self.size / 1.5)
            * random.uniform(0.7, 1.3)
        )

        # ----------------------------------------------------
        # Farbe
        # ----------------------------------------------------

        self.base_brightness = random.randint(
            self.brightness_min,
            self.brightness_max
        )

        # Manche Sterne bekommen einen leichten Farbton.
        tint_chance = 0.25 if layer == 2 else 0.10

        if random.random() < tint_chance:
            self.tint = random.choice([
                (180, 200, 255),  # blau
                (255, 210, 190),  # orange/rot
                (210, 220, 255),  # hellblau
            ])
        else:
            self.tint = (255, 255, 255)

        # ----------------------------------------------------
        # Twinkle
        # ----------------------------------------------------

        self.twinkle = random.random() < self.twinkle_chance

        self.brightness = float(self.base_brightness)

        self.twinkle_speed = random.uniform(20.0, 70.0)

        self.twinkle_direction = random.choice([-1, 1])

        # Nicht jeder Stern soll dauerhaft sichtbar flackern.
        self.twinkle_timer = random.uniform(0.0, 3.0)

        self.color = self._calculate_color()

    def _calculate_color(self):
        """Berechnet die aktuelle Farbe aus Helligkeit + Tint."""

        factor = self.brightness / 255.0

        return (
            min(255, int(self.tint[0] * factor)),
            min(255, int(self.tint[1] * factor)),
            min(255, int(self.tint[2] * factor)),
        )

    def update(self, dt):
        """
        Aktualisiert den Stern.

        dt = vergangene Zeit in Sekunden.
        """

        # Bewegung nach unten
        self.y += self.speed * dt

        # ----------------------------------------------------
        # Twinkle
        # ----------------------------------------------------

        if self.twinkle:
            self.twinkle_timer -= dt

            if self.twinkle_timer <= 0:
                self.brightness += (
                    self.twinkle_speed
                    * self.twinkle_direction
                    * dt
                )

                if self.brightness >= self.brightness_max:
                    self.brightness = self.brightness_max
                    self.twinkle_direction = -1

                elif self.brightness <= self.brightness_min:
                    self.brightness = self.brightness_min
                    self.twinkle_direction = 1

                self.color = self._calculate_color()

                # Kleine Pause zwischen manchen Flackerphasen
                if random.random() < 0.03:
                    self.twinkle_timer = random.uniform(0.2, 1.0)

        # ----------------------------------------------------
        # Stern wieder oben erscheinen lassen
        # ----------------------------------------------------

        if self.y > self.height + self.size:
            self.y = -self.size - 2
            self.x = random.uniform(0, self.width)

            # Neue zufällige Helligkeit
            self.brightness = random.randint(
                self.brightness_min,
                self.brightness_max
            )

            self.color = self._calculate_color()

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (
                int(self.x),
                int(self.y),
                self.size,
                self.size
            )
        )

    def resize(self, width, height):
        self.width = width
        self.height = height

        # Falls der Stern außerhalb des neuen Fensters liegt,
        # wird er neu positioniert.
        if self.x > width:
            self.x = random.uniform(0, width)

        if self.y > height:
            self.y = random.uniform(0, height)


# ============================================================
# MOVING BACKGROUND OBJECT
# ============================================================

class MovingBackgroundObject:
    """
    Gemeinsame Basis für Planeten, Asteroiden usw.
    """

    def __init__(
        self,
        image,
        width,
        height,
        speed_range,
        drift_range
    ):
        self.original = image

        self.width = width
        self.height = height

        self.img = image

        self.x = random.uniform(
            -self.img.get_width(),
            width
        )

        self.y = -self.img.get_height()

        self.speed = random.uniform(*speed_range)

        self.drift_x = random.uniform(*drift_range)

    def update(self, dt):
        self.y += self.speed * dt
        self.x += self.drift_x * dt

    def expired(self):
        return (
            self.y
            > self.height + self.img.get_height() + 20
        )

    def draw(self, screen):
        screen.blit(
            self.img,
            (
                int(self.x),
                int(self.y)
            )
        )


# ============================================================
# PLANET
# ============================================================

class Planet(MovingBackgroundObject):
    """
    Hintergrundplanet.

    Planeten bewegen sich langsam und sorgen für Tiefe.
    """

    def __init__(self, image, width, height):
        self.original = image

        # ----------------------------------------------------
        # Planetengröße
        # ----------------------------------------------------

        roll = random.random()

        if roll < 0.75:
            # Kleine Planeten
            scale = random.uniform(0.20, 0.40)

        elif roll < 0.95:
            # Mittlere Planeten
            scale = random.uniform(0.40, 0.65)

        else:
            # Seltene große Planeten
            scale = random.uniform(0.65, 1.0)

        new_width = max(
            16,
            int(image.get_width() * scale)
        )

        new_height = max(
            16,
            int(image.get_height() * scale)
        )

        # pygame.transform.scale erhält den Pixel-Art-Look.
        self.img = pygame.transform.scale(
            image,
            (
                new_width,
                new_height
            )
        )

        self.width = width
        self.height = height

        # ----------------------------------------------------
        # Startposition
        # ----------------------------------------------------

        self.x = random.uniform(
            -self.img.get_width() * 0.75,
            width + self.img.get_width() * 0.75
        )

        self.y = (
            -self.img.get_height()
            - random.uniform(0, height * 0.5)
        )

        # ----------------------------------------------------
        # Geschwindigkeit
        # ----------------------------------------------------

        self.speed = random.uniform(
            35.0,
            75.0
        )

        # Große Planeten bewegen sich etwas langsamer.
        if scale > 0.65:
            self.speed *= 0.7

        self.drift_x = random.uniform(
            -25.0,
            25.0
        )

        # ----------------------------------------------------
        # Leichte Transparenz für entfernte Planeten
        # ----------------------------------------------------

        self.alpha = random.randint(
            150,
            235
        )

        if self.alpha < 255:
            self.img = self.img.copy()
            self.img.set_alpha(self.alpha)

    def update(self, dt):
        self.y += self.speed * dt
        self.x += self.drift_x * dt

    def expired(self):
        return (
            self.y
            > self.height + self.img.get_height() + 30
        )


# ============================================================
# FOREGROUND OBJECT
# ============================================================

class ForegroundObject(MovingBackgroundObject):
    """
    Große dunkle Objekte im Vordergrund.

    Zum Beispiel:
        - Asteroiden
        - Raumschiffteile
        - Satelliten
        - Felsen
    """

    def __init__(self, image, width, height):
        self.original = image

        # ----------------------------------------------------
        # Größe
        # ----------------------------------------------------

        scale = random.uniform(
            0.3,
            1.0
        )

        new_width = max(
            6,
            int(image.get_width() * scale)
        )

        new_height = max(
            6,
            int(image.get_height() * scale)
        )

        scaled = pygame.transform.scale(
            image,
            (
                new_width,
                new_height
            )
        )

        # ----------------------------------------------------
        # Silhouette
        # ----------------------------------------------------

        self.img = self._to_silhouette(
            scaled
        )

        self.width = width
        self.height = height

        # ----------------------------------------------------
        # Position
        # ----------------------------------------------------

        self.x = random.randint(
            -self.img.get_width(),
            width
        )

        self.y = -self.img.get_height()

        # ----------------------------------------------------
        # Geschwindigkeit
        # ----------------------------------------------------

        self.speed = random.uniform(
            110.0,
            210.0
        )

        self.drift_x = random.uniform(
            -35.0,
            35.0
        )

    @staticmethod
    def _to_silhouette(surf):
        """
        Macht aus einem Sprite eine dunkle Silhouette.
        """

        try:
            mask = pygame.mask.from_surface(
                surf
            )

            silhouette = mask.to_surface(
                setcolor=(8, 8, 12, 255),
                unsetcolor=(0, 0, 0, 0)
            )

            return silhouette.convert_alpha()

        except Exception:
            # Fallback
            result = surf.copy()

            try:
                result.fill(
                    (8, 8, 12, 255),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            except Exception:
                result.fill(
                    (8, 8, 12)
                )

            return result

    def update(self, dt):
        self.y += self.speed * dt
        self.x += self.drift_x * dt

    def expired(self):
        return (
            self.y
            > self.height + self.img.get_height() + 30
        )


# ============================================================
# BACKGROUND MANAGER
# ============================================================

class BackgroundManager:
    """
    Verwalten des kompletten dynamischen Weltraum-Hintergrunds.

    Layer:

        Layer 1:
            kleine, dunkle Sterne

        Layer 2:
            größere/hellere Sterne

        Layer 3:
            Planeten

        Layer 4:
            Vordergrundobjekte
    """

    def __init__(
        self,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        assets=None
    ):
        self.width = width
        self.height = height

        self.assets = assets or {}

        # ====================================================
        # STAR LAYERS
        # ====================================================

        self.layer1 = []

        self.layer2 = []

        self._create_stars()

        # ====================================================
        # PLANETS
        # ====================================================

        self.layer3_planets = []

        # Maximal sichtbare Planeten
        self.planet_max_visible = 1

        # Zeit bis zum nächsten Spawn
        self.planet_spawn_timer = random.uniform(
            5.0,
            12.0
        )

        # ====================================================
        # FOREGROUND
        # ====================================================

        self.layer4_objects = []

        self.foreground_max_visible = 4

        self.foreground_spawn_timer = random.uniform(
            0.8,
            3.0
        )

        # ====================================================
        # ASSETS
        # ====================================================

        self.planet_images = self._load_planet_images()

        self.near_images = self._load_foreground_images()

    # ========================================================
    # STAR SETUP
    # ========================================================

    def _create_stars(self):
        """
        Erstellt die Sterne abhängig von der Auflösung.
        """

        desired1 = max(
            80,
            int(
                (self.width * self.height)
                / 6000
            )
        )

        desired2 = max(
            35,
            int(
                (self.width * self.height)
                / 12000
            )
        )

        self.layer1 = [
            Star(
                self.width,
                self.height,
                layer=1
            )
            for _ in range(desired1)
        ]

        self.layer2 = [
            Star(
                self.width,
                self.height,
                layer=2
            )
            for _ in range(desired2)
        ]

    # ========================================================
    # PLANET ASSETS
    # ========================================================

    def _load_planet_images(self):
        """
        Lädt Planeten aus den übergebenen Assets.

        Erwartete Keys:

            planet_blue_img
            planet_red_img
            planet_green_img
            planet_desert_img
        """

        images = []

        asset_keys = (
            "planet_blue",
            "planet_red",
            "planet_green",
            "planet_desert"
        )

        for key in asset_keys:
            image = self.assets.get(
                f"{key}_img"
            )

            if image is not None:
                images.append(image)

        if images:
            return images

        # ----------------------------------------------------
        # Fallback: Pixelart-Ordner
        # ----------------------------------------------------

        planets_dir = os.path.join(
            os.getcwd(),
            "Pixelarts",
            "Planets"
        )

        if os.path.isdir(planets_dir):
            for filename in sorted(
                os.listdir(planets_dir)
            ):
                path = os.path.join(
                    planets_dir,
                    filename
                )

                if not os.path.isfile(path):
                    continue

                try:
                    image = pygame.image.load(
                        path
                    ).convert_alpha()

                    images.append(image)

                except pygame.error:
                    # Ungültige Datei ignorieren
                    continue

        if images:
            return images

        # ----------------------------------------------------
        # Letzter Fallback
        # ----------------------------------------------------

        return self._generate_planet_images()

    # ========================================================
    # FOREGROUND ASSETS
    # ========================================================

    def _load_foreground_images(self):
        """
        Lädt Asteroiden/Vordergrundobjekte aus assets.
        """

        images = self.assets.get(
            "asteroid_images"
        )

        if images:
            return images

        return []

    # ========================================================
    # FALLBACK PLANETS
    # ========================================================

    @staticmethod
    def _generate_planet_images():
        """
        Erzeugt einfache Planeten, falls keine Bilder
        vorhanden sind.
        """

        palette = [
            (80, 150, 255),
            (255, 110, 90),
            (110, 220, 140),
            (215, 190, 120),
            (170, 110, 220),
        ]

        images = []

        for color in palette:
            surface = pygame.Surface(
                (64, 64),
                pygame.SRCALPHA
            )

            # Planet
            pygame.draw.circle(
                surface,
                color,
                (32, 32),
                24
            )

            # leichte Atmosphäre
            pygame.draw.circle(
                surface,
                (
                    255,
                    255,
                    255,
                    50
                ),
                (27, 25),
                20,
                2
            )

            # Lichtreflex
            pygame.draw.circle(
                surface,
                (
                    255,
                    255,
                    255,
                    80
                ),
                (24, 20),
                8
            )

            images.append(
                surface
            )

        return images

    # ========================================================
    # RESIZE
    # ========================================================

    def resize(self, width, height):
        """
        Passt den Hintergrund an eine neue Fenstergröße an.
        """

        self.width = width
        self.height = height

        # ----------------------------------------------------
        # Anzahl Sterne berechnen
        # ----------------------------------------------------

        desired1 = max(
            80,
            int(
                (width * height)
                / 6000
            )
        )

        desired2 = max(
            35,
            int(
                (width * height)
                / 12000
            )
        )

        # ----------------------------------------------------
        # Zu viele Sterne entfernen
        # ----------------------------------------------------

        if len(self.layer1) > desired1:
            self.layer1 = self.layer1[:desired1]

        if len(self.layer2) > desired2:
            self.layer2 = self.layer2[:desired2]

        # ----------------------------------------------------
        # Fehlende Sterne hinzufügen
        # ----------------------------------------------------

        while len(self.layer1) < desired1:
            self.layer1.append(
                Star(
                    width,
                    height,
                    layer=1
                )
            )

        while len(self.layer2) < desired2:
            self.layer2.append(
                Star(
                    width,
                    height,
                    layer=2
                )
            )

        # ----------------------------------------------------
        # Sterne aktualisieren
        # ----------------------------------------------------

        for star in self.layer1:
            star.resize(
                width,
                height
            )

        for star in self.layer2:
            star.resize(
                width,
                height
            )

    # ========================================================
    # SPAWN PLANET
    # ========================================================

    def _spawn_planet(self):
        """
        Erstellt einen neuen Planeten.
        """

        if not self.planet_images:
            return

        if (
            len(self.layer3_planets)
            >= self.planet_max_visible
        ):
            return

        planet = Planet(
            random.choice(
                self.planet_images
            ),
            self.width,
            self.height
        )

        self.layer3_planets.append(
            planet
        )

    # ========================================================
    # SPAWN FOREGROUND
    # ========================================================

    def _spawn_foreground_object(self):
        """
        Erstellt ein neues Vordergrundobjekt.
        """

        if not self.near_images:
            return

        if (
            len(self.layer4_objects)
            >= self.foreground_max_visible
        ):
            return

        obj = ForegroundObject(
            random.choice(
                self.near_images
            ),
            self.width,
            self.height
        )

        self.layer4_objects.append(
            obj
        )

    # ========================================================
    # UPDATE STARS
    # ========================================================

    def _update_stars(self, dt):
        for star in self.layer1:
            star.update(dt)

        for star in self.layer2:
            star.update(dt)

    # ========================================================
    # UPDATE PLANETS
    # ========================================================

    def _update_planets(self, dt):
        for planet in self.layer3_planets[:]:
            planet.update(dt)

            if planet.expired():
                self.layer3_planets.remove(
                    planet
                )

    # ========================================================
    # UPDATE FOREGROUND
    # ========================================================

    def _update_foreground(self, dt):
        for obj in self.layer4_objects[:]:
            obj.update(dt)

            if obj.expired():
                self.layer4_objects.remove(
                    obj
                )

    # ========================================================
    # SPAWN LOGIC
    # ========================================================

    def _update_spawn_timers(self, dt):
        # ----------------------------------------------------
        # PLANET
        # ----------------------------------------------------

        self.planet_spawn_timer -= dt

        if self.planet_spawn_timer <= 0:

            # Wahrscheinlichkeit, damit nicht jeder Timer
            # automatisch einen Planeten erzeugt.
            if random.random() < 0.65:
                self._spawn_planet()

            self.planet_spawn_timer = random.uniform(
                8.0,
                20.0
            )

        # ----------------------------------------------------
        # FOREGROUND
        # ----------------------------------------------------

        self.foreground_spawn_timer -= dt

        if self.foreground_spawn_timer <= 0:

            if random.random() < 0.75:
                self._spawn_foreground_object()

            self.foreground_spawn_timer = random.uniform(
                1.0,
                4.0
            )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):
        """
        Aktualisiert den kompletten Hintergrund.

        dt:
            Zeit seit dem letzten Frame in Sekunden.

        Beispiel:

            dt = clock.tick(60) / 1000.0
            background.update(dt)
        """

        # Schutz gegen extrem große dt-Werte.
        # Verhindert z. B. riesige Sprünge nach
        # einem Fensterwechsel/Alt-Tab.
        dt = min(
            max(dt, 0.0),
            0.1
        )

        self._update_stars(dt)

        self._update_spawn_timers(dt)

        self._update_planets(dt)

        self._update_foreground(dt)

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, screen):
        """
        Zeichnet alle Background-Layer in der richtigen
        Reihenfolge.
        """

        # ----------------------------------------------------
        # FARNE STERNE
        # ----------------------------------------------------

        for star in self.layer1:
            star.draw(screen)

        # ----------------------------------------------------
        # NÄHERE STERNE
        # ----------------------------------------------------

        for star in self.layer2:
            star.draw(screen)

        # ----------------------------------------------------
        # PLANETEN
        # ----------------------------------------------------

        for planet in self.layer3_planets:
            planet.draw(screen)

        # ----------------------------------------------------
        # VORDERGRUND
        # ----------------------------------------------------

        for obj in self.layer4_objects:
            obj.draw(screen)