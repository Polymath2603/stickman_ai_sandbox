import math

# Window Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
DT = 1.0 / FPS

# Box2D Settings
PPM = 30.0 # Pixels per meter
TARGET_FPS = FPS
TIME_STEP = DT
VEL_ITERS = 40
POS_ITERS = 20

GRAVITY = (0.0, -10.0) # Real world gravity (y is up in box2d)

# Stickman Geometry (meters)
HEAD_RADIUS = 0.4
HEAD_MASS = 1.0

TORSO_WIDTH = 0.4
TORSO_HEIGHT = 1.2
TORSO_MASS = 8.0

ARM_UPPER_LENGTH = 0.8
ARM_LOWER_LENGTH = 0.7
ARM_UPPER_MASS = 2.0
ARM_LOWER_MASS = 1.0

LEG_UPPER_LENGTH = 1.0
LEG_LOWER_LENGTH = 1.0
LEG_UPPER_MASS = 4.0
LEG_LOWER_MASS = 2.0

# Joint Limits (in radians)
NECK_LIMITS = (-0.5, 0.5) 
SHOULDER_LIMITS = (-math.pi, math.pi)
ELBOW_LIMITS = (0, math.pi) # Elbow bends forward/inward
HIP_LIMITS = (-1.5, 1.5)
KNEE_LIMITS = (-math.pi, 0) # Knee bends backwards

# World Objects
WALL_X = 20.0 # Distance from center
BALL_RADIUS = 0.3
BALL_MASS = 0.5
TABLE_WIDTH = 2.0
TABLE_HEIGHT = 1.0
TABLE_MASS = 15.0

# AI Constants
OLLAMA_MODEL = "qwen2.5:0.5b-instruct"
OLLAMA_URL = "http://127.0.0.1:11434"
