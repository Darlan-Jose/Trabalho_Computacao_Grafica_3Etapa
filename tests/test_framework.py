import math
import unittest
from pathlib import Path

import numpy as np

from app.models import Drone
from app.scene import build_scene
from framework import matrix as mat
from framework.core import Camera, Object3D
from framework.geometry import box, cylinder, sphere, torus


class FrameworkTests(unittest.TestCase):
    def test_parent_transform_inheritance(self):
        parent, child = Object3D(), Object3D()
        parent.position[:] = (3, 0, 0)
        parent.rotation[1] = math.pi / 2
        child.position[:] = (0, 0, 2)
        parent.add(child)
        np.testing.assert_allclose(child.world_matrix()[:3, 3], (5, 0, 0), atol=1e-6)

    def test_cycle_rejected_and_reparent_supported(self):
        a, b, c = Object3D(), Object3D(), Object3D()
        a.add(b)
        with self.assertRaises(ValueError):
            b.add(a)
        c.add(b)
        self.assertEqual(a.children, [])
        self.assertIs(b.parent, c)

    def test_unit_normals_uv_and_outward_winding(self):
        for geometry in (box(), sphere(), cylinder(), cylinder(top_radius=0.16), torus()):
            vertices = geometry.vertices
            self.assertEqual(vertices.shape[1], 8)
            self.assertEqual(len(vertices) % 3, 0)
            self.assertTrue(np.isfinite(vertices).all())
            np.testing.assert_allclose(np.linalg.norm(vertices[:, 3:6], axis=1), 1, atol=1e-6)
            self.assertTrue(((vertices[:, 6:] >= 0) & (vertices[:, 6:] <= 1)).all())
            triangles = vertices.reshape(-1, 3, 8)
            normal = np.cross(
                triangles[:, 1, :3] - triangles[:, 0, :3], triangles[:, 2, :3] - triangles[:, 0, :3]
            )
            orientation = (normal * triangles[:, :, 3:6].mean(axis=1)).sum(axis=1)
            self.assertTrue((orientation > 0).all())

    def test_nonuniform_scale_normal_matrix(self):
        transform = (mat.rotation_y(0.6) @ mat.scale(2, 0.5, 3))[:3, :3]
        tangent = mat.normalized((1, 1, 0))
        normal = mat.normalized((1, -1, 0))
        self.assertAlmostEqual(
            float(np.dot(transform @ tangent, np.linalg.inv(transform).T @ normal)), 0, places=6
        )

    def test_camera_view_and_perspective(self):
        camera = Camera()
        view = camera.view_matrix()
        np.testing.assert_allclose(view @ np.append(camera.eye, 1), (0, 0, 0, 1), atol=2e-6)
        projection = mat.perspective(math.pi / 3, 16 / 9, 0.1, 100)
        for z, expected in ((-0.1, -1), (-100, 1)):
            clip = projection @ np.array([0, 0, z, 1])
            self.assertAlmostEqual(clip[2] / clip[3], expected, places=5)

    def test_four_independent_rotors_inherit_drone_motion(self):
        drone = Drone()
        self.assertEqual(len(drone.rotors), 4)
        before = drone.rotors[0].world_matrix()[:3, 3].copy()
        drone.position[:] = (2, 3, 4)
        drone.animate_rotors(12)
        np.testing.assert_allclose(
            drone.rotors[0].world_matrix()[:3, 3] - before, (2, 3, 4), atol=1e-6
        )
        angles = [float(rotor.rotation[1]) for rotor in drone.rotors]
        drone.animate_rotors(12.001)
        delta = [
            (float(rotor.rotation[1]) - old + math.pi) % math.tau - math.pi
            for rotor, old in zip(drone.rotors, angles)
        ]
        self.assertGreater(delta[0], 0)
        self.assertLess(delta[1], 0)
        self.assertGreater(delta[3], 0)

    def test_all_texture_assets_exist_and_world_scales_invertible(self):
        root = Path(__file__).resolve().parents[1]
        scene, _, _ = build_scene()
        for mesh, world in scene.meshes():
            self.assertNotEqual(np.linalg.det(world[:3, :3]), 0)
            if mesh.material.texture:
                self.assertTrue((root / mesh.material.texture).is_file())

    def test_camera_can_move_without_mission(self):
        camera = Camera()
        before = camera.view_matrix().copy()
        camera.control(1, 0.2, -0.1, 1, 1, 0.2)
        self.assertFalse(np.allclose(before, camera.view_matrix()))

    def test_camera_tracking_converges_independently_of_frame_rate(self):
        targets = []
        for fps in (30, 144):
            camera = Camera()
            camera.tracking = True
            for _ in range(fps):
                camera.follow((1, 3, 0), (4, 3, 0), 1 / fps)
            targets.append(camera.target.copy())
        np.testing.assert_allclose(targets[0], targets[1], atol=2e-6)

    def test_manual_pan_releases_tracking_and_drag_is_clamped(self):
        camera = Camera()
        camera.tracking = True
        camera.control(0, 0, 0, 1, 0, 0.1)
        self.assertFalse(camera.tracking)
        camera.drag(20, 10000)
        self.assertLessEqual(camera.elevation, 1.45)
        camera.drag(0, -20000)
        self.assertGreaterEqual(camera.elevation, 0.12)


if __name__ == "__main__":
    unittest.main()
