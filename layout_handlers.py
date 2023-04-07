import pygame
import random
import time
import xml.etree.ElementTree as ET

MAIN_VIEW_FPS = 10
PIXEL_SIZE = 10

SNAKE_BLACK = pygame.Color(0, 0, 0)
SNAKE_WHITE = pygame.Color(255, 255, 255)
SNAKE_RED = pygame.Color(255, 0, 0)
SNAKE_GREEN = pygame.Color(0, 255, 0)
SNAKE_BLUE = pygame.Color(0, 0, 255)
SNAKE_ORANGE = pygame.Color(255, 153, 51)

GAME_FONT = "times new roman"
SCORE_FONT_SIZE = 20
PAUSED_FONT_SIZE = 50
GAME_OVER_FONT_SIZE = 50
GAME_PAUS_FONT_SIZE = 50
MIDDLE_SCREEN_FONT_SIZE = 50

INFO_SURFACE_HEIGHT = 30

class SnakeLayoutHandler:

    def __init__(self, game_window):
        self.game_window = game_window
        self.window_x, self.window_y = self.game_window.get_size()
        self.game_window.fill((255, 0, 0))
        
        self.info_surface_size = (self.window_x, INFO_SURFACE_HEIGHT)
        self.game_surface_size = (self.window_x, self.window_y - self.info_surface_size[1])
        
        self.info_surface = pygame.Surface(self.info_surface_size)
        self.game_surface = pygame.Surface(self.game_surface_size)
        
        self.info_board_pixels = (0, 0, self.window_x, INFO_SURFACE_HEIGHT)
        self.game_board_pixels = (0, self.info_board_pixels[3], self.window_x, self.window_y - INFO_SURFACE_HEIGHT)
    
    
    def get_game_surface_size(self):
        return self.game_surface_size


    def get_game_surface(self):
        return self.game_surface


    def set_middle_screen_text(self, text, color):
        my_font = pygame.font.SysFont(GAME_FONT, MIDDLE_SCREEN_FONT_SIZE)
        game_over_surface = my_font.render(text, True, color)
        game_over_rect = game_over_surface.get_rect()
        
        game_over_rect.midtop = (self.window_x // 2, self.window_y // 4)
        self.game_surface.blit(game_over_surface, game_over_rect)


    def get_new_text_surface(self, text, size, color):
        font = pygame.font.SysFont(GAME_FONT, size)
        surface = font.render(text, True, color)
        return surface

    
    def add_blocks_game_surface(self, blocks, color, pixel_size):
        for block in blocks:
            pygame.draw.rect(self.game_surface, color, pygame.Rect(block[0], block[1], pixel_size, pixel_size))


    def add_snake_to_game_surface(self, snake, direction, color, pixel_size):
        ## handle snake head and fill out the eyes
        head = snake[0]
        
        #eye_size = pixel_size // 5
        #eye_dist_l, eye_dist_r = eye_size, pixel_size - (2 * eye_size)
        
        ## hard coded for testing purposes/alignment (and because I know the value of 'PIXEL_SIZE')
        eye_size = 3
        eye_dist_l, eye_dist_r = 1, 6

        snake_head = self.game_surface.subsurface((head[0], head[1], pixel_size, pixel_size))
        snake_head.fill(color)

        match direction:
            case pygame.K_RIGHT:
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_r, eye_dist_l, eye_size, eye_size))
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_r, eye_dist_r, eye_size, eye_size))
            case pygame.K_DOWN:
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_l, eye_dist_r, eye_size, eye_size))
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_r, eye_dist_r, eye_size, eye_size))
            case pygame.K_LEFT:
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_l, eye_dist_l, eye_size, eye_size))
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_l, eye_dist_r, eye_size, eye_size))
            case pygame.K_UP:
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_l, eye_dist_l, eye_size, eye_size))
                pygame.draw.rect(snake_head, SNAKE_RED, (eye_dist_r, eye_dist_l, eye_size, eye_size))


        self.add_blocks_game_surface(snake[1:], color, pixel_size)


    def update_info_surface(self, info_texts):
        self.info_surface.fill(SNAKE_WHITE)
        info_width = self.info_surface_size[0] // len(info_texts)
        for i, info in enumerate(info_texts):
            xy_loc = (info_width * i, 0)
            self.info_surface.blit(self.get_new_text_surface(info, SCORE_FONT_SIZE, SNAKE_BLACK), xy_loc)

    
    def clear_game_surface(self):
        self.game_surface.fill(SNAKE_BLACK)


    def update_game_window(self):
        self.game_window.blit(self.info_surface, self.info_board_pixels)
        self.game_window.blit(self.game_surface, self.game_board_pixels)

        pygame.display.update()



class MenuLayoutHandler:

    def __init__(self, game_window, menu_items):
        self.game_window = game_window
        self.menu_items = menu_items
        self.menu_surfaces = []
        self.init_menu_surface()
        self.update_menu_surface()

    
    def draw_menu_surfaces(self):
        for i, surface in enumerate(self.menu_surfaces):
            x, y = surface.get_size()
            self.game_window.blit(surface, (0, i * y, x, (i + 1) * y))


    def move_menu_selector(self, index):
        for i, surface in enumerate(self.menu_surfaces):
            selector_size = surface.get_height() // 5
            selector = pygame.Rect(0, 0, selector_size, selector_size)
            selector.center = (surface.get_width() // 10, surface.get_height() // 2)
            color = SNAKE_ORANGE if i == index else surface.get_at((0, 0))
            pygame.draw.rect(surface, color, selector)


    def init_menu_surface(self):
        menu_surface_size = (self.game_window.get_width(), self.game_window.get_height() // len(self.menu_items))
        font_size = menu_surface_size[1] // 3

        for menu_item in self.menu_items:
            surface = pygame.Surface(menu_surface_size)
            surface.fill((0, 0, random.randint(50, 255)))

            font = pygame.font.SysFont(GAME_FONT, font_size)
            font_surface = font.render(menu_item, True, SNAKE_ORANGE)
            font_rect = font_surface.get_rect()
            
            font_rect.center = (surface.get_width() // 2, surface.get_height() // 2)
            surface.blit(font_surface, font_rect)

            self.menu_surfaces.append(surface)
        
        self.move_menu_selector(0)


    def update_menu_surface(self):
        self.draw_menu_surfaces()
        pygame.display.update()



class GameInterface:
    
    def __init__(self, width, height):
        print("Now starting the game!")

        pygame.init()
        pygame.display.set_caption("My Amazing Snake Game")
        self.game_window = pygame.display.set_mode((width, height))
        
    
    def get_game_window(self):
        return self.game_window


    @staticmethod
    def quit():
        print("Now quitting the game!")
        
        pygame.quit()
        quit()



class HighScoreLayoutHandler:
    DEFAULT_SCORES_DISP = 10

    def __init__(self, game_window):
        self.game_window = game_window


    def populate_and_draw_columns_to_surface(self, surface, columns, bold=False):
        x, y = surface.get_width() // len(columns), surface.get_height()
        offset = 10
        font_size = y // 2

        for i, column in enumerate(columns):
            cell_surface = surface.subsurface(x * i, 0, x, y)
            
            font = pygame.font.SysFont(GAME_FONT, font_size, bold)
            font_surface = font.render(str(column), True, SNAKE_BLACK)
            font_rect = font_surface.get_rect()
            font_rect.x = x // offset
            font_rect.y = y // offset
            
            cell_surface.blit(font_surface, font_rect)
            pygame.draw.rect(cell_surface, SNAKE_BLACK, (0, 0, *cell_surface.get_size()), 1)
    

    def list_scores(self, scores, start_rank, totals):
        columns = ["RANK", "PLAYER", "MODE", "SCORE", "TIME (s)", "DATE"]
        totals_disp = [f"TOT: {total}" for total in totals]

        if len(scores) > self.DEFAULT_SCORES_DISP:
            scores = scores[0:self.DEFAULT_SCORES_DISP]
        
        rows = self.DEFAULT_SCORES_DISP + 2
        x, y = self.game_window.get_width(), self.game_window.get_height() // rows
        self.game_window.fill(SNAKE_WHITE)

        row_surfaces = [self.game_window.subsurface((0, i * y, x, y)) for i in range(rows)]

        self.populate_and_draw_columns_to_surface(row_surfaces[0], columns, True)

        for i, score in enumerate(scores, start=1):
            score_surface = row_surfaces[i]
            player, mode, score, pl_time, date = score
            display_msgs = [start_rank + i, player, mode, score, f"{pl_time:.2f}", time.strftime('%Y-%m-%d', time.localtime(date))]
            
            self.populate_and_draw_columns_to_surface(score_surface, display_msgs)

        self.populate_and_draw_columns_to_surface(row_surfaces[-1], totals_disp, True)

        pygame.display.flip()



class PlayerNameLayoutHandler:
    NAME_MSG = "ENTER NAME:"
    X_SPLIT = 9
    Y_SPLIT = 5
    NAME_OFFSET = 2
    INPUT_NAME_FONT = "comic sans ms"
    UNDERSCORE_OFFSET = 5
    UNDERSCORE_SIZE = 10
    BLINK_SPEED = 0.5


    def __init__(self, game_window, name_length):
        self.game_window = game_window
        self.name_length = name_length
        self.name_rects = []
        self.font_size = 0
        self.init_name_rects()


    def init_name_rects(self):
        x, y = self.game_window.get_width() / self.X_SPLIT, self.game_window.get_height() / self.Y_SPLIT
        self.name_rects = [pygame.Rect((i + self.NAME_OFFSET) * x, 2 * y, x, y) for i in range(self.name_length)]
    

    def add_underscore_to_rect(self, rect, color=SNAKE_BLUE):
        underscore = pygame.Rect(rect.bottomleft, (rect.width - (2 * self.UNDERSCORE_OFFSET), self.UNDERSCORE_SIZE))
        underscore.x += self.UNDERSCORE_OFFSET
        pygame.draw.rect(self.game_window, color, underscore)


    def add_underscores(self,):
        for rect in self.name_rects:
            self.add_underscore_to_rect(rect)


    def blink_current_underscore(self, player):
        blink_index = len(player)
        if blink_index < self.name_length and time.time() % 1 > self.BLINK_SPEED:
            self.add_underscore_to_rect(self.name_rects[blink_index], SNAKE_BLACK)


    def update_player_name(self, player):
        for i, char in enumerate(player):
            char_rect = self.name_rects[i]
            my_font = pygame.font.SysFont(self.INPUT_NAME_FONT, char_rect.height - 10)
            char_img = my_font.render(char.upper(), True, SNAKE_RED)
            self.game_window.blit(char_img, char_img.get_rect(center = char_rect.center))
        

    def add_name_message(self):
        offset_x, offset_y = self.game_window.get_width() // 2, self.game_window.get_height() // self.Y_SPLIT
        msg_font = pygame.font.SysFont(GAME_FONT, GAME_OVER_FONT_SIZE)

        msg_img = msg_font.render(self.NAME_MSG, True, SNAKE_RED)
        msg_rect = msg_img.get_rect()
        msg_rect.midtop = offset_x, offset_y

        self.game_window.blit(msg_img, msg_rect)


    def update_screen(self, player):
        self.game_window.fill(SNAKE_BLACK)
        self.add_name_message()
        self.update_player_name(player)
        self.add_underscores()
        self.blink_current_underscore(player)

        pygame.display.update()



class InstructionLayoutHandler:
    GAME_INSTRUCTION_FILE = "instructions.xml"
    HEADER_TEXT = " -- START INSTRUCTIONS -- "
    FOOTER_TEXT = " -- END INSTRUCTIONS -- "
    BACKGROUND_COLOR = SNAKE_WHITE
    TEXT_COLOR = SNAKE_BLACK
    FONT_SIZE = 20
    Y_SPLIT = 20


    def __init__(self, game_window):
        self.game_window = game_window
        self.game_window.fill(self.BACKGROUND_COLOR)
        self.text_surfaces = []
        self.init_text_surfaces()


    def get_empty_surface(self):
        x, y = self.game_window.get_width(), self.game_window.get_height() // self.Y_SPLIT
        surface = pygame.Surface((x, y))
        surface.fill(self.BACKGROUND_COLOR)
        return surface


    def get_centered_text_surface(self, text, bold=False):
        surface = self.get_empty_surface()
        text_font = pygame.font.SysFont(GAME_FONT, self.FONT_SIZE, bold)

        text_img = text_font.render(text, True, self.TEXT_COLOR)
        text_rect = text_img.get_rect()
        text_rect.centerx = surface.get_width() // 2

        surface.blit(text_img, text_rect)
        return surface


    def add_empty_surface(self, index=None):
        empty_surface = self.get_empty_surface()
        if index:
            self.text_surfaces.insert(index, empty_surface)
        else:
            self.text_surfaces.append(empty_surface)
        

    def add_text_line(self, text, bold=False):
        surface = self.get_empty_surface()
        my_font = pygame.font.SysFont(GAME_FONT, self.FONT_SIZE, bold)
        start_w = 0
        text_to_add = True

        for word in text.split():
            my_word = my_font.render(f"{word} ", True, (0, 0, 0))
            text_to_add = True

            if start_w + my_word.get_width() > surface.get_width():
                start_w = 0
                self.text_surfaces.append(surface)
                surface = self.get_empty_surface()
                text_to_add = False
            
            surface.blit(my_word, (start_w, 0))
            start_w += my_word.get_width()

        if text_to_add:
            self.text_surfaces.append(surface)


    def add_header_footer(self):
        head_surface = self.get_centered_text_surface(self.HEADER_TEXT, True)
        foot_surface = self.get_centered_text_surface(self.FOOTER_TEXT, True)

        self.text_surfaces.insert(0, head_surface)
        self.add_empty_surface(1)
        self.text_surfaces.append(foot_surface)
        self.add_empty_surface()


    def init_text_surfaces(self):
        tree = ET.parse(self.GAME_INSTRUCTION_FILE)
        root = tree.getroot()

        for section in root.findall("section"):
            title = section.attrib["name"]
            instructions = section.find("instruction").text
            
            self.add_text_line(title, True)
            self.add_text_line(instructions)
            self.add_empty_surface()

        self.add_header_footer()


    def update_view(self, start_index):
        if start_index >= len(self.text_surfaces):
            return
        
        view_surfaces = self.text_surfaces[start_index:start_index + self.Y_SPLIT]

        for i, surface in enumerate(view_surfaces):
            self.game_window.blit(surface, (0, i * surface.get_height()))
        
        pygame.display.update()


