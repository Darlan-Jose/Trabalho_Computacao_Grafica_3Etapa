"""Modelagem por composição de caixas, esferas e cilindros do framework."""

import math

from framework.core import Material, Mesh, Object3D
from framework.geometry import box, cylinder, sphere

WHITE = Material((0.82, 0.88, 0.88), specular=0.4)
NAVY = Material((0.065, 0.12, 0.16), specular=0.4)
TEAL = Material((0.12, 0.65, 0.60), specular=0.5)
ORANGE = Material((0.96, 0.38, 0.16), specular=0.4)
GLASS = Material((0.07, 0.27, 0.35), specular=0.9, shininess=80)
METAL = Material((0.38, 0.46, 0.49), specular=0.7, shininess=64)
RUBBER = Material((0.025, 0.04, 0.05), specular=0.08)
YELLOW = Material((1.0, 0.71, 0.22))
GREEN_LIGHT = Material((0.2, 1, 0.65), emission=1)
RED_LIGHT = Material((1, 0.2, 0.1), emission=1)


def part(
    parent,
    name,
    geometry,
    material,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    rotation=(0, 0, 0),
    cast_shadow=True,
):
    mesh = Mesh(geometry, material, name, cast_shadow)
    mesh.position[:] = position
    mesh.scaling[:] = scale
    mesh.rotation[:] = rotation
    parent.add(mesh)
    return mesh


def group(parent, name, position=(0, 0, 0)):
    node = Object3D(name)
    node.position[:] = position
    parent.add(node)
    return node


class Drone(Object3D):
    def __init__(self):
        super().__init__("drone_quatro_helices")
        self.rotors = []
        part(self, "corpo", sphere(), WHITE, (0, 0.43, 0), (0.72, 0.32, 0.8))
        part(self, "cobertura", sphere(), TEAL, (0, 0.55, 0), (0.56, 0.15, 0.62))
        part(self, "bateria", box(), NAVY, (0, 0.43, -0.18), (0.38, 0.22, 0.44))
        for x, z in ((-0.68, -0.63), (0.68, -0.63), (-0.68, 0.63), (0.68, 0.63)):
            length = math.hypot(x, z)
            part(
                self,
                "braco",
                box(),
                WHITE,
                (x / 2, 0.43, z / 2),
                (0.12, 0.10, length),
                (0, math.atan2(x, z), 0),
            )
            part(self, "motor", cylinder(), NAVY, (x, 0.48, z), (0.20, 0.24, 0.20))
            rotor = group(self, f"helice_{len(self.rotors) + 1}", (x, 0.63, z))
            part(rotor, "pa", box(), TEAL, (0, 0, 0), (0.88, 0.025, 0.10))
            part(rotor, "ponta_a", box(), WHITE, (0.37, 0.002, 0), (0.13, 0.028, 0.10))
            part(rotor, "ponta_b", box(), WHITE, (-0.37, 0.002, 0), (0.13, 0.028, 0.10))
            part(rotor, "eixo", cylinder(), METAL, (0, 0.025, 0), (0.10, 0.07, 0.10))
            self.rotors.append(rotor)
            part(
                self,
                "luz",
                sphere(),
                RED_LIGHT if x < 0 else GREEN_LIGHT,
                (x, 0.39, z),
                (0.10, 0.06, 0.10),
            )
        for x in (-0.28, 0.28):
            part(self, "perna", box(), METAL, (x, 0.24, 0), (0.05, 0.30, 0.05))
            part(self, "patim", box(), RUBBER, (x, 0.09, 0), (0.08, 0.08, 0.6))
        self.gimbal = group(self, "gimbal", (0, 0.30, 0.28))
        part(self.gimbal, "camera", sphere(), NAVY, (0, 0, 0), (0.25, 0.23, 0.25))
        part(
            self.gimbal,
            "lente",
            cylinder(),
            GLASS,
            (0, 0, 0.13),
            (0.13, 0.08, 0.13),
            (math.pi / 2, 0, 0),
        )

    def animate_rotors(self, time):
        for index, rotor in enumerate(self.rotors):
            # Pares diagonais em sentidos contrários, sem incremento por quadro.
            sign = 1 if index in (0, 3) else -1
            rotor.rotation[1] = sign * time * 43 + index * 0.7
        self.gimbal.rotation[0] = -0.15 + 0.12 * math.sin(time * 1.1)


class Helicopter(Object3D):
    def __init__(self):
        super().__init__("helicoptero_estilizado")
        part(self, "fuselagem", sphere(), ORANGE, (0, 0.95, 0), (1.36, 1.25, 2.15))
        part(self, "cabine", sphere(), GLASS, (0, 1.07, 0.66), (1.18, 0.98, 1.20))
        part(self, "nariz", sphere(), ORANGE, (0, 0.75, 0.91), (0.96, 0.48, 0.88))
        part(
            self,
            "coluna_parabrisa",
            box(),
            WHITE,
            (0, 1.32, 1.0),
            (0.065, 0.6, 0.065),
            (0.45, 0, 0),
        )
        part(self, "teto", sphere(), ORANGE, (0, 1.49, 0.22), (1.08, 0.32, 1.45))
        part(self, "motor", sphere(), NAVY, (0, 1.52, -0.32), (0.80, 0.42, 1.03))
        # Cone truncado orientado ao longo da cauda (-Z).
        part(
            self,
            "cauda",
            cylinder(top_radius=0.16),
            ORANGE,
            (0, 1.02, -1.70),
            (0.62, 2.2, 0.62),
            (-math.pi / 2, 0, 0),
        )
        part(
            self,
            "estabilizador_vertical",
            box(),
            ORANGE,
            (0, 1.44, -2.64),
            (0.12, 1.05, 0.59),
            (0.2, 0, 0),
        )
        part(self, "estabilizador_horizontal", box(), WHITE, (0, 1.12, -2.27), (1.32, 0.09, 0.42))
        part(self, "eixo_rotor", cylinder(), METAL, (0, 1.88, -0.1), (0.16, 0.62, 0.16))
        self.main_rotor = group(self, "rotor_principal", (0, 2.12, -0.1))
        for angle in (0, math.pi / 2):
            blade = group(self.main_rotor, "conjunto_pas")
            blade.rotation[1] = angle
            part(blade, "pa", box(), NAVY, (0, 0, 0), (4.2, 0.045, 0.16))
            for x in (-1.92, 1.92):
                part(blade, "ponta", box(), YELLOW, (x, 0.004, 0), (0.30, 0.05, 0.16))
        part(self.main_rotor, "cubo", sphere(), METAL, (0, 0.06, 0), (0.32, 0.17, 0.32))
        self.tail_rotor = group(self, "rotor_cauda", (0.17, 1.49, -2.66))
        for angle in (0, math.pi / 2):
            part(
                self.tail_rotor,
                "pa_cauda",
                box(),
                WHITE,
                (0, 0, 0),
                (0.045, 0.90, 0.10),
                (angle, 0, 0),
            )
        for x in (-0.65, 0.65):
            for z in (-0.48, 0.52):
                part(
                    self,
                    "suporte_patim",
                    box(),
                    METAL,
                    (x, 0.40, z),
                    (0.08, 0.56, 0.08),
                    (0, 0, x * 0.24),
                )
            part(self, "patim", box(), NAVY, (x, 0.12, 0), (0.13, 0.15, 2.3))
            part(self, "ponta_patim", box(), NAVY, (x, 0.18, 1.13), (0.13, 0.15, 0.35), (0.4, 0, 0))
        for x in (-0.67, 0.67):
            part(self, "faixa_lateral", box(), WHITE, (x, 0.88, -0.14), (0.025, 0.16, 1.0))
            part(
                self,
                "luz_navegacao",
                sphere(),
                RED_LIGHT if x < 0 else GREEN_LIGHT,
                (x, 1.10, -0.35),
                (0.12, 0.12, 0.12),
            )
        part(self, "farol", sphere(), WHITE, (0, 0.64, 1.24), (0.25, 0.16, 0.12))

    def animate_rotors(self, time):
        self.main_rotor.rotation[1] = time * 23
        self.tail_rotor.rotation[0] = time * 37
