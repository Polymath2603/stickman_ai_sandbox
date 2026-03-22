import math

class Push_rightAction:
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0

    def step(self):
        self.ticks += 1
        
        cycle = self.ticks * 0.05 # Even slower for pushing
        
        # Deep Lean Right (Negative ankle angle)
        self.low.set_target_angle("l_ankle", -0.4, max_torque=500, kp=12.0)
        self.low.set_target_angle("r_ankle", -0.4, max_torque=500, kp=12.0)
        
        # High power marching (high torque, low speed)
        # We need to overcome the table's weight
        hip_swing = math.sin(cycle) * 0.4
        self.low.set_target_angle("r_hip", hip_swing, max_torque=800, kp=15.0)
        self.low.set_target_angle("l_hip", -hip_swing, max_torque=800, kp=15.0)
        
        # Keep knees slightly bent but strong
        self.low.set_target_angle("r_knee", -0.3, max_torque=600)
        self.low.set_target_angle("l_knee", -0.3, max_torque=600)
        
        # Arms forward to push
        self.low.set_target_angle("r_shoulder", -1.5, max_torque=400)
        self.low.set_target_angle("l_shoulder", -1.5, max_torque=400)
        self.low.set_target_angle("r_elbow", 0.2, max_torque=300)
        self.low.set_target_angle("l_elbow", 0.2, max_torque=300)

    def is_finished(self):
        return False
