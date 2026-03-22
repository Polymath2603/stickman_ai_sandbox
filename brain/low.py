from utils import config
import math

class LowLevelController:
    """
    brain/low.py
    Low-level control over the body. Applies movements as torques in joints.
    Valid joint names line up with body.py (e.g. 'l_hip', 'r_knee', 'neck').
    """
    def __init__(self, stickman):
        self.stickman = stickman

    def set_target_angle(self, joint_name, target_angle, max_torque=1000.0, kp=15.0, max_speed=5.0):
        """
        Uses Box2D's native motor to reach a target angle.
        motorSpeed acts as the corrective velocity, maxMotorTorque limits the strength.
        max_speed prevents explosive joint realignments when returning from extreme poses.
        """
        if joint_name not in self.stickman.joints:
            return

        joint = self.stickman.joints[joint_name]
        current_angle = joint.angle
        
        # Speed should be proportional to error, not a raw torque value
        error = target_angle - current_angle
        desired_speed = kp * error
        
        # Cap the speed so it doesn't violently kick the ground
        desired_speed = max(-max_speed, min(max_speed, desired_speed))
        
        joint.maxMotorTorque = max_torque
        joint.motorSpeed = desired_speed
        
    def relax(self, joint_name):
        """Releases a joint so it falls loosely to gravity."""
        if joint_name in self.stickman.joints:
            joint = self.stickman.joints[joint_name]
            joint.maxMotorTorque = 0.0
            joint.motorSpeed = 0.0

    def relax_all(self):
        for name in self.stickman.joints:
            self.relax(name)
