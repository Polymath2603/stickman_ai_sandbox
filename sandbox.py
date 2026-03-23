import pygame
import pymunk
from utils import config
import math

class Sandbox:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Stickman Pymunk Sandbox")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        self.grabbed_body = None
        
        # Pymunk Space
        self.space = pymunk.Space()
        self.space.gravity = config.GRAVITY
        
        # Ground (radius 0.02, offset -0.02 so top is at 0)
        self.ground = self.space.static_body
        ground_shape = pymunk.Segment(self.ground, (-100, -0.02), (100, -0.02), 0.02)
        ground_shape.friction = 1.0
        self.space.add(ground_shape)
        
        # Walls and Roof (Closed Box, adjusted for radius flushness)
        wall_height = 25.0
        r = 0.05
        self.left_wall = pymunk.Segment(self.ground, (-config.WALL_X - r, 0), (-config.WALL_X - r, wall_height), r)
        self.left_wall.friction = 0.5
        self.space.add(self.left_wall)
        
        self.right_wall = pymunk.Segment(self.ground, (config.WALL_X + r, 0), (config.WALL_X + r, wall_height), r)
        self.right_wall.friction = 0.5
        self.space.add(self.right_wall)
        
        self.roof = pymunk.Segment(self.ground, (-config.WALL_X, wall_height + r), (config.WALL_X, wall_height + r), r)
        self.roof.friction = 0.2
        self.space.add(self.roof)

        # Environment Objects
        # Stairs shifted to be flush with left wall at x = -config.WALL_X
        self._create_stairs_and_bar((-config.WALL_X, 0), steps=8)
        self._create_goal((config.WALL_X - 4, 0))

        # Soccer Ball
        mass = config.BALL_MASS
        radius = config.BALL_RADIUS
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        self.ball_body = pymunk.Body(mass, inertia)
        self.ball_body.position = (5, 1)
        self.ball_shape = pymunk.Circle(self.ball_body, radius)
        self.ball_shape.friction = 0.5
        self.ball_shape.elasticity = 0.7
        self.space.add(self.ball_body, self.ball_shape)

        # Mouse Interaction
        self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.mouse_joint = None

    def _create_stairs_and_bar(self, pos, steps=8):
        x_start, y_start = pos
        step_w, step_h = 1.0, 0.5
        
        # 1. Last Stair (Top one, 6.0m wide platform)
        top_h = step_h * steps
        top_w = 6.0 
        ox_top = x_start + top_w/2
        oy_top = y_start + top_h/2
        verts_top = [(-top_w/2 + ox_top, -top_h/2 + oy_top), (top_w/2 + ox_top, -top_h/2 + oy_top), 
                     (top_w/2 + ox_top, top_h/2 + oy_top), (-top_w/2 + ox_top, top_h/2 + oy_top)]
        top_shape = pymunk.Poly(self.space.static_body, verts_top)
        top_shape.friction = 0.8
        self.space.add(top_shape)
        
        # 2. Bar Fix (ON the last stair)
        bar_x = x_start + 3.0
        bar_y_rel = 4.5
        self._create_pullup_bar((bar_x, top_h + bar_y_rel), base_y=top_h)

        # 3. Other Stairs (Descending)
        remaining_x_start = x_start + top_w
        for i in range(1, steps):
            w = step_w
            h = step_h * (steps - i)
            ox = remaining_x_start + (i-1) * step_w + step_w/2
            oy = y_start + h/2
            verts = [(-w/2 + ox, -h/2 + oy), (w/2 + ox, -h/2 + oy), (w/2 + ox, h/2 + oy), (-w/2 + ox, h/2 + oy)]
            box_shape = pymunk.Poly(self.space.static_body, verts)
            box_shape.friction = 0.8
            self.space.add(box_shape)

    def _create_pullup_bar(self, pos, base_y=0):
        x, y = pos 
        width = 2.5
        r = 0.05
        ghost_filter = pymunk.ShapeFilter(mask=0)
        supp_l = pymunk.Segment(self.space.static_body, (x - width/2, base_y), (x - width/2, y), r)
        supp_r = pymunk.Segment(self.space.static_body, (x + width/2, base_y), (x + width/2, y), r)
        supp_l.filter = ghost_filter
        supp_r.filter = ghost_filter
        self.space.add(supp_l, supp_r)
        
        bar = pymunk.Segment(self.space.static_body, (x - width/2, y), (x + width/2, y), 0.1)
        bar.friction = 1.0
        self.space.add(bar)

    def _create_goal(self, pos):
        x, y = pos
        width, height = 4.0, 3.0
        back_post = pymunk.Segment(self.space.static_body, (x + width, 0), (x + width, height), 0.1)
        crossbar = pymunk.Segment(self.space.static_body, (x, height), (x + width, height), 0.1)
        back_post.friction = 0.5
        crossbar.friction = 0.5
        self.space.add(back_post, crossbar)

    def w2s(self, p):
        """World to Screen coordinates"""
        return int(p[0] * config.PPM + config.SCREEN_WIDTH / 2), int(config.SCREEN_HEIGHT - (p[1] * config.PPM) - 50)

    def s2w(self, p):
        """Screen to World coordinates"""
        return (p[0] - config.SCREEN_WIDTH / 2) / config.PPM, (config.SCREEN_HEIGHT - p[1] - 50) / config.PPM

    def handle_mouse_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        world_p = self.s2w(mouse_pos)
        self.mouse_body.position = world_p
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            info = self.space.point_query_nearest(world_p, 0, pymunk.ShapeFilter())
            if info and info.shape.body.body_type == pymunk.Body.DYNAMIC:
                self.grabbed_body = info.shape.body
                self.mouse_joint = pymunk.PivotJoint(self.mouse_body, self.grabbed_body, world_p)
                self.mouse_joint.max_force = 10000 * self.grabbed_body.mass
                self.mouse_joint.error_bias = pow(1.0 - 0.1, 60.0)
                self.space.add(self.mouse_joint)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mouse_joint:
                self.space.remove(self.mouse_joint)
                self.mouse_joint = None

    def reset_objects(self):
        self.ball_body.position = (5, 1)
        self.ball_body.velocity = (0, 0)
        self.ball_body.angular_velocity = 0

    def render(self):
        self.screen.fill((30, 30, 40))
        
        # Ground line exactly at y=0, visually correct now that segments are offset
        pygame.draw.line(self.screen, (100, 100, 100), self.w2s((-100, 0)), self.w2s((100, 0)), 5)
        
        # Draw all bodies
        for shape in self.space.shapes:
            is_ghost = shape.filter.mask == 0
            
            if isinstance(shape, pymunk.Circle):
                pos = self.w2s(shape.body.position)
                radius = int(shape.radius * config.PPM)
                color = (150, 150, 200) if shape.body.body_type == pymunk.Body.DYNAMIC else (200, 200, 200)
                pygame.draw.circle(self.screen, color, pos, radius)
                pygame.draw.circle(self.screen, (255, 255, 255), pos, radius, 1)
                angle = shape.body.angle
                end_pt = (pos[0] + math.cos(angle) * radius, pos[1] - math.sin(angle) * radius)
                pygame.draw.line(self.screen, (255, 255, 255), pos, end_pt, 1)
            elif isinstance(shape, pymunk.Poly):
                vertices = []
                for v in shape.get_vertices():
                    world_v = shape.body.local_to_world(v)
                    vertices.append(self.w2s(world_v))
                color = (150, 150, 200) if shape.body.body_type == pymunk.Body.DYNAMIC else (180, 180, 180)
                pygame.draw.polygon(self.screen, color, vertices)
                pygame.draw.polygon(self.screen, (255, 255, 255), vertices, 1)
            elif isinstance(shape, pymunk.Segment):
                p1 = self.w2s(shape.body.local_to_world(shape.a))
                p2 = self.w2s(shape.body.local_to_world(shape.b))
                color = (160, 160, 160) if is_ghost else (255, 255, 255)
                thickness = max(1, int(shape.radius * 2 * config.PPM))
                pygame.draw.line(self.screen, color, p1, p2, thickness)

        # Draw mouse joint line
        if self.mouse_joint:
            p1 = self.w2s(self.mouse_body.position)
            p2 = self.w2s(self.grabbed_body.local_to_world(self.mouse_joint.anchor_b))
            pygame.draw.line(self.screen, (0, 255, 0), p1, p2, 2)

    def step(self):
        dt = 1.0 / 60.0
        iterations = 10
        for _ in range(iterations):
            self.space.step(dt / iterations)
