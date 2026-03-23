from brain.low import LowLevelController
import importlib
import os

class HighLevelController:
    """
    brain/high.py
    High level control. Uses low-level to do high-level functions.
    Sequences actions dynamically from the actions folder.
    """
    def __init__(self, stickman):
        self.low = LowLevelController(stickman)
        self.stickman = stickman
        self.current_action = None

    def execute_action(self, action_name, **kwargs):
        """Loads and starts an action with optional parameters."""
        try:
            module = importlib.import_module(f"skills.{action_name.lower()}")
            action_class = getattr(module, action_name.capitalize() + "Action")

            # Pass kwargs to the action constructor
            self.current_action = action_class(self.stickman, self.low, **kwargs)
            print(f"HighLevel: Executing {action_name} with params {kwargs}")
        except Exception as e:
            print(f"HighLevel: Action '{action_name}' failed to load: {e}")
            self.current_action = None

    def step(self):
        """Ticks the current action."""
        if self.current_action:
            if self.current_action.is_finished():
                print(f"HighLevel: Action finished.")
                self.current_action = None
            else:
                self.current_action.step()

    def stop(self):
        self.current_action = None
        self.low.relax_all()
