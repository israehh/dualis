"""Escenas F1: base + gestor con escena activa y cambio verificable.

Sin habitaciones, sin entidades, sin gameplay. Solo ciclo de vida.
"""


class Scene:
    name = "scene"

    def __init__(self, bus=None):
        self.bus = bus
        self.entered = False
        self.exited = False

    def enter(self):
        self.entered = True
        self.exited = False
        if self.bus is not None:
            self.bus.emit("SCENE_ENTER", {"scene": self.name})

    def exit(self):
        self.exited = True
        if self.bus is not None:
            self.bus.emit("SCENE_EXIT", {"scene": self.name})

    def update(self, dt):
        pass

    def render(self, surface, fps=0.0):
        pass


class SceneManager:
    def __init__(self, bus):
        self.bus = bus
        self.active = None
        self.active_scene = None
        self.visits = []

    def enter_empty(self, name="void"):
        self.active = name
        self.active_scene = None
        self.visits.append(name)
        self.bus.emit("ROOM_ENTER", {"room": name})

    def set_scene(self, scene):
        if self.active_scene is not None:
            self.active_scene.exit()
        self.active_scene = scene
        self.active = scene.name
        self.visits.append(scene.name)
        scene.enter()
        return scene

    def update(self, dt):
        if self.active_scene is not None:
            self.active_scene.update(dt)

    def render(self, surface, fps=0.0):
        if self.active_scene is not None:
            self.active_scene.render(surface, fps)
