from db_handlers import DatabaseHandler
from layout_handlers import GameInterface
from input_handlers import MainMenuInputHandler


if __name__ == "__main__":
    window_size = (720, 480)
    
    dbHandler = DatabaseHandler()
    game_interface = GameInterface(*window_size)
    game_window = game_interface.get_game_window()

    mainMenu = MainMenuInputHandler(game_window, dbHandler)

    mainMenu.run()

    game_interface.quit()
