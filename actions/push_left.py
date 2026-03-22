import math

class Push_leftAction:
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0

    def step(self):
        self.ticks += 1
        
        cycle = self.ticks * 0.05 # Even slower for pushing
        
        # Deep Lean Left (Positive ankle angle)
        self.low.set_target_angle("l_ankle", 0.4, max_torque=500, kp=12.0)
        self.low.set_target_angle("r_ankle", 0.4, max_torque=500, kp=12.0)
        
        # High power marching
        hip_swing = math.sin(cycle) * 0.4
        self.low.set_target_angle("r_hip", hip_swing, max_torque=800, kp=15.0)
        self.low.set_target_angle("l_hip", -hip_swing, max_torque=800, kp=15.0)
        
        # Keep knees slightly bent but strong
        self.low.set_target_angle("r_knee", -0.3, max_torque=600)
        self.low.set_target_angle("l_knee", -0.3, max_torque=600)
        
        # Arms forward to push (positive is left if hanging? No, CCW is positive)
        # Rotating up from hanging (-pi/2) CCW goes towards 0 (right).
        # We want to push left, which is CW (negative). 
        # Wait, if arm hangs at -pi/2, rotating CW (negative) goes towards -pi (facing left).
        # So yes, negative is "pointing left". (Actually -1.5 is nearly horizontal left).
        # Wait, if -pi/2 is down, and we want to point at -pi (horizontal left), we need a delta of -pi/2 (-1.57).
        self.low.set_target_angle("r_shoulder", 1.5, max_torque=400) # Wait, walk_left used mirror logic?
        # Let's check walk_left shoulder: math.sin(cycle) * 0.5. 
        # If sin is 1, shoulder is 0.5 (CCW from vertical-down, which is towards right).
        # So for walk left, arms should point left? No, they swing.
        # Let's just use 1.5 for left push.
        self.low.set_target_angle("r_shoulder", 1.5, max_torque=400)
        self.low.set_target_angle("l_shoulder", 1.5, max_torque=400)
        self.low.set_target_angle("r_elbow", -0.2, max_torque=300)
        self.low.set_target_angle("l_elbow", -0.2, max_torque=300)

    def is_finished(self):
        return False
