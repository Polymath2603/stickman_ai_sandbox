import sys
import threading
from brain.high import HighLevelController

class AIInterface:
    """
    ai.py
    Translates CLI commands into Ollama AI prompts or directly applies actions via high.py
    """
    def __init__(self, high_level):
        self.high = high_level
        self.running = True
        
    def start_cli(self):
        print("--- Stickman AI CLI Started ---")
        print("Commands: 'walk [left/right]', 'push [left/right]', 'kick [left/right]', 'jump', 'crouch', 'stop'")
        print("Type 'exit' to quit AI CLI.")

        while self.running:
            try:
                cmd = input("Stickman> ").strip()
                if cmd == "exit":
                    self.running = False
                    break
                elif cmd == "stop":
                    self.high.stop()
                else:
                    self._parse_and_execute_command(cmd)
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break

    def _parse_and_execute_command(self, cmd):
        """Parse commands like 'walk left', 'push right', 'kick right'"""
        parts = cmd.lower().split()
        if len(parts) == 0:
            return

        action = parts[0]
        direction = parts[1] if len(parts) > 1 else "right"  # Default to right

        if action in ["walk", "push", "kick"]:
            if direction not in ["left", "right"]:
                direction = "right"  # Default fallback

            if action == "kick":
                # For kick, also specify which leg
                leg = "right" if direction == "right" else "left"
                self.high.execute_action(action, leg=leg)
            else:
                self.high.execute_action(action, direction=direction)

        elif action in ["jump", "crouch"]:
            self.high.execute_action(action)
        else:
            print(f"Unknown command: {cmd}")
            print("Available: walk/push/kick [left/right], jump, crouch, stop")
                
    def run_in_background(self):
        t = threading.Thread(target=self.start_cli)
        t.daemon = True
        t.start()
        return t
