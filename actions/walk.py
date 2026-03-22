import math

class WalkAction:
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
                self.ticks = 0  # Reset for walking
        else:
            # Phase 2: Walk in the facing direction
            self._walk_forward()

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

    def _walk_forward(self):
        # Walking speed (slower, more stable)
        cycle = self.ticks * 0.07

        # Lean forward slightly for walking momentum
        self.low.set_target_angle("l_ankle", -0.1, max_torque=150, kp=8.0, max_speed=3.0)
        self.low.set_target_angle("r_ankle", -0.1, max_torque=150, kp=8.0, max_speed=3.0)

        # Hips swing opposite each other smoothly
        r_hip_angle = math.sin(cycle) * 0.6
        l_hip_angle = math.sin(cycle + math.pi) * 0.6

        # Knee bends when hip is swinging forward
        r_knee_angle = -0.6 - math.cos(cycle) * 0.6
        l_knee_angle = -0.6 - math.cos(cycle + math.pi) * 0.6

        # Apply walking motion
        self.low.set_target_angle("r_hip", r_hip_angle, max_torque=300, kp=10.0, max_speed=4.0)
        self.low.set_target_angle("l_hip", l_hip_angle, max_torque=300, kp=10.0, max_speed=4.0)

        self.low.set_target_angle("r_knee", r_knee_angle, max_torque=150, kp=8.0, max_speed=4.0)
        self.low.set_target_angle("l_knee", l_knee_angle, max_torque=150, kp=8.0, max_speed=4.0)

        # Arms swing naturally opposite to legs
        self.low.set_target_angle("r_shoulder", math.sin(cycle + math.pi) * 0.5, max_torque=100, max_speed=3.0)
        self.low.set_target_angle("l_shoulder", math.sin(cycle) * 0.5, max_torque=100, max_speed=3.0)

    def is_finished(self):
        return False