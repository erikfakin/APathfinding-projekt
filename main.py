import time
import pygame
import random

# Dimenzije prozora igre
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Dimenzije mape igre
MAP_WIDTH = 800
MAP_HEIGHT = 600
GRID_SIZE = 20
COLS = MAP_WIDTH // GRID_SIZE
ROWS = MAP_HEIGHT // GRID_SIZE

# Boje za razlicite elemente igre
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
PLAYER_COLOR = (174, 255, 255)
END_COLOR = (255, 182, 193)
COST_1_COLOR = (119, 221, 119)
COST_2_COLOR = (255, 255, 204)
COST_3_COLOR = (255, 204, 153)
EMPTY_CELL_COLOR = (174, 198, 255)
OBSTACLE_COLOR = BLACK_COLOR

BUTTON_COLOR = (0, 0, 255)
BUTTON_HOVER_COLOR = (0, 0, 150)

# Smjerovi kretanja na mrezi (gore, desno, dolje, lijevo)
DIRECTIONS = [
    (0, -1),  # gore
    (1, 0),  # desno
    (0, 1),  # dolje
    (-1, 0),  # lijevo
]


# Klasa koja predstavlja cvor u mrezi (celiju u igri)
class Node:
    def __init__(self, position=None, cost=1):
        self.position = position
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0
        self.cost = cost
        self.isObstacle = False

    def __eq__(self, other):
        return self.position == other.position


# A* algoritam za pronalazenje najkraceg puta
def astar(grid, start, end):
    # Napravimo start i end node
    startNode = start
    startNode.g = 0
    startNode.h = abs(end.position[0] - start.position[0]) + abs(
        end.position[1] - start.position[1]
    )
    startNode.f = startNode.g + startNode.h
    startNode.parent = None

    endNode = end

    # Inicijaliziramo praznu listu otvorenih i zatvorenih cvorova
    openList = []
    closedList = []

    # Dodajemo start u otvorenu listu
    openList.append(startNode)

    # Ovdje trazimo najkraci put. Kad stignemo do cilja vracamo listu cvorova do cilja
    while len(openList) > 0:
        currentNode = openList[0]

        # Trazimo cvor u openList koji ima najmanji ukupni f
        for node in openList:
            if node.f < currentNode.f:
                currentNode = node

        openList.remove(currentNode)
        closedList.append(currentNode)

        # Provjeravamo da li smo nasli kraj
        # Ako jedmo vracamo listu cvorova od starta do kraja
        if currentNode == endNode:
            path = []
            current = currentNode
            while current is not None:
                path.append(current)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generiraj susjedne cvorove oko trenutne pozicije
        for newPosition in DIRECTIONS:
            nodePosition = (
                currentNode.position[0] + newPosition[0],
                currentNode.position[1] + newPosition[1],
            )

            # Provijeri da li je nodePosition izvan mape, ako je prekoci
            if (
                nodePosition[0] < 0
                or nodePosition[0] > COLS - 1
                or nodePosition[1] < 0
                or nodePosition[1] > ROWS - 1
            ):
                continue

            # Ucitaj u newNode cvor iz pozicije iz grida
            newNode = grid[nodePosition[0]][nodePosition[1]]

            # Provijeri ako je new_node obstacle. ako je prekosci
            if newNode.isObstacle:
                continue

            # Provijeri ako je newNode u listi zatvorenih cvorova
            if newNode in closedList:
                continue

            # g vrijednost od novog cvora (ukupna tezina)
            tentative_g = currentNode.g + currentNode.cost

            # ako new_node nije vec u listi otvorenih cvorova dodaj ga
            if newNode not in openList:
                openList.append(newNode)
            # ako je put preko postojeceg cvora "skuplji" preskoci, zadrzavamo staru bolju vrijednost
            elif tentative_g >= newNode.g:
                continue

            # ako smo stigli do tu znaci da smo nasli novi brzi put do cvora
            # postavimo tako parent - tj. cvor sa kojeg smo dosli u taj cvor
            newNode.parent = currentNode
            # spremimo vrijednosti g, h i f
            newNode.g = tentative_g
            newNode.h = abs(end.position[0] - newNode.position[0]) + abs(
                end.position[1] - newNode.position[1]
            )
            newNode.f = newNode.g + newNode.h


# Klasa za prikazivanje teksta na ekranu
class TextDisplay:
    def __init__(self, position, color=BLACK_COLOR, font_size=30):
        # Initialize Pygame
        self.font = pygame.font.Font(None, font_size)  # Use default font
        self.color = color  # Text color
        self.position = position  # Position to display the text
        self.text_surface = None
        self.text = ""  # Default empty text

    def set_text(self, text):
        """Set the text to be displayed and render it."""
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.color)

    def draw(self, surface):
        """Draw the rendered text on the specified surface."""
        if self.text_surface:
            surface.blit(self.text_surface, self.position)


class Button:
    def __init__(
        self,
        position,
        size,
        text,
        callback,
        font_size=30,
        color=BUTTON_COLOR,
        hover_color=BUTTON_HOVER_COLOR,
    ):
        self.rect = pygame.Rect(
            position[0], position[1], size[0], size[1]
        )  # The area of the button
        self.color = color  # Normal color
        self.hover_color = hover_color  # Color when mouse hovers
        self.text = text  # Text to display on the button
        self.callback = callback
        self.font = pygame.font.SysFont(None, font_size)  # Font for the button text
        self.text_surf = self.font.render(text, True, EMPTY_CELL_COLOR)
        self.text_rect = self.text_surf.get_rect(
            center=self.rect.center
        )  # Center the text inside the button

    def draw(self, screen):
        # Change button color if mouse is hovering over it
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # Draw the button text
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self):
        # Check if the mouse is inside the button and if the mouse was clicked
        if (
            self.rect.collidepoint(pygame.mouse.get_pos())
            and pygame.mouse.get_pressed()[0]
        ):
            return True
        return False


# Klasa za igraca
class Player:
    def __init__(self):
        self.speed = 50
        self.time = 0
        self.is_moving = False
        self.sprite = pygame.image.load("player.png")
        self.sprite = pygame.transform.scale(self.sprite, (GRID_SIZE, GRID_SIZE))

    def draw(self, surface, position):
        surface.blit(self.sprite, position)


# Klasa za igru
class Game:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = WINDOW_WIDTH, WINDOW_HEIGHT
        self.path = []
        self.elapsedTime = 0
        self.grid_updated = False
        self.player = Player()
        self.grid = [
            [Node((col, row), self.get_random_cost()) for row in range(ROWS)]
            for col in range(COLS)
        ]
        self.buttons = []

        self.start = self.grid[0][0]
        self.end = self.grid[random.randint(0, COLS - 1)][random.randint(0, ROWS - 1)]

    # Inicijalizira Pygame, parametre mreze, pocetnu i zavrsnu tocku, generira nasumicne prepreke, postavlja prozor i tipke.
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        self.generate_random_obstacles()

        self.buttons.append(
            Button((810, 10), (180, 50), "Randomize", self.generate_random_obstacles)
        )
        self.buttons.append(Button((810, 70), (180, 50), "Clear", self.clear_all))
        self.buttons.append(Button((810, 130), (180, 50), "Start", self.start_moving))
        self.buttons.append(Button((810, 190), (180, 50), "Stop", self.stop_moving))

        self.timeDisplay = TextDisplay((810, MAP_HEIGHT - 50))
        self.lengthDisplay = TextDisplay((810, MAP_HEIGHT - 100))

        self._running = True

    # Obraduje dogadaje u igri poput klikanja i tipkanja
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.is_clicked():
                    button.callback()

        x, y = pygame.mouse.get_pos()
        col = x // GRID_SIZE
        row = y // GRID_SIZE

        if col >= COLS or row >= ROWS:
            return

        mouse_buttons = pygame.mouse.get_pressed()

        # sa ljevim klikom dodajemo prepreku
        if mouse_buttons[0] == 1:  # Left mouse button
            if not self.grid[col][row].isObstacle:
                self.grid[col][row].isObstacle = True
                self.grid_updated = True

        # sa desnim klikom brisemo prepreke
        elif mouse_buttons[2] == 1:  # Right mouse button
            if self.grid[col][row].isObstacle:
                self.grid[col][row].isObstacle = False
                self.grid_updated = True

        keys = pygame.key.get_pressed()
        # sa tipkom 1 postavljamo polje sa tezinom 1
        if keys[pygame.K_1]:
            self.grid[col][row].isObstacle = False
            self.grid[col][row].cost = 1
            self.grid_updated = True
        # sa tipkom 2 postavljamo polje sa tezinom 1
        elif keys[pygame.K_2]:
            self.grid[col][row].isObstacle = False
            self.grid[col][row].cost = 2
            self.grid_updated = True
        # sa tipkom 3 postavljamo polje sa tezinom 3
        elif keys[pygame.K_3]:
            self.grid[col][row].isObstacle = False
            self.grid[col][row].cost = 3
            self.grid_updated = True
        # sa tipkom s postavljamo lokaciju igraca
        elif keys[pygame.K_s]:
            self.grid[col][row].isObstacle = False
            self.start = self.grid[col][row]
            self.grid_updated = True
        # sa tipkom e postavljamo cilj
        elif keys[pygame.K_e]:
            self.grid[col][row].isObstacle = False
            self.end = self.grid[col][row]
            self.grid_updated = True

    # Glavna logika igre koja se izvrsava u svakom ciklusu: upravljanje kretanjem igrača i ažuriranje puta.
    def on_loop(self):
        self.player.time += 1
        if self.grid_updated:
            self.get_path()
            self.grid_updated = False

        if self.path and self.player.is_moving:
            if (self.player.time / self.path[0].cost) // self.player.speed >= 1:
                self.player.time = 0
                self.path.pop(0)
                if self.path:
                    self.start = self.path[0]

        self.timeDisplay.set_text(str(round(self.elapsedTime * 1000, 3)) + "ms")
        self.lengthDisplay.set_text("Total cost: " + str(self.get_path_cost()))

    # Iscrtava sve na ekranu: mrezu, putanju, igraca, dugmadi i tekst.
    def on_render(self):
        # Popunjava ekran bijele boje kako bismo mogli crtati sve na prazan ekran
        self._display_surf.fill(WHITE_COLOR)
        self.draw_map()
        self.draw_path()
        self.player.draw(
            self._display_surf,
            (
                self.start.position[0] * GRID_SIZE,
                self.start.position[1] * GRID_SIZE,
            ),
        )

        for button in self.buttons:
            button.draw(self._display_surf)

        self.timeDisplay.draw(self._display_surf)
        self.lengthDisplay.draw(self._display_surf)

        # Azurira ekran
        pygame.display.flip()

    # Zatvara Pygame kada aplikacija zavrsi.
    def on_cleanup(self):
        pygame.quit()

    # Pokrece aplikaciju, pokrece glavnu petlju događaja.
    def on_execute(self):
        self.on_init()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

        self.on_cleanup()

    # Izračunava najkraći put koristeći A* algoritam
    def get_path(self):
        startTime = time.time()
        self.path = astar(self.grid, self.start, self.end)
        endTime = time.time()
        self.elapsedTime = endTime - startTime

    def clear_obstacles(self):
        self.path = []

        for y in range(ROWS):
            for x in range(COLS):
                self.grid[x][y].isObstacle = False

        self.grid_updated = True

    # Brise sve prepreke i postavlja mrezu na pocetne vrijednosti.
    def clear_all(self):
        self.path = []

        for y in range(ROWS):
            for x in range(COLS):
                self.grid[x][y].isObstacle = False
                self.grid[x][y].cost = 1

        self.grid_updated = True

    # Generira nasumicne prepreke na mrezi.
    def generate_random_obstacles(self, obstacles=250):
        self.path = []
        self.start = self.grid[0][0]
        self.end = self.grid[random.randint(0, COLS - 1)][random.randint(0, ROWS - 1)]

        self.clear_obstacles()
        # generate random obstacles

        for i in range(obstacles):
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if self.grid[x][y] == self.start or self.grid[x][y] == self.end:
                continue
            self.grid[x][y].isObstacle = True

        # Provjerava ako postoji put
        self.get_path()
        while not self.path:
            self.generate_random_obstacles()

    # Pokrece kretanje igraca.
    def start_moving(self):
        self.player.is_moving = True

    # Zaustavlja kretanje igraca
    def stop_moving(self):
        self.player.is_moving = False

    # Vraća ukupni trosak puta
    def get_path_cost(self):
        path_cost = 0
        if self.path:
            for node in self.path:
                path_cost += node.cost
        return path_cost

    # Iscrtava mrezu i razlicite vrste celija (prepreke, pocetnu tocku, cilj, itd.).
    def draw_map(self):
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(
                    col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE
                )

                if self.grid[col][row] == self.end:
                    pygame.draw.rect(
                        self._display_surf,
                        (0, 0, 255),
                        pygame.Rect(
                            col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE
                        ),
                    )
                elif self.grid[col][row].isObstacle:
                    pygame.draw.rect(
                        self._display_surf,
                        OBSTACLE_COLOR,
                        pygame.Rect(
                            col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE
                        ),
                    )
                elif self.grid[col][row].cost == 1:
                    pygame.draw.rect(
                        self._display_surf,
                        COST_1_COLOR,
                        pygame.Rect(
                            col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE
                        ),
                    )
                elif self.grid[col][row].cost == 2:
                    pygame.draw.rect(
                        self._display_surf,
                        COST_2_COLOR,
                        pygame.Rect(
                            col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE
                        ),
                    )
                elif self.grid[col][row].cost == 3:
                    pygame.draw.rect(
                        self._display_surf,
                        COST_3_COLOR,
                        pygame.Rect(
                            col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE
                        ),
                    )

        for row in range(ROWS):
            pygame.draw.line(
                self._display_surf,
                BLACK_COLOR,
                (0, row * GRID_SIZE),
                (MAP_WIDTH, row * GRID_SIZE),
            )

        for col in range(COLS):
            pygame.draw.line(
                self._display_surf,
                BLACK_COLOR,
                (col * GRID_SIZE, 0),
                (col * GRID_SIZE, MAP_HEIGHT),
            )

    # Iscrtava put kroz mapu koristeci crvene krugove.
    def draw_path(self):
        # draw path
        if self.path:
            for cell in self.path:
                if cell == self.path[0]:
                    continue
                pygame.draw.circle(
                    self._display_surf,
                    (255, 0, 0, 100),
                    (
                        cell.position[0] * GRID_SIZE + GRID_SIZE // 2,
                        cell.position[1] * GRID_SIZE + GRID_SIZE // 2,
                    ),
                    GRID_SIZE // 4,
                )

    def get_random_cost(self):
        rand = random.randint(1, 10)
        if rand < 9:
            return 1
        elif rand == 9:
            return 2
        elif rand == 10:
            return 3


# Provjerava ako se izvodi ovaj file
if __name__ == "__main__":
    game = Game()
    game.on_execute()
