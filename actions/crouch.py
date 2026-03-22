class CrouchAction:
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level

    def step(self):
        # Hold squat
        self.low.set_target_angle("l_hip", 1.2, max_torque=800)
        self.low.set_target_angle("r_hip", 1.2, max_torque=800)
        self.low.set_target_angle("l_knee", -2.4, max_torque=800)
        self.low.set_target_angle("r_knee", -2.4, max_torque=800)
        self.low.set_target_angle("l_ankle", 1.2, max_torque=400)
        self.low.set_target_angle("r_ankle", 1.2, max_torque=400)
        
        # Lean forward to balance
        self.low.set_target_angle("l_shoulder", 0.5)
        self.low.set_target_angle("r_shoulder", 0.5)

    def is_finished(self):
        return False
