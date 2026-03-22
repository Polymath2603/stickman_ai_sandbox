import gymnasium as gym
from gymnasium import spaces
import numpy as np
import math
from physics.world import PhysicsWorld
from physics.body import Stickman
from utils import config

class StickmanEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()
        self.world = PhysicsWorld()
        self.stickman = Stickman(self.world)
        self.render_mode = render_mode
        
        # Actions: 8 joints (L/R Hip, Knee, Shoulder, Elbow)
        # We output target angles (localized to joints)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(8,), dtype=np.float32)
        
        # Observations: (torso_x, torso_y, torso_angle, torso_vx, torso_vy, torso_va, 
        #                8 joint angles, 8 joint velocities) = 22
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(22,), dtype=np.float32)
        
        self.max_steps = 1000
        self.current_step = 0
        self.initial_x = 600.0

    def _get_obs(self):
        torso = self.stickman.bodies["torso"]
        obs = [
            (torso.position.x - self.initial_x) / 100.0,
            (torso.position.y) / 100.0,
            torso.angle,
            torso.velocity.x / 100.0,
            torso.velocity.y / 100.0,
            torso.angular_velocity
        ]
        
        # Joint states
        for name in self.stickman.joints:
            if name == "neck": continue # ignore neck for RL for now
            joint, limits, motor, spring = self.stickman.joints[name]
            angle = joint.b.angle - joint.a.angle
            vel = joint.b.angular_velocity - joint.a.angular_velocity
            obs.append(angle)
            obs.append(vel / 10.0)
            
        return np.array(obs, dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.world = PhysicsWorld()
        self.stickman = Stickman(self.world)
        self.current_step = 0
        return self._get_obs(), {}

    def step(self, action):
        self.current_step += 1
        
        # Map actions to joint targets
        joint_names = ["left_hip", "left_knee", "right_hip", "right_knee", 
                       "left_shoulder", "left_elbow", "right_shoulder", "right_elbow"]
        
        for i, name in enumerate(joint_names):
            # Scale -1..1 to reasonable joint angles
            target = action[i] * 1.5 # rad range
            
            joint, limits, motor, spring = self.stickman.joints[name]
            current_angle = joint.b.angle - joint.a.angle
            error = target - current_angle
            motor.rate = np.clip(error * 20.0, -15, 15)
            spring.rest_angle = target

        # Step physics
        self.world.step(config.DT)
        
        obs = self._get_obs()
        
        # Reward calculation
        torso = self.stickman.bodies["torso"]
        vx = torso.velocity.x
        height = torso.position.y
        angle = torso.angle
        
        # Forward speed (direction +1)
        reward = vx / 50.0 
        
        # Survival reward
        reward += 0.1 
        
        # Penalty for falling
        terminated = False
        if height > config.SCREEN_HEIGHT - 100 or abs(angle) > 1.2:
            reward -= 10.0
            terminated = True
            
        if self.current_step >= self.max_steps:
            truncated = True
        else:
            truncated = False
            
        return obs, reward, terminated, truncated, {}

    def render(self):
        # We'll use the existing Renderer for this later
        pass
