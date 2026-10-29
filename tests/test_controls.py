"""Hit testing do painel não precisa de janela nem contexto OpenGL."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pygame

from app.hud import HUD
from app.mission import Mission
from framework.core import Camera
from framework.window import create_window


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()

    def test_resized_timeline_selects_same_time_while_paused(self):
        for size in ((1280, 800), (960, 640), (480, 480)):
            hud, mission, camera = HUD(), Mission(), Camera()
            mission.paused = True
            surface = hud.draw(
                size, mission, SimpleNamespace(shadows_enabled=True, procedural_enabled=True), 60
            )
            self.assertEqual(surface.get_size(), size)
            rect = next(rect for rect, action in hud.hit_regions if action == 4)
            click = ((rect.x + rect.width * 0.5) * hud.scale, rect.centery * hud.scale)
            self.assertTrue(hud.handle_click(click, mission, camera))
            self.assertAlmostEqual(mission.time, 17, places=6)
            self.assertTrue(mission.paused)

    def test_pause_and_follow_buttons(self):
        hud, mission, camera = HUD(), Mission(), Camera()
        hud.draw(
            (960, 640), mission, SimpleNamespace(shadows_enabled=True, procedural_enabled=True), 60
        )
        for action in ("pause", "follow"):
            rect = next(rect for rect, kind in hud.hit_regions if kind == action)
            self.assertTrue(hud.handle_click(rect.center, mission, camera))
        self.assertTrue(mission.paused)
        self.assertTrue(camera.tracking)
        self.assertFalse(hud.handle_click((0, 0), mission, camera))

    def test_msaa_falls_back_if_driver_rejects_it(self):
        with (
            patch("pygame.display.gl_set_attribute") as attributes,
            patch("pygame.display.set_mode", side_effect=[pygame.error("No MSAA"), None]) as mode,
            patch("pygame.display.gl_get_attribute", return_value=0),
        ):
            self.assertEqual(create_window((960, 640), 4), 0)
            self.assertEqual(mode.call_count, 2)
            self.assertIn(
                ((pygame.GL_MULTISAMPLESAMPLES, 0),), [call for call in attributes.call_args_list]
            )


if __name__ == "__main__":
    unittest.main()
