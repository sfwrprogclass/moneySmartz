"""
Money Smartz: Financial Life Simulator

This is the main entry point for the Money Smartz game.
It initializes the game and starts the main game loop.
"""

import pygame
import sys
from moneySmartz import Game, GUIManager
from moneySmartz.screens import TitleScreen

def main():
    """
    Main function that initializes and runs the game.
    """
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    
    # Create game instance
    game = Game()
    
    # Create GUI manager
    gui_manager = GUIManager(game)
    game.gui_manager = gui_manager
    
    # Set initial screen
    gui_manager.set_screen(TitleScreen(game))
    
    # Run the game
    try:
        gui_manager.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()