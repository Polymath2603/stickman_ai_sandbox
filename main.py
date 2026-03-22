import pygame
import sys
from sandbox import Sandbox
from body import Body
from brain.low import LowLevelController
from brain.high import HighLevelController
from brain.idle import IdleController

import argparse
from utils.reporter import Reporter
from utils import config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Action to test headlessly")
    parser.add_argument("--frames", type=int, default=120, help="Frames to test")
    parser.add_argument("--demo", action="store_true", help="Run automated visual demo")
    args = parser.parse_args()

    sandbox = Sandbox()
    
    # Starting ragdoll position
    start_pos = (sandbox.s2w((600, 400))[0], 0.2)
    stickman = Body(sandbox.world, position=start_pos)
    
    # Brains
    low = LowLevelController(stickman)
    high = HighLevelController(stickman)
    idle = IdleController(stickman, low)

    active_keys = set()
    frames_simulated = 0

    running = True
    validation_pending = False
    validation_result = None
    last_action = None
    test_commands = [
        # Example: (joint, angle, torque, kp, max_speed)
        ("r_hip", 0.5, 600, 10.0, 5.0),
        ("l_hip", -0.5, 600, 10.0, 5.0),
        ("r_knee", -1.0, 400, 8.0, 4.0),
        ("l_knee", -1.0, 400, 8.0, 4.0),
        # Add more as needed for your test
    ]
    test_index = 0
    awaiting_validation = False
    validation_message = ""
    while running:
        if args.test:
            # Automated test mode with validation
            if test_index < len(test_commands):
                joint, angle, torque, kp, max_speed = test_commands[test_index]
                low.set_target_angle(joint, angle, max_torque=torque, kp=kp, max_speed=max_speed)
                validation_message = f"Validate: {joint} angle={angle} torque={torque} kp={kp} max_speed={max_speed}"
                awaiting_validation = True
            else:
                print("All test commands validated. Exiting.")
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and hasattr(sandbox, 'validation_button_rect'):
                    if sandbox.validation_button_rect.collidepoint(event.pos):
                        if awaiting_validation:
                            validation_pending = True
            sandbox.step()
            sandbox.render()
            # Draw validation message on screen
            if validation_message:
                label = sandbox.font.render(validation_message, True, (255, 255, 0))
                sandbox.screen.blit(label, (40, config.SCREEN_HEIGHT - 80))
            pygame.display.flip()
            sandbox.clock.tick(60)
            if validation_pending:
                print(f"[AGENT] {validation_message} -- Is it correct? (Click YES/NO)")
                user_response = input("yes/no: ").strip().lower()
                if user_response == "yes":
                    test_index += 1
                    validation_pending = False
                    awaiting_validation = False
                    validation_message = ""
                else:
                    print("[AGENT] Please enter new values: joint,angle,torque,kp,max_speed (comma separated): ", end="", flush=True)
                    vals = input().strip().split(",")
                    if len(vals) == 5:
                        joint, angle, torque, kp, max_speed = vals
                        low.set_target_angle(joint.strip(), float(angle), max_torque=float(torque), kp=float(kp), max_speed=float(max_speed))
                        validation_message = f"Validate: {joint} angle={angle} torque={torque} kp={kp} max_speed={max_speed}"
                        # Do not increment test_index, repeat validation
                    else:
                        print("[AGENT] Invalid input. Please enter five values.")
                # Redraw after input
                sandbox.render()
                if validation_message:
                    label = sandbox.font.render(validation_message, True, (255, 255, 0))
                    sandbox.screen.blit(label, (40, config.SCREEN_HEIGHT - 80))
                pygame.display.flip()
        else:
            # ...existing code for interactive mode...
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                sandbox.handle_mouse_events(event)
                if event.type == pygame.KEYDOWN:
                    active_keys.add(event.key)
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r:
                        for b in stickman.bodies.values():
                            sandbox.world.DestroyBody(b)
                        stickman.bodies.clear()
                        stickman.joints.clear()
                        stickman.create_ragdoll(start_pos=start_pos)
                        sandbox.reset_objects()
                        active_keys.clear()
                        high.stop()
                    elif event.key == pygame.K_SPACE:
                        idle.toggle()
                if event.type == pygame.KEYUP:
                    if event.key in active_keys:
                        active_keys.remove(event.key)
            # ...existing code for key-based action selection and rendering...
                        for b in stickman.bodies.values():
                            sandbox.world.DestroyBody(b)
                        stickman.bodies.clear()
                        stickman.joints.clear()
                        stickman.create_ragdoll(start_pos=start_pos)
                        sandbox.reset_objects()
                        active_keys.clear()
                        high.stop()
                    elif event.key == pygame.K_SPACE:
                        idle.toggle()
                if event.type == pygame.KEYUP:
                    if event.key in active_keys:
                        active_keys.remove(event.key)

            # Action logic (unchanged)
            # ...existing code for key-based action selection...

            # Validation prompt/response
            if validation_pending:
                try:
                    user_input = input().strip().lower()
                    if user_input == "yes":
                        print("[AGENT] Action validated as correct!")
                        validation_result = True
                        validation_pending = False
                    elif user_input == "no":
                        print("[AGENT] Please enter new torque, kp, max_speed (comma separated): ", end="", flush=True)
                        vals = input().strip().split(",")
                        if len(vals) == 3:
                            torque, kp, max_speed = map(float, vals)
                            # Apply to all joints for demo (real agent would target specific ones)
                            for joint in stickman.joints:
                                low.set_target_angle(joint, 0.0, max_torque=torque, kp=kp, max_speed=max_speed)
                            print(f"[AGENT] Applied torque={torque}, kp={kp}, max_speed={max_speed} to all joints.")
                        else:
                            print("[AGENT] Invalid input. Please enter three numbers.")
                        validation_pending = False
                        validation_result = False
                except Exception as e:
                    print(f"[AGENT] Error: {e}")
                    validation_pending = False

            # ...existing code...
            is_action_active = (high.current_action is not None)
            is_mouse_active = (sandbox.mouse_joint is not None)
            idle.update(is_action_active=is_action_active, is_mouse_active=is_mouse_active)
            high.step()
            sandbox.step()
            sandbox.render()
            if sandbox.clock.get_time() > 0 and pygame.time.get_ticks() % 500 < 50:
                Reporter.print_diagnostics(stickman)
            hud = sandbox.font.render(f"Balance: {'ON' if idle.is_active else 'OFF'} | High: {type(high.current_action).__name__ if high.current_action else 'None'}", True, (255, 255, 255))
            sandbox.screen.blit(hud, (10, 10))
            pygame.display.flip()
            sandbox.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
