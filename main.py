import time
import pygame
import random
import math

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
        self.came_from = None
        self.g = 0
        self.h = 0
        self.f = 0
        self.cost = cost
        self.is_obstacle = False

    def __eq__(self, other):
        return self.position == other.position


def manhattan_distance(start_node, end_node):
    return abs(end_node.position[0] - start_node.position[0]) + abs(
        end_node.position[1] - start_node.position[1]
    )


def euclidian_distance(start_node, end_node):
    return math.sqrt(
        (end_node.position[0] - start_node.position[0]) ** 2
        + (end_node.position[1] - start_node.position[1]) ** 2
    )


def chebyshev_distance(start_node, end_node):
    return max(
        abs(end_node.position[0] - start_node.position[0]),
        abs(end_node.position[1] - start_node.position[1]),
    )


# A* algoritam za pronalazenje najkraceg puta
def astar(grid, start, end, heuristic):
    # postavimo trosak za sve cvorove na beskonacno
    for col in grid:
        for node in col:
            node.g = float("inf")

    # Napravimo start i end node
    startNode = start
    startNode.g = 0
    startNode.h = heuristic(start, end)
    startNode.f = startNode.g + startNode.h
    startNode.came_from = None

    endNode = end

    # Inicijaliziramo praznu listu otvorenih i zatvorenih cvorova
    openList = []

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

        # Provjeravamo da li smo nasli kraj
        # Ako jedmo vracamo listu cvorova od starta do kraja
        if currentNode == endNode:
            path = []
            current = currentNode
            while current is not None:
                path.append(current)
                current = current.came_from
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
            if newNode.is_obstacle:
                continue

            # g vrijednost od novog cvora (ukupna tezina)
            tentative_g = currentNode.g + currentNode.cost

            # Ovaj put do susjeda je bolji od bilo kojeg prethodnog. Zabilježi ga!
            if tentative_g < newNode.g:
                # ako new_node nije vec u listi otvorenih cvorova dodaj ga
                if newNode not in openList:
                    openList.append(newNode)

                # postavimo came_from - tj. cvor sa kojeg smo dosli u taj cvor
                newNode.came_from = currentNode

                # spremimo vrijednosti g, h i f
                newNode.g = tentative_g
                newNode.h = heuristic(newNode, end)
                newNode.f = newNode.g + newNode.h


# Dodajemo funkcionalnost za odabir heuristike
class Dropdown:
    def __init__(self, position, size, options, callback):
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.options = options
        self.callback = callback
        self.dropdown_open = False
        self.selected_option = None
        self.option_rects = []

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(
            self.selected_option if self.selected_option else self.options[0],
            True,
            (0, 0, 0),
        )
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))
       

        if self.dropdown_open:
            dropdown_bg_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + 3 * self.rect.height,
                    self.rect.width,
                    self.rect.height,
                )
            pygame.draw.rect(screen, (230, 230, 230), dropdown_bg_rect)
            self.option_rects = []
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + (i + 1) * self.rect.height,
                    self.rect.width,
                    self.rect.height,
                )
                self.option_rects.append(option_rect)
                pygame.draw.rect(screen, (230, 230, 230), option_rect)
                pygame.draw.rect(screen, BLACK_COLOR, option_rect, 1) 
                option_text = font.render(option, True, (0, 0, 0))
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.dropdown_open = not self.dropdown_open

            if self.dropdown_open:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_option = self.options[i]
                        self.dropdown_open = False
                        self.callback(self.selected_option)
                        break

    # Funkcija koja crta strelicu

    def draw_arrow(self, surface, position, size, direction="down"):
        x, y = position
        color = EMPTY_CELL_COLOR
        half_size = size // 2

        if direction == "down":
            points = [(x, y), (x + half_size, y + size), (x + size, y)]
        elif direction == "up":
            points = [(x, y + size), (x + half_size, y), (x + size, y + size)]

        pygame.draw.polygon(surface, color, points)


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
        """Set the text as a list of lines."""
        self.text_lines = text.split("\n")  # Split into multiple lines

    def draw(self, surface):
        """Draw each line of text with spacing."""
        y_offset = 0
        for line in self.text_lines:
            text_surface = self.font.render(line, True, self.color)
            surface.blit(text_surface, (self.position[0], self.position[1] + y_offset))
            y_offset += self.font.get_height() + 5  # Add spacing between lines


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

    def set_text(self, text):
        self.text = text
        self.text_surf = self.font.render(self.text, True, EMPTY_CELL_COLOR)


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
        self.elapsed_time = 0
        self.grid_updated = False
        self.player = Player()
        self.grid = [
            [Node((col, row), self.get_random_cost()) for row in range(ROWS)]
            for col in range(COLS)
        ]
        self.heuristic = manhattan_distance  # Default heuristic
        self.buttons = []

        self.start = self.grid[0][0]
        self.end = self.grid[random.randint(0, COLS - 1)][random.randint(0, ROWS - 1)]

        # za 60 fps
        self.clock = pygame.time.Clock()
        self.fps = 60
    

    # Inicijalizira Pygame, parametre mreze, pocetnu i zavrsnu tocku, generira nasumicne prepreke, postavlja prozor i tipke.
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        self.generate_random_obstacles()

        self.heuristic_dropdown = Dropdown(
            (810, 230),
            (180, 40),
            ["Manhattan", "Euclidean", "Chebyshev"],
            self.on_heuristic_selected,
        )

        self.buttons.append(
            Button((810, 10), (180, 50), "Randomize", self.generate_random_obstacles)
        )
        self.buttons.append(Button((810, 70), (180, 50), "Clear", self.clear_all))

        self.start_stop_button = Button(
            (810, 130),
            (180, 50),
            "Start" if self._running else "Stop",
            self.start_stop_moving,
        )
        self.buttons.append(self.start_stop_button)

        self.time_display = TextDisplay((810, MAP_HEIGHT - 50))
        self.length_display = TextDisplay((810, MAP_HEIGHT - 100))

        self.heuristic_text = TextDisplay((810, 210))
        self.heuristic_text.set_text("Heuristika:")
        
        self.controls_text = TextDisplay((810, 290))
        self.controls_text.set_text(
            "Controls:"
        )
        self.controls_list_text = TextDisplay((815, 315),font_size=22)
        self.controls_list_text.set_text(
            "LMB: Add Obstacle\n"
            "RMB: Clear Obstacle\n"
            "1: Set Cost 1\n"
            "2: Set Cost 2\n"
            "3: Set Cost 3\n"
            "S: Set Start\n"
            "E: Set End"
        )
      
        
        
        self._running = True

    # Obraduje dogadaje u igri poput klikanja i tipkanja
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.is_clicked():
                    button.callback()

            # Handle the dropdown menu
            self.heuristic_dropdown.handle_event(event)

        x, y = pygame.mouse.get_pos()
        col = x // GRID_SIZE
        row = y // GRID_SIZE

        if col >= COLS or row >= ROWS:
            return

        mouse_buttons = pygame.mouse.get_pressed()

        # sa ljevim klikom dodajemo prepreku
        if mouse_buttons[0] == 1:  # Left mouse button
            if not self.grid[col][row].is_obstacle:
                self.grid[col][row].is_obstacle = True
                self.grid_updated = True

        # sa desnim klikom brisemo prepreke
        elif mouse_buttons[2] == 1:  # Right mouse button
            if self.grid[col][row].is_obstacle:
                self.grid[col][row].is_obstacle = False
                self.grid_updated = True

        keys = pygame.key.get_pressed()
        # sa tipkom 1 postavljamo polje sa tezinom 1
        if keys[pygame.K_1]:
            self.grid[col][row].is_obstacle = False
            self.grid[col][row].cost = 1
            self.grid_updated = True
        # sa tipkom 2 postavljamo polje sa tezinom 1
        elif keys[pygame.K_2]:
            self.grid[col][row].is_obstacle = False
            self.grid[col][row].cost = 2
            self.grid_updated = True
        # sa tipkom 3 postavljamo polje sa tezinom 3
        elif keys[pygame.K_3]:
            self.grid[col][row].is_obstacle = False
            self.grid[col][row].cost = 3
            self.grid_updated = True
        # sa tipkom s postavljamo lokaciju igraca
        elif keys[pygame.K_s]:
            self.grid[col][row].is_obstacle = False
            self.start = self.grid[col][row]
            self.grid_updated = True
        # sa tipkom e postavljamo cilj
        elif keys[pygame.K_e]:
            self.grid[col][row].is_obstacle = False
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

        self.time_display.set_text(str(round(self.elapsed_time * 1000, 3)) + "ms")
        self.length_display.set_text("Total cost: " + str(self.get_path_cost()))

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

        controls_bg_rect = pygame.Rect(810, 310, 180, 145)
        pygame.draw.rect(self._display_surf, (230, 230, 230), controls_bg_rect)  
       

        self.time_display.draw(self._display_surf)
        self.length_display.draw(self._display_surf)
        self.heuristic_text.draw(self._display_surf)
        self.controls_text.draw(self._display_surf)
        self.controls_list_text.draw(self._display_surf)
        self.heuristic_dropdown.draw(self._display_surf)  # Draw the heuristic dropdown
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
            self.clock.tick(self.fps)

        self.on_cleanup()

    # Izračunava najkraći put koristeći A* algoritam
    def get_path(self):
        start_time = time.time()
        self.path = astar(self.grid, self.start, self.end, self.heuristic)
        end_time = time.time()
        self.elapsed_time = end_time - start_time

    def clear_obstacles(self):
        self.path = []

        for y in range(ROWS):
            for x in range(COLS):
                self.grid[x][y].is_obstacle = False

        self.grid_updated = True

    # Brise sve prepreke i postavlja mrezu na pocetne vrijednosti.
    def clear_all(self):
        self.path = []

        for y in range(ROWS):
            for x in range(COLS):
                self.grid[x][y].is_obstacle = False
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
            self.grid[x][y].is_obstacle = True

        # Provjerava ako postoji put
        self.get_path()
        while not self.path:
            self.generate_random_obstacles()

    # Pokrece ili zaustavlja kretanje igraca.
    def start_stop_moving(self):
        self.player.is_moving = not self.player.is_moving
        self.start_stop_button.set_text("Stop" if self.player.is_moving else "Start")

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
                        rect,
                    )
                elif self.grid[col][row].is_obstacle:
                    pygame.draw.rect(
                        self._display_surf,
                        OBSTACLE_COLOR,
                        rect,
                    )
                elif self.grid[col][row].cost == 1:
                    pygame.draw.rect(
                        self._display_surf,
                        COST_1_COLOR,
                        rect,
                    )
                elif self.grid[col][row].cost == 2:
                    pygame.draw.rect(
                        self._display_surf,
                        COST_2_COLOR,
                        rect,
                    )
                elif self.grid[col][row].cost == 3:
                    pygame.draw.rect(
                        self._display_surf,
                        COST_3_COLOR,
                        rect,
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

    # Dodajemo funkciju koja se poziva kad se odabere opcija heuristike

    def on_heuristic_selected(self, option):
        if option == "Manhattan":
            self.heuristic = manhattan_distance
        elif option == "Euclidean":
            self.heuristic = euclidian_distance
        elif option == "Chebyshev":
            self.heuristic = chebyshev_distance

        self.get_path()


# Provjerava ako se izvodi ovaj file
if __name__ == "__main__":
    game = Game()
    game.on_execute()
