import pygame
import time
import random
from layout_handlers import *


DEFAULT_SNAKE_SPEED = 15
DEFAULT_SNAKE_HEAD = [100, 50]
DEFAULT_SNAKE_LENGTH = 4
SPEED_FF_INCREASE = 2
APPLE_SPEED_UP_INTERVAL = 3
DEFAULT_LIVES = 3
START_DIRECTION = pygame.K_RIGHT
SCORE_INTERVAL = 10

WALL_LENGTH = 16
HORIZONTAL = "horizontal"
VERTICAL = "vertical"
WALL_DIRECTIONS = [HORIZONTAL, VERTICAL]

DEFAULT_POISONED_APPLES = 3

PAUSE_KEY = pygame.K_SPACE
VALID_KEYS = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
OPPOSITES = {pygame.K_UP: pygame.K_DOWN, 
    pygame.K_DOWN: pygame.K_UP, 
    pygame.K_LEFT: pygame.K_RIGHT, 
    pygame.K_RIGHT: pygame.K_LEFT, 
}


class SnakeStandard:
    GAME_MODE = "Standard"

    def __init__(self, game_window):
        print("Snake Standard initialized")
        self.game_window = game_window
        self.loHandler = SnakeLayoutHandler(self.game_window)
        self.game_surface = self.loHandler.get_game_surface()
        self.window_x, self.window_y = self.game_surface.get_size()
        self.init_game_variables()

    
    def init_game_variables(self):
        self.head_direction = START_DIRECTION
        self.picked_apples = 0
        self.score = 0
        self.apple_spawned = False
        self.apple_location = []
        self.snake_head = DEFAULT_SNAKE_HEAD.copy()
        self.snake_body = [[self.snake_head[0] - (i * PIXEL_SIZE), self.snake_head[1]] for i in range(DEFAULT_SNAKE_LENGTH)]
        self.occupied_locations = [self.snake_body, self.apple_location]


    def location_is_occupied(self, locations):
        #return any(self.game_surface.get_at(loc) != SNAKE_BLACK for loc in locations)
        return any(loc in occupied for loc in locations for occupied in self.occupied_locations)


    def get_new_location(self, xy_limits):
        limit_x, limit_y = xy_limits
        x_location = random.randrange(1, (self.window_x // PIXEL_SIZE) - limit_x) * PIXEL_SIZE
        y_location = random.randrange(1, (self.window_y // PIXEL_SIZE) - limit_y) * PIXEL_SIZE
        new_location = [x_location, y_location]
        return new_location if not self.location_is_occupied([new_location]) else self.get_new_location(xy_limits)


    def update_apple_if_needed(self):
        if self.apple_spawned:
            return False

        self.apple_location = self.get_new_location((0, 0))
        self.apple_spawned = True
        return True


    def add_new_window_contents(self):
        self.loHandler.clear_game_surface()

        self.loHandler.add_snake_to_game_surface(self.snake_body, self.head_direction, SNAKE_GREEN, PIXEL_SIZE)
        self.loHandler.add_blocks_game_surface([self.apple_location], SNAKE_WHITE, PIXEL_SIZE)


    def get_updated_info_fields(self, speed, time):
        return [
            f"SCORE: {self.score}", 
            f"MODE: {self.GAME_MODE}", 
            f"SPEED: {speed}", 
            f"TIME: {int(time)} s", 
        ]


    def update_score(self, speed, time):
        updated_info = self.get_updated_info_fields(speed, time)
        self.loHandler.update_info_surface(updated_info)


    def game_over(self):
        self.loHandler.set_middle_screen_text(f"GAME OVER! Score: {self.score}", SNAKE_RED)


    def set_pause_screen(self):
        self.loHandler.set_middle_screen_text("GAME IS PAUSED", SNAKE_WHITE)


    def validate_snake_in_bounds(self):
        valid_snake = True

        if self.snake_head[0] < 0 or self.snake_head[0] > self.window_x - PIXEL_SIZE:
            valid_snake = False
        
        if self.snake_head[1] < 0 or self.snake_head[1] > self.window_y - PIXEL_SIZE:
            valid_snake = False
        
        if self.snake_head in self.snake_body[1::]:
            valid_snake = False

        return valid_snake


    def apple_is_bitten(self):
        return self.snake_head[0] == self.apple_location[0] and self.snake_head[1] == self.apple_location[1]


    def update_snake_head(self, direction):
        self.head_direction = direction

        if direction == pygame.K_UP:
            self.snake_head[1] -= PIXEL_SIZE
        if direction == pygame.K_DOWN:
            self.snake_head[1] += PIXEL_SIZE
        if direction == pygame.K_LEFT:
            self.snake_head[0] -= PIXEL_SIZE
        if direction == pygame.K_RIGHT:
            self.snake_head[0] += PIXEL_SIZE


    def update_snake_body(self):
        self.snake_body.insert(0, list(self.snake_head))
        
        if self.apple_is_bitten():
            self.score += SCORE_INTERVAL
            self.picked_apples += 1
            self.apple_spawned = False
        else:
            self.snake_body.pop()


    def run_game(self):
        self.init_game_variables()
        self.update_apple_if_needed()
        direction = change_to = self.head_direction
        playing, paused = True, False
        fps = pygame.time.Clock()
        start_time = time.time()

        while playing:
            snake_speed = DEFAULT_SNAKE_SPEED + (self.picked_apples // APPLE_SPEED_UP_INTERVAL)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    GameInterface.quit()
                    
                if event.type == pygame.KEYDOWN and event.key in VALID_KEYS and not paused:
                    change_to = event.key
                if event.type == pygame.KEYDOWN and event.key == PAUSE_KEY:
                    paused = not paused
           
            if paused:
                self.set_pause_screen()
            else:
                if change_to == direction and pygame.key.get_pressed()[direction]:
                    snake_speed *= SPEED_FF_INCREASE
                
                if direction != OPPOSITES[change_to]:
                    direction = change_to
                
                self.update_snake_head(direction)
                self.update_snake_body()
                
                valid_snake = self.validate_snake_in_bounds()

                if valid_snake:
                    self.update_apple_if_needed()
                    self.add_new_window_contents()
                else:
                    self.game_over()
                    playing = False

            self.update_score(0 if paused else snake_speed, time.time() - start_time)

            self.loHandler.update_game_window()
            fps.tick(snake_speed)
        
        stop_time = time.time()
        play_time = stop_time - start_time
        time.sleep(2)

        return (self.GAME_MODE, self.score, play_time, stop_time)



class SnakeMedium(SnakeStandard):
    GAME_MODE = "Walls"
    
    def __init__(self, game_window):
        print("Snake Medium initialized")
        super().__init__(game_window)
        self.wall = []
        self.occupied_locations.append(self.wall)


    def set_new_wall(self):
        wall_dir = random.choice(WALL_DIRECTIONS)
        wall_start = self.get_new_location((WALL_LENGTH, 0) if wall_dir == HORIZONTAL else (0, WALL_LENGTH))

        if wall_dir == HORIZONTAL:
            self.wall = [[wall_start[0] + (i * PIXEL_SIZE), wall_start[1]] for i in range(WALL_LENGTH)]
        elif wall_dir == VERTICAL:
            self.wall = [[wall_start[0], wall_start[1] + (i * PIXEL_SIZE)] for i in range(WALL_LENGTH)]
        else:
            self.wall = []

        if super().location_is_occupied(self.wall):
            return self.set_new_wall()


    def validate_snake_in_bounds(self):
        valid_snake = super().validate_snake_in_bounds()

        if self.snake_head in self.wall:
            valid_snake = False

        return valid_snake


    def update_apple_if_needed(self):
        update_needed = super().update_apple_if_needed()
        
        if update_needed:
            self.set_new_wall()
        
        return update_needed


    def add_new_window_contents(self):
        super().add_new_window_contents()
        self.loHandler.add_blocks_game_surface(self.wall, SNAKE_ORANGE, PIXEL_SIZE)



class SnakeHard(SnakeMedium):
    GAME_MODE = "Poison"

    def __init__(self, game_window):
        print("SPAWNING THE HARD VERSION!")
        super().__init__(game_window)
        self.poisoned_apples = []
        self.occupied_locations.append(self.poisoned_apples)

    
    def set_poisoned_apples(self):
        self.poisoned_apples = [self.get_new_location((0, 0)) for _ in range(DEFAULT_POISONED_APPLES)]


    def validate_snake_in_bounds(self):
        valid_snake = super().validate_snake_in_bounds()

        if self.snake_head in self.poisoned_apples:
            valid_snake = False

        return valid_snake

    def update_apple_if_needed(self):
        update_needed = super().update_apple_if_needed()

        if update_needed:
            self.set_poisoned_apples()
        
        return update_needed


    def add_new_window_contents(self):
        super().add_new_window_contents()
        self.loHandler.add_blocks_game_surface(self.poisoned_apples, SNAKE_BLUE, PIXEL_SIZE)



class SnakeExtreme(SnakeHard):
    pass


