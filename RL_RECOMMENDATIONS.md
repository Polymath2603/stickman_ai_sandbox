# Reinforcement Learning Recommendations

To develop a high-level AI that learns individual skills and selects them to achieve goals, we recommend the following approach:

## 1. Core Framework
- **Primary Recommendation**: [Stable Baselines3 (SB3)](https://stable-baselines3.readthedocs.io/)
- **Reasoning**: SB3 is highly modular, well-documented, and works seamlessly with Gym/Gymnasium environments. It uses PyTorch and is perfect for building continuous control policies for robotics-like simulations.

## 2. Skill-Level RL Algorithms
These algorithms are best for learning "Low-Level Skills" like standing, walking, and jumping.

### [PPO] Proximal Policy Optimization
- **Best for**: Stability and reliability. PPO is the "standard" starting point for most RL tasks.
- **Why**: It handles continuous action spaces (joint velocities/torques) very well and is less sensitive to hyperparameter tuning than other algorithms.

### [SAC] Soft Actor-Critic
- **Best for**: Sample efficiency and energy-efficient movement.
- **Why**: SAC is an off-policy algorithm that tends to learn much faster than PPO. It naturally explores the environment and often results in more "fluid" or "human-like" motion because it maximizes entropy (exploration).

## 3. Brain AI (High-Level Controller)
To select actions to achieve goals, use a **Hierarchical Architecture**.

### [HRL] Hierarchical Reinforcement Learning
- **Concept**: A "Manager" AI that observes the high-level goal (e.g., "Go to the soccer ball") and selects which learned skill (e.g., "Walk") to execute.
- **Implementation**:
    - **Options Framework**: Treat each learned skill (Walk, Jump) as a temporal abstraction. The high-level agent picks an option, executes it until completion, then picks the next.
    - **Goal-Conditioned Policies**: Train the skills to be goal-aware. Instead of just "Walking", train the agent to "Walk to Target Vector".

## 4. Storage & Organization
- **Skills Directory**: Store the trained model weights (e.g., `.zip` or `.pth` files) in `skills/`.
- **Refactoring**: Each file in `skills/` (like `walk.py`) should represent an interface that loads the corresponding trained model and executes its policy.

## Next Steps
1.  **Refine the Gym Environment**: Ensure `gym_env/` correctly wraps the Pymunk sandbox.
2.  **Define Rewards**:
    - **Standing**: Reward for keeping the head high and torso upright.
    - **Walking**: Reward for forward displacement (x-velocity).
    - **Jumping**: Reward for maximum y-height reached.
3.  **Train Skills**: Use SB3 to train individual PPO/SAC models for each skill.
