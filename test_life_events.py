import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import directly from the moneySmartz.py file (not the package)
import moneySmartz
Game = moneySmartz.Game
Player = moneySmartz.Player

def test_life_events():
    """Test that life events trigger GUI screens instead of console output."""
    print("[DEBUG_LOG] Testing life events GUI display...")

    # Create a game instance
    game = Game()

    # Initialize player properly
    game.player = Player("TestPlayer")

    # Test high school graduation event
    game.player.age = 18
    game.player.education = "High School"

    print(f"[DEBUG_LOG] Player age: {game.player.age}")
    print(f"[DEBUG_LOG] Player education: {game.player.education}")

    # Check if GUI life events are triggered
    result = game.check_life_stage_events_gui()

    if result:
        print("[DEBUG_LOG] SUCCESS: Life event GUI screen was triggered!")
        return True
    else:
        print("[DEBUG_LOG] FAILURE: Life event GUI screen was NOT triggered!")
        return False

if __name__ == "__main__":
    test_life_events()
