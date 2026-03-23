import pygame
import sys
import argparse
from sandbox import Sandbox
from body import Body
from brain.low import LowLevelController
from utils import config

def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()

    sandbox = Sandbox()
    
    # Starting ragdoll position
    start_pos = (0, 2)
    stickman = Body(sandbox.space, position=start_pos)
    
    # Low-level brain only for now
    low = LowLevelController(stickman)

    active_keys = set()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            sandbox.handle_mouse_events(event)
            
            if event.type == pygame.KEYDOWN:
                active_keys.add(event.key)
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset ragdoll
                    for b in list(stickman.bodies.values()) + [stickman.bodies.get("head")]:
                        if b in sandbox.space.bodies:
                            sandbox.space.remove(b)
                    for j in stickman.joints.values():
                        if j in sandbox.space.constraints:
                            sandbox.space.remove(j)
                    for m in stickman.motors.values():
                        if m in sandbox.space.constraints:
                            sandbox.space.remove(m)
                    
                    stickman.create_ragdoll(start_pos=start_pos)
                    sandbox.reset_objects()
                    active_keys.clear()
            
            if event.type == pygame.KEYUP:
                if event.key in active_keys:
                    active_keys.remove(event.key)

        # No automatic stiffening with 'W' anymore
        low.relax_all()

        sandbox.step()
        sandbox.render()
        
        # Simple HUD
        hud = sandbox.font.render(f"Pymunk Ragdoll | Drag with Mouse | 'R' to reset", True, (255, 255, 255))
        sandbox.screen.blit(hud, (10, 10))
        
        pygame.display.flip()
        sandbox.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
