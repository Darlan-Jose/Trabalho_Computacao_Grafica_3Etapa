"""Cenário da base aérea e aplicação das poses aos modelos hierárquicos."""

import math

from app.mission import DRONE_PAD, HELI_PAD
from app.models import (
    GREEN_LIGHT,
    METAL,
    NAVY,
    ORANGE,
    TEAL,
    WHITE,
    YELLOW,
    Drone,
    Helicopter,
    group,
    part,
)
from framework.core import Material, Scene
from framework.geometry import box, cylinder, sphere


def build_scene():
    scene = Scene("base_aurora")
    concrete = Material(
        (0.57, 0.65, 0.65), texture="assets/textures/concrete.png", uv_repeat=(8, 8), specular=0.05
    )
    part(scene, "plataforma", box(), NAVY, (0, -0.39, 0), (18, 0.7, 15))
    part(scene, "piso_texturizado", box(), concrete, (0, -0.025, 0), (17.8, 0.08, 14.8))
    part(
        scene,
        "solo",
        box(),
        Material((0.055, 0.13, 0.15)),
        (0, -0.84, 0),
        (150, 0.15, 150),
        cast_shadow=False,
    )
    # Juntas do pavimento e faixa central de circulação.
    for x in range(-8, 9, 2):
        part(
            scene,
            "junta_piso",
            box(),
            Material((0.24, 0.32, 0.33)),
            (x, 0.02, 0),
            (0.018, 0.008, 14.4),
            cast_shadow=False,
        )
    for z in range(-6, 7, 2):
        part(
            scene,
            "junta_piso",
            box(),
            Material((0.24, 0.32, 0.33)),
            (0, 0.02, z),
            (17.4, 0.008, 0.018),
            cast_shadow=False,
        )
    for z in range(-6, 7, 2):
        part(
            scene,
            "sinalizacao",
            box(),
            YELLOW,
            (0.3, 0.03, z),
            (0.09, 0.015, 0.8),
            cast_shadow=False,
        )
    for name, pad, size, label in [
        ("heliponto_h", HELI_PAD, 4.9, "helipad_h"),
        ("heliponto_d", DRONE_PAD, 3.6, "helipad_d"),
    ]:
        part(
            scene,
            name,
            cylinder(64),
            Material((0.13, 0.22, 0.25)),
            (pad[0], 0.07, pad[2]),
            (size, 0.14, size),
        )
        part(
            scene,
            name + "_imagem",
            box(),
            Material((1, 1, 1), texture=f"assets/textures/{label}.png", specular=0.05),
            (pad[0], 0.147, pad[2]),
            (size * 0.70, 0.014, size * 0.70),
            cast_shadow=False,
        )
        for i in range(12):
            a = math.tau * i / 12
            part(
                scene,
                "luz_heliponto",
                sphere(),
                GREEN_LIGHT,
                (pad[0] + math.cos(a) * size * 0.46, 0.17, pad[2] + math.sin(a) * size * 0.46),
                (0.10, 0.06, 0.10),
                cast_shadow=False,
            )
    # Hangar ao fundo, com porta segmentada e sinalização de segurança procedural.
    hangar = group(scene, "hangar", (-5.5, 0, -4.8))
    part(hangar, "edificio", box(), Material((0.19, 0.29, 0.32)), (0, 1.2, 0), (4.3, 2.4, 2.9))
    part(hangar, "cobertura", box(), TEAL, (0, 2.45, 0), (4.6, 0.18, 3.2))
    part(hangar, "porta", box(), NAVY, (0, 1.05, 1.46), (3.45, 2.05, 0.05))
    for y in (0.25, 0.55, 0.85, 1.15, 1.45, 1.75):
        part(hangar, "lamina_porta", box(), METAL, (0, y, 1.50), (3.3, 0.035, 0.03))
    hazard = Material((1, 0.69, 0.16), procedural=True)
    for x in (-1.9, 1.9):
        part(hangar, "faixa_seguranca", box(), hazard, (x, 1.05, 1.52), (0.20, 2.10, 0.08))
    part(
        hangar,
        "placa_aurora",
        box(),
        Material(texture="assets/textures/aurora.png", emission=0.45),
        (0, 2.12, 1.52),
        (2.5, 0.32, 0.05),
    )
    # Torre de controle e antena estáticas: apenas as duas aeronaves são personagens.
    tower = group(scene, "torre", (5.6, 0, -4.9))
    part(tower, "base", box(), WHITE, (0, 1.2, 0), (1.45, 2.4, 1.5))
    part(tower, "cabine", box(), NAVY, (0, 2.9, 0), (2.3, 1.1, 2.1))
    part(
        tower,
        "vidro",
        box(),
        Material((0.12, 0.39, 0.46), specular=0.8),
        (0, 2.92, 1.06),
        (1.94, 0.68, 0.025),
    )
    for x in (-1.16, 1.16):
        part(
            tower,
            "vidro_lateral",
            box(),
            Material((0.12, 0.39, 0.46), specular=0.8),
            (x, 2.92, 0),
            (0.025, 0.68, 1.74),
        )
    part(tower, "telhado", box(), TEAL, (0, 3.52, 0), (2.65, 0.16, 2.45))
    part(tower, "antena", cylinder(), METAL, (0, 4.0, 0), (0.06, 0.95, 0.06))
    part(tower, "baliza", sphere(), ORANGE, (0, 4.5, 0), (0.17, 0.17, 0.17))
    # Balizadores baixos evitam esconder os protagonistas.
    for x in (-8.3, 8.3):
        for z in (-6.5, -2.5, 1.5, 5.5):
            part(scene, "balizador", cylinder(), NAVY, (x, 0.25, z), (0.15, 0.5, 0.15))
            part(scene, "lente_balizador", sphere(), GREEN_LIGHT, (x, 0.52, z), (0.15, 0.12, 0.15))
    for x in (2.0, 3.15):
        part(
            scene,
            "caixa_equipamento",
            box(),
            Material((0.36, 0.44, 0.43)),
            (x, 0.37, -5.8),
            (0.85, 0.74, 0.85),
        )
        part(scene, "tampa_caixa", box(), YELLOW, (x, 0.77, -5.8), (0.90, 0.07, 0.90))
    helicopter, drone = Helicopter(), Drone()
    scene.add(helicopter)
    scene.add(drone)
    return scene, helicopter, drone


def apply_mission(mission, helicopter, drone):
    pose = mission.pose
    helicopter.position[:] = pose.helicopter
    helicopter.rotation[1] = pose.helicopter_yaw
    drone.position[:] = pose.drone
    drone.rotation[1] = pose.drone_yaw
    helicopter.animate_rotors(mission.time)
    drone.animate_rotors(mission.time)
