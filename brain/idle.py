from brain.low import LowLevelController
from utils import config
import math

class IdleController:
    """
    brain/idle.py
    Parallel balance controller. Tries to maintain upright posture continuously.
    Works cooperatively with high.py (doesn't overwrite active joints arbitrarily, or combines softly).
    """
    def __init__(self, stickman, low_level):
        self.stickman = stickman
        self.low = low_level
        self.is_active = True

    def toggle(self):
        self.is_active = not self.is_active
        if not self.is_active:
            self.low.relax_all()

    def update(self, is_action_active=False, is_mouse_active=False):
        if not self.is_active:
            return
            
        if is_mouse_active:
            # Yield completely to the mouse constraint to prevent solver jitter
            self.low.relax_all()
            return
            
        torso = self.stickman.bodies["torso"]
        # Basic upright standing PID
        target_angle = 0.0
        # Calculate Center of Mass (CoM) vs Support Base (approx mid-ankles)
        l_foot = self.stickman.bodies["l_foot"].position.x
        r_foot = self.stickman.bodies["r_foot"].position.x
        support_center = (l_foot + r_foot) / 2.0
        
        com_x = torso.position.x
        error_x = com_x - support_center
        
        # 1. Apply 'invisible' core stability torque to Torso to keep it upright
        # Softened P to prevent Box2D high-frequency solver "shocking", but massively increased D to prevent "punching balloon" swaying
        if is_action_active:
            # Yield significantly to allow walking/jumping dynamics
            kp_gyro = 500.0
            kd_gyro = 50.0
        else:
            # Firm posture for idle standing
            kp_gyro = 2000.0
            kd_gyro = 300.0
            
        upright_error = 0.0 - torso.angle
        torso.ApplyTorque(upright_error * kp_gyro - torso.angularVelocity * kd_gyro, True)

        # 2. Use the CoM error to calculate a desired ankle lean to keep feet under CoM
        # Add a deeper deadzone to fully stabilize once upright
        if abs(error_x) < 0.1:
            error_x = 0.0
        
        target_angle = max(-0.2, min(0.2, error_x * 0.15)) 
        
        # 3. Soften the leg joints significantly to allow natural yielding to gravity/mouse
        # Add max_speed=2.0 so when an action ends, the legs slowly transition back to idle instead of violently snapping
        # Ankles
        self.low.set_target_angle("l_ankle", target_angle, max_torque=200.0, kp=8.0, max_speed=2.0)
        self.low.set_target_angle("r_ankle", target_angle, max_torque=200.0, kp=8.0, max_speed=2.0)
        
        # Knees
        self.low.set_target_angle("l_knee", 0.0, max_torque=300.0, kp=10.0, max_speed=2.0)
        self.low.set_target_angle("r_knee", 0.0, max_torque=300.0, kp=10.0, max_speed=2.0)
        
        # Hips (Counter-tilt slightly if legs lean)
        self.low.set_target_angle("l_hip", -target_angle * 0.5, max_torque=300.0, kp=10.0, max_speed=2.0)
        self.low.set_target_angle("r_hip", -target_angle * 0.5, max_torque=300.0, kp=10.0, max_speed=2.0)
        
        # Relaxed arms balance
        self.low.set_target_angle("l_shoulder", 0.1, max_torque=100.0, kp=8.0, max_speed=2.0)
        self.low.set_target_angle("r_shoulder", -0.1, max_torque=100.0, kp=8.0, max_speed=2.0)
        self.low.set_target_angle("l_elbow", 0.1, max_torque=80.0, kp=8.0, max_speed=2.0)
        self.low.set_target_angle("r_elbow", -0.1, max_torque=80.0, kp=8.0, max_speed=2.0)
        
        self.low.set_target_angle("neck", 0.0, max_torque=100.0, kp=10.0)
