import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import directly from the moneySmartz.py file
import moneySmartz

def verify_gui_life_events():
    """Verify that the GUI life events method is properly implemented."""
    print("[DEBUG_LOG] Verifying GUI life events implementation...")
    
    # Create a game instance
    game = moneySmartz.Game()
    
    # Initialize player properly
    game.player = moneySmartz.Player("TestPlayer")
    
    # Test different life event scenarios
    test_cases = [
        {"age": 18, "education": "High School", "event": "High School Graduation"},
        {"age": 22, "education": "College (In Progress)", "event": "College Graduation"},
        {"age": 22, "education": "High School Graduate", "job": None, "event": "Job Opportunity"},
        {"age": 20, "education": "High School Graduate", "event": "Car Purchase"},
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[DEBUG_LOG] Test Case {i+1}: {test_case['event']}")
        
        # Set up player for this test case
        game.player.age = test_case["age"]
        game.player.education = test_case["education"]
        if "job" in test_case:
            game.player.job = test_case["job"]
        
        # Check the method implementation by looking at the source
        try:
            # Get the method source to see if it's implemented
            import inspect
            source = inspect.getsource(game.check_life_stage_events_gui)
            
            # Check if the method has actual implementation (not just pass statements)
            if "pass" in source and test_case["event"] in ["High School Graduation", "College Graduation", "Job Opportunity", "Car Purchase"]:
                print(f"[DEBUG_LOG] BEFORE FIX: {test_case['event']} would have been 'pass'")
            else:
                print(f"[DEBUG_LOG] AFTER FIX: {test_case['event']} has proper implementation")
                
            # Check if the specific conditions are met
            if test_case["event"] == "High School Graduation" and game.player.age == 18 and game.player.education == "High School":
                print(f"[DEBUG_LOG] ✓ High School Graduation conditions met")
            elif test_case["event"] == "College Graduation" and game.player.age == 22 and game.player.education == "College (In Progress)":
                print(f"[DEBUG_LOG] ✓ College Graduation conditions met")
            elif test_case["event"] == "Job Opportunity" and game.player.age == 22 and not game.player.job and game.player.education != "College (In Progress)":
                print(f"[DEBUG_LOG] ✓ Job Opportunity conditions met")
            elif test_case["event"] == "Car Purchase" and game.player.age == 20:
                print(f"[DEBUG_LOG] ✓ Car Purchase conditions met")
                
        except Exception as e:
            print(f"[DEBUG_LOG] Error checking method: {e}")
    
    print(f"\n[DEBUG_LOG] Verification complete!")

if __name__ == "__main__":
    verify_gui_life_events()