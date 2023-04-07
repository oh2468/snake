import pygame
import time
from layout_handlers import *
from game_modes import *


class NameInputHandler:
    PLAYER_NAME_LENGTH = 5
    INPUT_FPS_TICK = 10

    def __init__(self, game_window):
        self.game_window = game_window
        self.loHandler = PlayerNameLayoutHandler(self.game_window, self.PLAYER_NAME_LENGTH)
        self.player = []

    
    def run_main_loop(self):
        fps = pygame.time.Clock()
        complete_name = False

        while not complete_name:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    GameInterface.quit()

                if event.type == pygame.KEYDOWN:
                    key = event.unicode
                    if key.isalpha() and len(self.player) < 5:
                        self.player.append(key)
                    if event.key == pygame.K_BACKSPACE and len(self.player) > 0:
                        self.player.pop()
                    if event.key == pygame.K_RETURN and len(self.player) == self.PLAYER_NAME_LENGTH:
                        #print("".join(self.player))
                        complete_name = True
            
            self.loHandler.update_screen(self.player)
            fps.tick(self.INPUT_FPS_TICK)
        
        return "".join(self.player)



class MainMenuInputHandler:

    def __init__(self, game_window, dbHandler):
        self.game_window = game_window
        self.dbHandler = dbHandler
        self.init_menu_layout_handler()

    
    def init_menu_layout_handler(self):
        self.MENU_ITEMS = [
            {"label": "Instructions", "action": lambda: InstructionInputHandler(self.game_window).main_loop(), },
            {"label": "Standard Mode", "action": lambda: SnakeStandard(self.game_window).run_game(), },
            {"label": "Walls Mode", "action": lambda: SnakeMedium(self.game_window).run_game(), },
            {"label": "Poison Mode", "action": lambda: SnakeHard(self.game_window).run_game(), },
            {"label": "High Scores", "action": lambda: HighScoreInputHandler(self.game_window, self.dbHandler).run(), },
        ]

        self.menuLoHandler = MenuLayoutHandler(self.game_window, [item["label"] for item in self.MENU_ITEMS])


    def run(self):
        menu_index = 0
        interested = True
        fps = pygame.time.Clock()

        while interested:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    GameInterface.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        interested = False
                    if event.key == pygame.K_UP and menu_index > 0:
                        menu_index -= 1
                    if event.key == pygame.K_DOWN and menu_index < (len(self.MENU_ITEMS) - 1):
                        menu_index += 1
                    if event.key == pygame.K_RETURN:
                        #print(self.MENU_ITEMS[menu_index]["label"])
                        game_result = self.MENU_ITEMS[menu_index]["action"]()
                        if game_result:
                            #print(game_result)
                            nameHandler = NameInputHandler(self.game_window)
                            player_name = nameHandler.run_main_loop()
                            self.dbHandler.set_score(player_name, *game_result)

                    self.menuLoHandler.move_menu_selector(menu_index)

            self.menuLoHandler.update_menu_surface()
            fps.tick(MAIN_VIEW_FPS)
        
        

class HighScoreInputHandler(MainMenuInputHandler):

    def __init__(self, game_window, dbHandler):
        super().__init__(game_window, dbHandler)
        self.scoreDispHandl = HighScoreLayoutHandler(self.game_window)
        self.scores = []


    def delete_all_db_scores(self):
        self.scores = []
        self.dbHandler.delete_all_scores()


    def get_score_portion(self, start, amount):
        return self.scores[start:start + amount]


    def get_db_totals(self, mode):
        db_totals = self.dbHandler.get_totals(mode)
        
        if None in db_totals:
            return [0 for _ in range(6)]

        totals = list(db_totals[:-2])
        totals[4] = f"{totals[4]:.2f}"

        start_date_ts = db_totals[-2]
        end_date_ts = db_totals[-1]

        all_dates = self.dbHandler.get_all_dates()
        unique_days = {time.localtime(date)[:3] for date, *_ in all_dates}

        totals.append(len(unique_days))
        return totals


    def score_display_loop(self, mode):
        browsing = True
        self.scores = self.dbHandler.get_mode_scores(mode)
        totals = self.get_db_totals(mode)
        start_index, num_scores = 0, self.scoreDispHandl.DEFAULT_SCORES_DISP
        scores_to_display = self.get_score_portion(start_index, num_scores)

        fps = pygame.time.Clock()
        while browsing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    GameInterface.quit()

                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP:
                            if start_index > 0:
                                start_index -= 1
                                scores_to_display = self.get_score_portion(start_index, num_scores)
                        case pygame.K_DOWN:
                            if start_index < (len(self.scores) - num_scores):
                                start_index += 1
                                scores_to_display = self.get_score_portion(start_index, num_scores)
                        case _:
                            browsing = False
            if scores_to_display or not self.scores:
                self.scoreDispHandl.list_scores(scores_to_display, start_index, totals)
                scores_to_display = []

            fps.tick(MAIN_VIEW_FPS)


    def init_menu_layout_handler(self):
        self.MENU_ITEMS = [
            {"label": "All Scores", "action": lambda: self.score_display_loop(""), },
            {"label": "Standard Scores", "action": lambda: self.score_display_loop("Standard"), },
            {"label": "Walls Scores", "action": lambda: self.score_display_loop("Walls"), },
            {"label": "Poison Scores", "action": lambda: self.score_display_loop("Poison"), },
            {"label": "DELETE All Scores", "action": lambda: self.delete_all_db_scores(), },
        ]

        self.menuLoHandler = MenuLayoutHandler(self.game_window, [item["label"] for item in self.MENU_ITEMS])



class InstructionInputHandler:

    def __init__(self, game_window):
        self.game_window = game_window
        self.loHandler = InstructionLayoutHandler(self.game_window)


    def main_loop(self):
        fps = pygame.time.Clock()
        done = False
        index = 0

        self.loHandler.update_view(index)
                
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    GameInterface.quit()

                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP:
                            index -= 1 if index > 0 else index
                        case pygame.K_DOWN:
                            index += 1
                        case _:
                            if event.key != pygame.K_LEFT and event.key != pygame.K_RIGHT:
                                done = True
                    
                    self.loHandler.update_view(index)
            
            fps.tick(MAIN_VIEW_FPS)


