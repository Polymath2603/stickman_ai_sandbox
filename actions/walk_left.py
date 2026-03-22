import math

class Walk_leftAction:
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0

    def step(self):
        self.ticks += 1
        
        # Walking speed (slower, more stable)
        cycle = self.ticks * 0.07 
        
        # Lean left (positive ankle angle) to walk left
        self.low.set_target_angle("l_ankle", 0.15, max_torque=150, kp=8.0, max_speed=3.0)
        self.low.set_target_angle("r_ankle", 0.15, max_torque=150, kp=8.0, max_speed=3.0)
        
        # Hips swing opposite each other smoothly
        r_hip_angle = math.sin(cycle) * 0.6
        l_hip_angle = math.sin(cycle + math.pi) * 0.6 
        
        # Knee bends (negative) when hip is swinging left (velocity < 0). 
        # Velocity of sin(x) is cos(x). So bend when cos(x) < 0.
        r_knee_angle = -0.6 + math.cos(cycle) * 0.6 
        l_knee_angle = -0.6 + math.cos(cycle + math.pi) * 0.6
        
        # Firm torques to enforce ground arc against floor friction
        # Softened torques and PIDs (Suspension) to stop the legs acting like rigid iron stilts
        self.low.set_target_angle("r_hip", r_hip_angle, max_torque=300, kp=10.0, max_speed=4.0)
        self.low.set_target_angle("l_hip", l_hip_angle, max_torque=300, kp=10.0, max_speed=4.0)
        
        self.low.set_target_angle("r_knee", r_knee_angle, max_torque=150, kp=8.0, max_speed=4.0)
        self.low.set_target_angle("l_knee", l_knee_angle, max_torque=150, kp=8.0, max_speed=4.0)
        
        self.low.set_target_angle("r_shoulder", math.sin(cycle + math.pi) * 0.5, max_torque=100, max_speed=3.0)
        self.low.set_target_angle("l_shoulder", math.sin(cycle) * 0.5, max_torque=100, max_speed=3.0)

    def is_finished(self):
        return False
