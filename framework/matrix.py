"""Matrizes homogêneas: vetores-coluna, eixo Y para cima, ângulos em radianos."""

import math

import numpy as np


def identity():
    return np.eye(4, dtype=np.float32)


def translation(x, y, z):
    m = identity()
    m[:3, 3] = (x, y, z)
    return m


def scale(x, y, z):
    return np.diag([x, y, z, 1]).astype(np.float32)


def rotation_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=np.float32)


def rotation_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=np.float32)


def rotation_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32)


def normalized(v):
    v = np.asarray(v, dtype=np.float32)
    length = np.linalg.norm(v)
    if length < 1e-8:
        raise ValueError("Não é possível normalizar um vetor nulo.")
    return v / length


def look_at(eye, target, up=(0, 1, 0)):
    forward = normalized(np.asarray(target) - np.asarray(eye))
    right = normalized(np.cross(forward, up))
    vertical = np.cross(right, forward)
    m = identity()
    m[:3, :3] = np.array([right, vertical, -forward])
    m[:3, 3] = -m[:3, :3] @ np.asarray(eye)
    return m


def perspective(fov, aspect, near, far):
    if not (aspect > 0 and 0 < near < far):
        raise ValueError("Volume de perspectiva inválido.")
    f = 1 / math.tan(fov / 2)
    return np.array(
        [
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
            [0, 0, -1, 0],
        ],
        dtype=np.float32,
    )


def orthographic(left, right, bottom, top, near, far):
    return np.array(
        [
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )
