"""Primitivas próprias, trianguladas, com normais e UVs explícitos.

Cada linha: posição (3), normal (3), coordenada de textura (2).
Os dados ficam na CPU até Renderer criar o VAO/VBO compartilhado.
"""

import math
from functools import lru_cache

import numpy as np


class Geometry:
    def __init__(self, rows):
        self.vertices = np.asarray(rows, dtype=np.float32)


@lru_cache(maxsize=None)
def box():
    rows = []
    # Tangentes u,v: u × v = normal exterior (orientação anti-horária).
    faces = [
        ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
        ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
        ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
        ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
        ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
        ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
    ]
    for normal, u, v in faces:
        n, u, v = np.array(normal), np.array(u), np.array(v)
        corners = [
            n * 0.5 + u * a * 0.5 + v * b * 0.5 for a, b in [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        ]
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
        for i in (0, 1, 2, 0, 2, 3):
            rows.append([*corners[i], *normal, *uv[i]])
    return Geometry(rows)


@lru_cache(maxsize=None)
def sphere(segments=24, rings=12):
    rows = []

    def vertex(i, j):
        u, v = i / segments, j / rings
        theta, phi = u * math.tau, v * math.pi
        n = (math.sin(phi) * math.cos(theta), math.cos(phi), math.sin(phi) * math.sin(theta))
        return [*(c * 0.5 for c in n), *n, u, 1 - v]

    for j in range(rings):
        for i in range(segments):
            a, b, c, d = vertex(i, j), vertex(i + 1, j), vertex(i + 1, j + 1), vertex(i, j + 1)
            if j > 0:
                rows.extend((a, b, d))
            if j < rings - 1:
                rows.extend((b, c, d))
    return Geometry(rows)


@lru_cache(maxsize=None)
def cylinder(segments=32, top_radius=0.5):
    """Cilindro no eixo Y; top_radius=0 produz um cone."""
    rows = []
    slope = 0.5 - top_radius
    for i in range(segments):
        a, b = math.tau * i / segments, math.tau * (i + 1) / segments

        def side(angle, y, radius, u):
            n = np.array([math.cos(angle), slope, math.sin(angle)])
            n /= np.linalg.norm(n)
            return [radius * math.cos(angle), y, radius * math.sin(angle), *n, u, y + 0.5]

        va, vb = side(a, -0.5, 0.5, i / segments), side(b, -0.5, 0.5, (i + 1) / segments)
        vc, vd = (
            side(b, 0.5, top_radius, (i + 1) / segments),
            side(a, 0.5, top_radius, i / segments),
        )
        rows.extend((va, vd, vb))
        if top_radius > 0:
            rows.extend((vb, vd, vc))
        for y, r, ny in ((-0.5, 0.5, -1), (0.5, top_radius, 1)):
            if r == 0:
                continue
            center = [0, y, 0, 0, ny, 0, 0.5, 0.5]

            def edge(t, radius=r, height=y, normal_y=ny):
                return [
                    radius * math.cos(t),
                    height,
                    radius * math.sin(t),
                    0,
                    normal_y,
                    0,
                    0.5 + 0.5 * math.cos(t),
                    0.5 + 0.5 * math.sin(t),
                ]

            rows.extend((center, edge(b), edge(a)) if ny > 0 else (center, edge(a), edge(b)))
    return Geometry(rows)


@lru_cache(maxsize=None)
def torus(segments=32, rings=8, tube=0.025):
    """Anel no plano XZ, diâmetro externo unitário; usado nos protetores de hélice."""
    rows = []

    def vertex(i, j):
        u, v = i / segments, j / rings
        a, b = u * math.tau, v * math.tau
        radius = 0.5 - tube + tube * math.cos(b)
        normal = (math.cos(a) * math.cos(b), math.sin(b), math.sin(a) * math.cos(b))
        return [radius * math.cos(a), tube * math.sin(b), radius * math.sin(a), *normal, u, v]

    for i in range(segments):
        for j in range(rings):
            a, b, c, d = vertex(i, j), vertex(i + 1, j), vertex(i + 1, j + 1), vertex(i, j + 1)
            rows.extend((a, d, b, b, d, c))
    return Geometry(rows)
