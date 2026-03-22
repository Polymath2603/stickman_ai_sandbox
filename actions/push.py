import math

class PushAction:
    def __init__(self, stickman, low_level, direction="right"):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0
        self.direction = direction  # "left" or "right"
        self.turning = True
        self.turn_ticks = 0

    def step(self):
        self.ticks += 1

        if self.turning:
            # Phase 1: Turn to face the direction
            self._turn_to_direction()
            if self.turn_ticks > 20:  # Turn for ~20 ticks
                self.turning = False
                self.ticks = 0  # Reset for pushing
        else:
            # Phase 2: Push in the facing direction
            self._push_forward()

    def _turn_to_direction(self):
        self.turn_ticks += 1

        # Turn the torso to face the direction
        turn_angle = 0.5 if self.direction == "right" else -0.5

        # Use hip angles to turn the body
        self.low.set_target_angle("r_hip", turn_angle * 0.3, max_torque=400, kp=8.0)
        self.low.set_target_angle("l_hip", -turn_angle * 0.3, max_torque=400, kp=8.0)

        # Keep knees slightly bent for stability
        self.low.set_target_angle("r_knee", -0.2, max_torque=200)
        self.low.set_target_angle("l_knee", -0.2, max_torque=200)

    def _push_forward(self):
        cycle = self.ticks * 0.05 # Even slower for pushing

        # Lean forward for pushing force
        self.low.set_target_angle("l_ankle", -0.3, max_torque=500, kp=12.0)
        self.low.set_target_angle("r_ankle", -0.3, max_torque=500, kp=12.0)

        # High power marching (high torque, low speed)
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