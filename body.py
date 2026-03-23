import pymunk
import math
from utils import config

class Body:
    def __init__(self, space, position=(0, 2)):
        self.space = space
        self.bodies = {}
        self.shapes = {}
        self.joints = {}
        self.motors = {}
        self.create_ragdoll(position)

    def _create_limb(self, name, position, width, length, mass):
        inertia = pymunk.moment_for_box(mass, (width, length))
        body = pymunk.Body(mass, inertia)
        body.position = position
        shape = pymunk.Poly.create_box(body, (width, length))
        shape.friction = 0.5
        shape.filter = pymunk.ShapeFilter(group=1) # Prevent internal collisions
        self.space.add(body, shape)
        self.bodies[name] = body
        self.shapes[name] = shape
        return body, shape

    def _create_joint(self, name, bodyA, bodyB, anchorA, anchorB, limits):
        # Pivot joint for positioning (using local anchors)
        joint = pymunk.PivotJoint(bodyA, bodyB, anchorA, anchorB)
        self.space.add(joint)
        self.joints[name] = joint
        
        # Rotary limit joint for constraints
        limit = pymunk.RotaryLimitJoint(bodyA, bodyB, limits[0], limits[1])
        self.space.add(limit)
        
        # Simple motor for active control (muscle tone)
        motor = pymunk.SimpleMotor(bodyA, bodyB, 0)
        motor.max_force = 500.0 # Small default force to keep it from being too floppy
        self.space.add(motor)
        self.motors[name] = motor
        
        return joint

    def create_ragdoll(self, start_pos=(0, 2)):
        x, y = start_pos
        
        # --- Create Bodies ---
        # Torso
        torso_y = y + config.LEG_UPPER_LENGTH + config.LEG_LOWER_LENGTH + config.TORSO_HEIGHT/2
        torso, _ = self._create_limb("torso", (x, torso_y), config.TORSO_WIDTH, config.TORSO_HEIGHT, config.TORSO_MASS)
        
        # Head
        head_radius = config.HEAD_RADIUS
        head_mass = config.HEAD_MASS
        head_inertia = pymunk.moment_for_circle(head_mass, 0, head_radius)
        head_body = pymunk.Body(head_mass, head_inertia)
        head_body.position = (x, torso_y + config.TORSO_HEIGHT/2 + head_radius)
        head_shape = pymunk.Circle(head_body, head_radius)
        head_shape.friction = 0.5
        head_shape.filter = pymunk.ShapeFilter(group=1)
        self.space.add(head_body, head_shape)
        self.bodies["head"] = head_body
        self.shapes["head"] = head_shape

        # Arms
        arm_y = torso_y + config.TORSO_HEIGHT/2 - 0.2
        for side, dx in [("l", -0.15), ("r", 0.15)]:
            # Upper arm
            u_arm_y = arm_y - config.ARM_UPPER_LENGTH/2
            u_arm, _ = self._create_limb(f"{side}_u_arm", (x + dx, u_arm_y), 0.2, config.ARM_UPPER_LENGTH, config.ARM_UPPER_MASS)
            # Lower arm
            l_arm_y = u_arm_y - config.ARM_UPPER_LENGTH/2 - config.ARM_LOWER_LENGTH/2
            l_arm, _ = self._create_limb(f"{side}_l_arm", (x + dx, l_arm_y), 0.2, config.ARM_LOWER_LENGTH, config.ARM_LOWER_MASS)
            
            # Joints
            self._create_joint(f"{side}_shoulder", torso, u_arm, (dx, config.TORSO_HEIGHT/2 - 0.2), (0, config.ARM_UPPER_LENGTH/2), config.SHOULDER_LIMITS)
            self._create_joint(f"{side}_elbow", u_arm, l_arm, (0, -config.ARM_UPPER_LENGTH/2), (0, config.ARM_LOWER_LENGTH/2), config.ELBOW_LIMITS)

        # Legs
        leg_y = torso_y - config.TORSO_HEIGHT/2
        for side, dx in [("l", -0.15), ("r", 0.15)]:
            # Upper leg
            u_leg_y = leg_y - config.LEG_UPPER_LENGTH/2
            u_leg, _ = self._create_limb(f"{side}_u_leg", (x + dx, u_leg_y), 0.25, config.LEG_UPPER_LENGTH, config.LEG_UPPER_MASS)
            # Lower leg
            l_leg_y = u_leg_y - config.LEG_UPPER_LENGTH/2 - config.LEG_LOWER_LENGTH/2
            l_leg, _ = self._create_limb(f"{side}_l_leg", (x + dx, l_leg_y), 0.25, config.LEG_LOWER_LENGTH, config.LEG_LOWER_MASS)
            
            # Foot
            foot_y = l_leg_y - config.LEG_LOWER_LENGTH/2 - 0.1
            foot, _ = self._create_limb(f"{side}_foot", (x + dx + 0.1, foot_y), 0.4, 0.2, config.FOOT_MASS)

            # Joints
            self._create_joint(f"{side}_hip", torso, u_leg, (dx, -config.TORSO_HEIGHT/2), (0, config.LEG_UPPER_LENGTH/2), config.HIP_LIMITS)
            self._create_joint(f"{side}_knee", u_leg, l_leg, (0, -config.LEG_UPPER_LENGTH/2), (0, config.LEG_LOWER_LENGTH/2), config.KNEE_LIMITS)
            self._create_joint(f"{side}_ankle", l_leg, foot, (0, -config.LEG_LOWER_LENGTH/2), (-0.1, 0.1), (-0.5, 0.5))

        # Neck
        self._create_joint("neck", torso, head_body, (0, config.TORSO_HEIGHT/2), (0, -head_radius), config.NECK_LIMITS)
