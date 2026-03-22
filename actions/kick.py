import math

class KickAction:
    def __init__(self, stickman, low_level, leg="right"):
        self.stickman = stickman
        self.low = low_level
        self.ticks = 0
        self.leg = leg  # "left" or "right"
        self.phase = "windup"

    def step(self):
        self.ticks += 1

        if self.phase == "windup":
            self._windup()
            if self.ticks > 15:
                self.phase = "chamber"
                self.ticks = 0
        elif self.phase == "chamber":
            self._chamber()
            if self.ticks > 8:
                self.phase = "strike"
                self.ticks = 0
        elif self.phase == "strike":
            self._strike()
            if self.ticks > 6:
                self.phase = "follow_through"
                self.ticks = 0
        elif self.phase == "follow_through":
            self._follow_through()
            if self.ticks > 10:
                self.phase = "recovery"
                self.ticks = 0
        elif self.phase == "recovery":
            self._recovery()

    def _windup(self):
        """Phase 1: Wind up - lift kicking leg back, shift weight to standing leg"""
        if self.leg == "right":
            # Lift right leg back
            self.low.set_target_angle("r_hip", 0.8, max_torque=600, kp=12.0, max_speed=8.0)
            self.low.set_target_angle("r_knee", -1.8, max_torque=500, kp=10.0, max_speed=6.0)

            # Balance on left leg - shift weight
            self.low.set_target_angle("l_hip", -0.3, max_torque=500, kp=8.0)
            self.low.set_target_angle("l_knee", -0.4, max_torque=400, kp=8.0)
            self.low.set_target_angle("l_ankle", -0.2, max_torque=300, kp=6.0)

            # Lean torso slightly back for balance
            # Arms help with balance
            self.low.set_target_angle("r_shoulder", 0.5, max_torque=200)
            self.low.set_target_angle("l_shoulder", -0.3, max_torque=200)

        else:  # left leg kick
            # Lift left leg back
            self.low.set_target_angle("l_hip", -0.8, max_torque=600, kp=12.0, max_speed=8.0)
            self.low.set_target_angle("l_knee", -1.8, max_torque=500, kp=10.0, max_speed=6.0)

            # Balance on right leg
            self.low.set_target_angle("r_hip", 0.3, max_torque=500, kp=8.0)
            self.low.set_target_angle("r_knee", -0.4, max_torque=400, kp=8.0)
            self.low.set_target_angle("r_ankle", 0.2, max_torque=300, kp=6.0)

            # Arms help with balance
            self.low.set_target_angle("l_shoulder", -0.5, max_torque=200)
            self.low.set_target_angle("r_shoulder", 0.3, max_torque=200)

    def _chamber(self):
        """Phase 2: Chamber - bring leg to kicking position"""
        if self.leg == "right":
            # Bring right leg to chamber position
            self.low.set_target_angle("r_hip", 0.2, max_torque=700, kp=15.0, max_speed=10.0)
            self.low.set_target_angle("r_knee", -0.8, max_torque=600, kp=12.0, max_speed=8.0)

            # Maintain balance
            self.low.set_target_angle("l_hip", -0.4, max_torque=500, kp=8.0)
            self.low.set_target_angle("l_knee", -0.5, max_torque=400, kp=8.0)

        else:  # left leg
            self.low.set_target_angle("l_hip", -0.2, max_torque=700, kp=15.0, max_speed=10.0)
            self.low.set_target_angle("l_knee", -0.8, max_torque=600, kp=12.0, max_speed=8.0)

            # Maintain balance
            self.low.set_target_angle("r_hip", 0.4, max_torque=500, kp=8.0)
            self.low.set_target_angle("r_knee", -0.5, max_torque=400, kp=8.0)

    def _strike(self):
        """Phase 3: Strike - explosive extension forward"""
        if self.leg == "right":
            # Powerful forward kick
            self.low.set_target_angle("r_hip", -1.5, max_torque=1500, kp=25.0, max_speed=25.0)
            self.low.set_target_angle("r_knee", 0.1, max_torque=1200, kp=20.0, max_speed=20.0)

            # Counter-balance with standing leg and torso
            self.low.set_target_angle("l_hip", -0.6, max_torque=600, kp=10.0)
            self.low.set_target_angle("l_knee", -0.7, max_torque=500, kp=8.0)
            self.low.set_target_angle("l_ankle", -0.3, max_torque=400, kp=8.0)

        else:  # left leg
            self.low.set_target_angle("l_hip", 1.5, max_torque=1500, kp=25.0, max_speed=25.0)
            self.low.set_target_angle("l_knee", 0.1, max_torque=1200, kp=20.0, max_speed=20.0)

            # Counter-balance
            self.low.set_target_angle("r_hip", 0.6, max_torque=600, kp=10.0)
            self.low.set_target_angle("r_knee", -0.7, max_torque=500, kp=8.0)
            self.low.set_target_angle("r_ankle", 0.3, max_torque=400, kp=8.0)

    def _follow_through(self):
        """Phase 4: Follow through - continue the motion"""
        if self.leg == "right":
            # Continue the kick motion
            self.low.set_target_angle("r_hip", -1.8, max_torque=1000, kp=15.0, max_speed=15.0)
            self.low.set_target_angle("r_knee", 0.3, max_torque=800, kp=12.0, max_speed=12.0)

            # Maintain counter-balance
            self.low.set_target_angle("l_hip", -0.5, max_torque=500, kp=8.0)
            self.low.set_target_angle("l_knee", -0.6, max_torque=400, kp=8.0)

        else:  # left leg
            self.low.set_target_angle("l_hip", 1.8, max_torque=1000, kp=15.0, max_speed=15.0)
            self.low.set_target_angle("l_knee", 0.3, max_torque=800, kp=12.0, max_speed=12.0)

            # Maintain counter-balance
            self.low.set_target_angle("r_hip", 0.5, max_torque=500, kp=8.0)
            self.low.set_target_angle("r_knee", -0.6, max_torque=400, kp=8.0)

    def _recovery(self):
        """Phase 5: Recovery - return to standing position"""
        # Relax all joints to return to natural standing
        self.low.relax_all()

    def is_finished(self):
        return self.ticks > 60  # Total duration ~60 ticks