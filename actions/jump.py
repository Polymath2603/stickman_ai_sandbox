class JumpAction:
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0

    def step(self):
        self.ticks += 1
        
        if self.ticks < 20:
            # Phase 1: Deep Squat
            self.low.set_target_angle("l_hip", 1.2, max_torque=800, max_speed=5.0)
            self.low.set_target_angle("r_hip", 1.2, max_torque=800, max_speed=5.0)
            self.low.set_target_angle("l_knee", -2.4, max_torque=800, max_speed=5.0)
            self.low.set_target_angle("r_knee", -2.4, max_torque=800, max_speed=5.0)
            self.low.set_target_angle("l_ankle", 1.0, max_torque=400, max_speed=5.0)
            self.low.set_target_angle("r_ankle", 1.0, max_torque=400, max_speed=5.0)
            
            # Arms back for momentum
            self.low.set_target_angle("l_shoulder", 1.5, max_torque=200)
            self.low.set_target_angle("r_shoulder", 1.5, max_torque=200)
        elif self.ticks < 32:
            # Phase 2: Explosive Extension (The "Spring")
            # We use high torque and high speed to push off the floor
            self.low.set_target_angle("l_hip", -0.3, max_torque=1000, max_speed=20.0, kp=30.0)
            self.low.set_target_angle("r_hip", -0.3, max_torque=1000, max_speed=20.0, kp=30.0)
            self.low.set_target_angle("l_knee", 0.0, max_torque=1000, max_speed=20.0, kp=30.0)
            self.low.set_target_angle("r_knee", 0.0, max_torque=1000, max_speed=20.0, kp=30.0)
            
            # Ankle flick (pointing toes down to push off)
            self.low.set_target_angle("l_ankle", -0.5, max_torque=600, max_speed=20.0)
            self.low.set_target_angle("r_ankle", -0.5, max_torque=600, max_speed=20.0)
            
            # Arms swing up explosively
            self.low.set_target_angle("l_shoulder", -2.5, max_torque=500, max_speed=20.0)
            self.low.set_target_angle("r_shoulder", -2.5, max_torque=500, max_speed=20.0)
        elif self.ticks < 60:
            # Phase 3: Tuck in air
            self.low.set_target_angle("l_knee", -1.5, max_torque=200)
            self.low.set_target_angle("r_knee", -1.5, max_torque=200)
            self.low.set_target_angle("l_hip", 1.0, max_torque=200)
            self.low.set_target_angle("r_hip", 1.0, max_torque=200)
        else:
            # Fall naturally
            self.low.relax_all()

    def is_finished(self):
        return self.ticks > 60
