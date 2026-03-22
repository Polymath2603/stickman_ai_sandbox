from environment.objects import EnvironmentManager

class Scene:
    def __init__(self, world):
        self.world = world
        self.env_manager = EnvironmentManager(world)

    def get_objects(self):
        return self.env_manager.get_objects()
