import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
from moneySmartz import Game, GUIManager
from moneySmartz.screens import TitleScreen, GameScreen

def test_gui_life_events():
    """Test GUI life events to see if they're working properly."""
    print("[DEBUG_LOG] Testing GUI life events...")
    
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    
    # Create game instance
    game = Game()
    
    # Create GUI manager
    gui_manager = GUIManager(game)
    game.gui_manager = gui_manager
    
    # Initialize player properly
    from moneySmartz.models import Player
    game.player = Player("TestPlayer")
    
    # Set up for high school graduation event
    game.player.age = 18
    game.player.education = "High School"
    
    print(f"[DEBUG_LOG] Player age: {game.player.age}")
    print(f"[DEBUG_LOG] Player education: {game.player.education}")
    
    # Test the GUI life events method
    print("[DEBUG_LOG] Calling check_life_stage_events_gui()...")
    result = game.check_life_stage_events_gui()
    
    if result:
        print("[DEBUG_LOG] SUCCESS: GUI life event was triggered!")
        print(f"[DEBUG_LOG] Current screen: {type(gui_manager.current_screen).__name__}")
    else:
        print("[DEBUG_LOG] FAILURE: GUI life event was NOT triggered!")
    
    # Clean up
    pygame.quit()
    
    return result

if __name__ == "__main__":
    test_gui_life_events()