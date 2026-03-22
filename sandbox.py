import pygame
import Box2D
from Box2D.b2 import world, polygonShape, circleShape, edgeShape, mouseJoint
from utils import config
import math

class Sandbox:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Stickman Box2D Sandbox")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        # Box2D world
        self.world = world(gravity=config.GRAVITY, doSleep=True)
        
        # Ground
        ground_fixture = Box2D.b2FixtureDef(shape=edgeShape(vertices=[(-100, 0), (100, 0)]), friction=1.0)
        self.ground = self.world.CreateStaticBody(position=(0, 0))
        self.ground.CreateFixture(ground_fixture)
        
        # Walls
        wall_shape = edgeShape(vertices=[(0, 0), (0, 20)])
        self.left_wall = self.world.CreateStaticBody(position=(-config.WALL_X, 0))
        self.left_wall.CreateFixture(shape=wall_shape, friction=0.5)
        self.right_wall = self.world.CreateStaticBody(position=(config.WALL_X, 0))
        self.right_wall.CreateFixture(shape=wall_shape, friction=0.5)

        # Soccer Ball
        self.ball = self.world.CreateDynamicBody(position=(5, 1))
        self.ball.CreateFixture(shape=circleShape(radius=config.BALL_RADIUS), 
                                density=config.BALL_MASS/(math.pi * config.BALL_RADIUS**2), 
                                friction=0.5, restitution=0.7)

        # Table (a simple heavy box for now, maybe with legs later)
        self.table = self.world.CreateDynamicBody(position=(-5, config.TABLE_HEIGHT/2))
        self.table.CreateFixture(shape=polygonShape(box=(config.TABLE_WIDTH/2, config.TABLE_HEIGHT/2)), 
                                 density=config.TABLE_MASS/(config.TABLE_WIDTH * config.TABLE_HEIGHT), 
                                 friction=0.8)

        # Mouse Interaction State
        self.mouse_joint = None
        self.mouse_body = self.world.CreateStaticBody(position=(0,0))
        self.grabbed_body = None

    def w2s(self, p):
        """World to Screen coordinates"""
        return int(p[0] * config.PPM + config.SCREEN_WIDTH / 2), int(config.SCREEN_HEIGHT - (p[1] * config.PPM) - 50)

    def s2w(self, p):
        """Screen to World coordinates"""
        return (p[0] - config.SCREEN_WIDTH / 2) / config.PPM, (config.SCREEN_HEIGHT - p[1] - 50) / config.PPM

    def handle_mouse_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        world_p = self.s2w(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Query for bodies at world_p
            aabb = Box2D.b2AABB(lowerBound=(world_p[0]-0.001, world_p[1]-0.001), 
                                upperBound=(world_p[0]+0.001, world_p[1]+0.001))
            
            class QueryCallback(Box2D.b2QueryCallback):
                def __init__(self, p):
                    super(QueryCallback, self).__init__()
                    self.point = p
                    self.fixture = None
                def ReportFixture(self, fixture):
                    if fixture.body.type == Box2D.b2_dynamicBody and fixture.TestPoint(self.point):
                        self.fixture = fixture
                        return False # stop after first one
                    return True
            
            callback = QueryCallback(world_p)
            self.world.QueryAABB(callback, aabb)
            
            if callback.fixture:
                self.grabbed_body = callback.fixture.body
                self.mouse_joint = self.world.CreateMouseJoint(
                    bodyA=self.mouse_body,
                    bodyB=self.grabbed_body,
                    target=world_p,
                    maxForce=1000.0 * self.grabbed_body.mass
                )
                self.grabbed_body.awake = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mouse_joint:
                self.world.DestroyJoint(self.mouse_joint)
                self.mouse_joint = None
                self.grabbed_body = None

        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_joint:
                self.mouse_joint.target = world_p

    def reset_objects(self):
        """Resets the ball and table positions"""
        # Reset Ball
        self.ball.position = (5, 1)
        self.ball.linearVelocity = (0, 0)
        self.ball.angularVelocity = 0
        
        # Reset Table
        self.table.position = (-5, config.TABLE_HEIGHT/2)
        self.table.linearVelocity = (0, 0)
        self.table.angularVelocity = 0
        self.table.angle = 0


    def render(self):
        self.screen.fill((30, 30, 40))
        # Draw Floor
        pygame.draw.line(self.screen, (100, 100, 100), 
                         self.w2s((-100, 0)), self.w2s((100, 0)), 5)
        colors = {
            Box2D.b2_staticBody: (255, 255, 255),
            Box2D.b2_dynamicBody: (150, 150, 200),
        }
        # Draw all bodies
        for body in self.world.bodies:
            for fixture in body.fixtures:
                shape = fixture.shape
                color = colors.get(body.type, (150, 150, 200))
                if isinstance(shape, polygonShape):
                    vertices = [self.w2s(body.transform * v) for v in shape.vertices]
                    pygame.draw.polygon(self.screen, color, vertices)
                    pygame.draw.polygon(self.screen, (255, 255, 255), vertices, 1)
                elif isinstance(shape, circleShape):
                    center = self.w2s(body.transform * shape.pos)
                    radius = int(shape.radius * config.PPM)
                    pygame.draw.circle(self.screen, color, center, radius)
                    pygame.draw.circle(self.screen, (255, 255, 255), center, radius, 1)
                    # draw a line to show rotation
                    ax = body.transform.R.x_axis
                    end_pt = (center[0] + ax[0] * radius, center[1] - ax[1] * radius)
                    pygame.draw.line(self.screen, (255, 255, 255), center, end_pt, 1)
                elif isinstance(shape, edgeShape):
                    v1 = self.w2s(body.transform * shape.vertices[0])
                    v2 = self.w2s(body.transform * shape.vertices[1])
                    pygame.draw.line(self.screen, color, v1, v2, 3)
        # Draw mouse joint line
        if self.mouse_joint:
            p1 = self.w2s(self.mouse_joint.anchorB)
            p2 = self.w2s(self.mouse_joint.target)
            pygame.draw.line(self.screen, (0, 255, 0), p1, p2, 2)

        # Draw Validation Button (bottom right)
        button_w, button_h = 140, 40
        button_x = config.SCREEN_WIDTH - button_w - 20
        button_y = config.SCREEN_HEIGHT - button_h - 20
        self.validation_button_rect = pygame.Rect(button_x, button_y, button_w, button_h)
        pygame.draw.rect(self.screen, (0, 180, 0), self.validation_button_rect)
        label = self.font.render("VALIDATE ACTION", True, (255,255,255))
        self.screen.blit(label, (button_x + 10, button_y + 10))

    def step(self):
        self.world.Step(config.TIME_STEP, config.VEL_ITERS, config.POS_ITERS)
        self.world.ClearForces()
