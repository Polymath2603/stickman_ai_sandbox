from utils import config
import math

class LowLevelController:
    """
    brain/low.py
    Low-level control over the body. Applies movements as relative angular velocities in joints.
    Utilizes Pymunk's SimpleMotor for active control.
    """
    def __init__(self, stickman):
        self.stickman = stickman

    def set_target_angle(self, joint_name, target_angle, max_torque=10000.0, kp=10.0, max_speed=10.0):
        """
        Uses Pymunk's SimpleMotor to reach a target angle via PD control.
        """
        if joint_name not in self.stickman.motors:
            return

        motor = self.stickman.motors[joint_name]
        body_a = motor.a
        body_b = motor.b
        
        # Current relative angle
        current_angle = body_b.angle - body_a.angle
        
        # PD Control for motor rate (angular velocity)
        error = target_angle - current_angle
        desired_rate = kp * error
        
        # Cap the rate
        desired_rate = max(-max_speed, min(max_speed, desired_rate))
        
        motor.max_force = max_torque
        motor.rate = desired_rate
        
    def relax(self, joint_name):
        """Releases a joint so it falls loosely to gravity."""
        if joint_name in self.stickman.motors:
            motor = self.stickman.motors[joint_name]
            motor.max_force = 0.0
            motor.rate = 0.0

    def relax_all(self):
        for name in self.stickman.motors:
            self.relax(name)
