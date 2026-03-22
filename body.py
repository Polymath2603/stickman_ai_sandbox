import Box2D
from Box2D.b2 import polygonShape, circleShape, revoluteJoint
from utils import config
import math

class Body:
    def __init__(self, world, position):
        self.world = world
        self.bodies = {}
        self.joints = {}
        self.create_ragdoll(position)

    def _create_limb(self, name, position, width, length, mass, category_bits=0x0001, mask_bits=0xFFFE): # Collide with everything except other limbs (0x0002)
        # Avoid internal collision by setting groupIndex to a negative value or masking
        fixture_def = Box2D.b2FixtureDef(
            shape=polygonShape(box=(width/2, length/2)),
            density=mass / (width * length),
            friction=0.5,
            restitution=0.1,
            filter=Box2D.b2Filter(groupIndex=-1) # Prevent ragdoll parts from colliding with each other
        )
        body = self.world.CreateDynamicBody(position=position)
        body.CreateFixture(fixture_def)
        self.bodies[name] = body
        return body

    def _create_joint(self, name, bodyA, bodyB, localAnchorA, localAnchorB, limits):
        joint = self.world.CreateRevoluteJoint(
            bodyA=bodyA,
            bodyB=bodyB,
            localAnchorA=localAnchorA,
            localAnchorB=localAnchorB,
            enableLimit=True,
            lowerAngle=limits[0],
            upperAngle=limits[1],
            enableMotor=True,
            maxMotorTorque=0.0, # Will be driven by brain
            motorSpeed=0.0
        )
        self.joints[name] = joint
        return joint

    def create_ragdoll(self, start_pos=(0, 2)):
        x, y = start_pos
        
        # --- Create Bodies ---
        # Torso
        torso = self._create_limb("torso", (x, y + config.TORSO_HEIGHT/2 + config.LEG_UPPER_LENGTH + config.LEG_LOWER_LENGTH), 
                                  config.TORSO_WIDTH, config.TORSO_HEIGHT, config.TORSO_MASS)
        
        # Head (Circle)
        head_body = self.world.CreateDynamicBody(position=(x, torso.position.y + config.TORSO_HEIGHT/2 + config.HEAD_RADIUS))
        head_body.CreateFixture(shape=circleShape(radius=config.HEAD_RADIUS), density=config.HEAD_MASS/(math.pi * config.HEAD_RADIUS**2), filter=Box2D.b2Filter(groupIndex=-1))
        self.bodies["head"] = head_body

        # Arms
        arm_y = torso.position.y + config.TORSO_HEIGHT/2 - 0.2
        for side, dx in [("l", -0.1), ("r", 0.1)]:
            # Upper arm
            u_arm = self._create_limb(f"{side}_u_arm", (x + dx, arm_y - config.ARM_UPPER_LENGTH/2), 
                                      0.2, config.ARM_UPPER_LENGTH, config.ARM_UPPER_MASS)
            # Lower arm
            l_arm = self._create_limb(f"{side}_l_arm", (x + dx, u_arm.position.y - config.ARM_UPPER_LENGTH/2 - config.ARM_LOWER_LENGTH/2), 
                                      0.2, config.ARM_LOWER_LENGTH, config.ARM_LOWER_MASS)
            
            # Joints
            self._create_joint(f"{side}_shoulder", torso, u_arm, 
                               (dx, config.TORSO_HEIGHT/2 - 0.2), (0, config.ARM_UPPER_LENGTH/2), config.SHOULDER_LIMITS)
            self._create_joint(f"{side}_elbow", u_arm, l_arm, 
                               (0, -config.ARM_UPPER_LENGTH/2), (0, config.ARM_LOWER_LENGTH/2), config.ELBOW_LIMITS)

        # Legs
        leg_y = torso.position.y - config.TORSO_HEIGHT/2
        for side, dx in [("l", -0.1), ("r", 0.1)]:
            # Upper leg
            u_leg = self._create_limb(f"{side}_u_leg", (x + dx, leg_y - config.LEG_UPPER_LENGTH/2), 
                                      0.25, config.LEG_UPPER_LENGTH, config.LEG_UPPER_MASS)
            # Lower leg
            l_leg = self._create_limb(f"{side}_l_leg", (x + dx, u_leg.position.y - config.LEG_UPPER_LENGTH/2 - config.LEG_LOWER_LENGTH/2), 
                                      0.25, config.LEG_LOWER_LENGTH, config.LEG_LOWER_MASS)
            
            # Foot
            foot = self._create_limb(f"{side}_foot", (x + dx + 0.1, l_leg.position.y - config.LEG_LOWER_LENGTH/2 - 0.1), 
                                     0.4, 0.2, 1.0) # Normal foot

            # Ensure high friction on feet
            foot.fixtures[0].friction = 1.0

            # Joints
            self._create_joint(f"{side}_hip", torso, u_leg, 
                               (dx, -config.TORSO_HEIGHT/2), (0, config.LEG_UPPER_LENGTH/2), config.HIP_LIMITS)
            self._create_joint(f"{side}_knee", u_leg, l_leg, 
                               (0, -config.LEG_UPPER_LENGTH/2), (0, config.LEG_LOWER_LENGTH/2), config.KNEE_LIMITS)
            self._create_joint(f"{side}_ankle", l_leg, foot, 
                               (0, -config.LEG_LOWER_LENGTH/2), (-0.1, 0.1), (-0.5, 0.5))

        # Neck
        self._create_joint("neck", torso, head_body, (0, config.TORSO_HEIGHT/2), (0, -config.HEAD_RADIUS), config.NECK_LIMITS)
