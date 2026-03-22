import pymunk
from utils import config

class SandboxObject:
    def __init__(self, world, obj_id, obj_type, pos, mass=2.0, size=(40, 40)):
        self.id = obj_id
        self.type = obj_type
        self.is_held = False
        
        moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 0.8
        
        world.add_body(self.body)
        world.add_shape(self.shape)

class EnvironmentManager:
    def __init__(self, world):
        self.world = world
        self.objects = []
        
        # Add a default box
        self.add_object("box_1", "box", (800, config.SCREEN_HEIGHT - 100))
        self.add_object("box_2", "box", (200, config.SCREEN_HEIGHT - 100))

    def add_object(self, obj_id, obj_type, pos):
        obj = SandboxObject(self.world, obj_id, obj_type, pos)
        self.objects.append(obj)

    def get_objects(self):
        return self.objects
