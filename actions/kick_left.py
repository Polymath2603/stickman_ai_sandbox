import math

class Kick_leftAction:
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0

    def step(self):
        self.ticks += 1
        
        if self.ticks < 10:
            # Phase 1: Wind-up (Lift left leg back/up)
            # Negative hip is left/forward, so positive is right/back
            self.low.set_target_angle("l_hip", -0.8, max_torque=500, max_speed=10.0)
            self.low.set_target_angle("l_knee", -2.0, max_torque=500, max_speed=10.0)
            
            # Balance on right leg
            self.low.set_target_angle("r_hip", 0.2, max_torque=500)
            self.low.set_target_angle("r_knee", -0.2, max_torque=500)
            self.low.set_target_angle("r_ankle", 0.1, max_torque=300)
            
        elif self.ticks < 18:
            # Phase 2: The Kick (Snap left leg forward/left)
            self.low.set_target_angle("l_hip", 1.2, max_torque=1200, max_speed=30.0, kp=40.0)
            self.low.set_target_angle("l_knee", 0.0, max_torque=1200, max_speed=30.0, kp=40.0)
            
            # Balance tilt
            self.low.set_target_angle("r_ankle", -0.2, max_torque=400)
        else:
            # Phase 3: Recover
            self.low.relax_all()

    def is_finished(self):
        return self.ticks > 30
