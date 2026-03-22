import sys
import itertools
import time
import pygame
from sandbox import Sandbox
from body import Body
from brain.low import LowLevelController
from brain.high import HighLevelController
from brain.idle import IdleController
from utils.reporter import Reporter

# List of all actions to test
ACTIONS = [
    "walk_right", "walk_left", "kick_right", "kick_left", "push_right", "push_left",
    "jump", "crouch", "hold", "throw", "pushup"
]

# Parameter grid for low-level control (torque, kp, max_speed)
PARAM_GRID = list(itertools.product(
    [100, 300, 600, 1200],   # max_torque
    [5.0, 10.0, 15.0, 25.0], # kp
    [2.0, 4.0, 8.0, 15.0]    # max_speed
))

FRAMES_PER_ACTION = 90


def test_all_actions():
    sandbox = Sandbox()
    start_pos = (sandbox.s2w((600, 400))[0], 0.2)
    stickman = Body(sandbox.world, position=start_pos)
    low = LowLevelController(stickman)
    high = HighLevelController(stickman)
    idle = IdleController(stickman, low)

    for action in ACTIONS:
        print(f"\n=== TESTING ACTION: {action} ===")
        for (max_torque, kp, max_speed) in PARAM_GRID:
            print(f"-- Params: torque={max_torque}, kp={kp}, max_speed={max_speed}")
            # Patch low-level controller for this test
            orig_set_target = low.set_target_angle
            def patched_set_target_angle(joint, angle, **kwargs):
                kwargs['max_torque'] = max_torque
                kwargs['kp'] = kp
                kwargs['max_speed'] = max_speed
                return orig_set_target(joint, angle, **kwargs)
            low.set_target_angle = patched_set_target_angle

            high.execute_action(action)
            idle.is_active = False  # Let action override
            frames = 0
            errors = []
            while frames < FRAMES_PER_ACTION:
                # Step controllers
                is_action_active = (high.current_action is not None)
                is_mouse_active = (sandbox.mouse_joint is not None)
                idle.update(is_action_active=is_action_active, is_mouse_active=is_mouse_active)
                high.step()
                sandbox.step()
                # High-frequency reporting
                print(f"[Frame {frames}] Action: {action}")
                Reporter.print_diagnostics(stickman)
                # Print object diagnostics
                for obj_name, body in sandbox.__dict__.items():
                    if hasattr(body, 'position'):
                        print(f"Object {obj_name}: pos={getattr(body, 'position', None)} vel={getattr(body, 'linearVelocity', None)}")
                # Check for falling or instability
                if hasattr(stickman, 'bodies'):
                    torso = stickman.bodies.get('torso')
                    if torso and abs(getattr(torso, 'angle', 0)) > 1.5:
                        errors.append(f"Torso fell over at frame {frames}")
                        break
                frames += 1
                pygame.event.get()  # Prevent window freeze
            if errors:
                print(f"[FAIL] {action} with params {max_torque},{kp},{max_speed}: {errors[-1]}")
            else:
                print(f"[PASS] {action} with params {max_torque},{kp},{max_speed}")
            # Reset stickman for next test
            for b in stickman.bodies.values():
                sandbox.world.DestroyBody(b)
            stickman.bodies.clear()
            stickman.joints.clear()
            stickman.create_ragdoll(start_pos=start_pos)
            sandbox.reset_objects()
            high.stop()
            time.sleep(0.05)
    print("\nAll actions tested.")

if __name__ == "__main__":
    test_all_actions()
