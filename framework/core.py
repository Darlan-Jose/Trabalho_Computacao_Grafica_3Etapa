"""Grafo de cena: Object3D → Scene/Camera/Mesh; Geometry + Material."""

import math
from dataclasses import dataclass

import numpy as np

from framework import matrix as mat


class Object3D:
    def __init__(self, name="objeto"):
        self.name = name
        self.position = np.zeros(3, dtype=np.float32)
        self.rotation = np.zeros(3, dtype=np.float32)
        self.scaling = np.ones(3, dtype=np.float32)
        self.parent = None
        self.children = []
        self.visible = True

    def add(self, child):
        ancestor = self
        while ancestor is not None:
            if ancestor is child:
                raise ValueError("O grafo não pode conter ciclos.")
            ancestor = ancestor.parent
        if child.parent is not None:
            child.parent.children.remove(child)
        child.parent = self
        self.children.append(child)
        return child

    def local_matrix(self):
        x, y, z = self.rotation
        return (
            mat.translation(*self.position)
            @ mat.rotation_y(y)
            @ mat.rotation_x(x)
            @ mat.rotation_z(z)
            @ mat.scale(*self.scaling)
        )

    def world_matrix(self):
        local = self.local_matrix()
        return local if self.parent is None else self.parent.world_matrix() @ local

    def meshes(self, parent_matrix=None):
        if not self.visible:
            return
        world = self.local_matrix()
        if parent_matrix is not None:
            world = parent_matrix @ world
        if isinstance(self, Mesh):
            yield self, world
        for child in self.children:
            yield from child.meshes(world)


class Scene(Object3D):
    pass


@dataclass(frozen=True)
class Material:
    color: tuple = (1, 1, 1)
    texture: str | None = None
    uv_repeat: tuple = (1, 1)
    specular: float = 0.25
    shininess: float = 32.0
    emission: float = 0.0
    procedural: bool = False


class Mesh(Object3D):
    def __init__(self, geometry, material, name="malha", cast_shadow=True):
        super().__init__(name)
        self.geometry = geometry
        self.material = material
        self.cast_shadow = cast_shadow


class Camera(Object3D):
    """Câmera orbital em perspectiva com alvo deslocável pelo teclado."""

    def __init__(self):
        super().__init__("camera")
        self.reset()

    def reset(self):
        self.target = np.array([0, 0.2, 0], dtype=np.float32)
        self.azimuth = math.radians(34)
        self.elevation = math.radians(32)
        self.distance = 24.0
        self.tracking = False

    @property
    def eye(self):
        c = math.cos(self.elevation)
        return self.target + self.distance * np.array(
            [c * math.sin(self.azimuth), math.sin(self.elevation), c * math.cos(self.azimuth)],
            dtype=np.float32,
        )

    def view_matrix(self):
        return mat.look_at(self.eye, self.target)

    def projection_matrix(self, aspect):
        return mat.perspective(math.radians(48), aspect, 0.1, 100.0)

    def control(self, orbit_x, orbit_y, zoom, pan_x, pan_z, dt):
        self.azimuth += orbit_x * dt
        self.elevation = np.clip(self.elevation + orbit_y * dt, 0.12, 1.45)
        self.distance = np.clip(self.distance + zoom * dt * 9, 6, 40)
        right = np.array([math.cos(self.azimuth), 0, -math.sin(self.azimuth)])
        forward = np.array([-math.sin(self.azimuth), 0, -math.cos(self.azimuth)])
        self.target += (right * pan_x + forward * pan_z) * dt * 5
        self.target[[0, 2]] = np.clip(self.target[[0, 2]], -12, 12)
        if pan_x or pan_z:
            self.tracking = False

    def drag(self, dx, dy):
        self.azimuth -= dx * 0.006
        self.elevation = float(np.clip(self.elevation + dy * 0.006, 0.12, 1.45))

    def follow(self, helicopter, drone, dt):
        if self.tracking:
            target = (np.asarray(helicopter) + np.asarray(drone)) * 0.5 + (0, 0.8, 0)
            self.target += (target - self.target) * (1 - math.exp(-4 * dt))
