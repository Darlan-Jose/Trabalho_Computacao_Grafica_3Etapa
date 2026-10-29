"""Teste real da GPU/Mesa: shaders, FBO, sombras, animação e pausa.

Execute da raiz: python tools/validate_render.py
Linux sem display: usa SDL offscreen. Não é necessário para rodar a aplicação.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pygame
from OpenGL import GL as gl

from app.hud import HUD
from app.mission import Mission
from app.scene import apply_mission, build_scene
from framework.core import Camera
from framework.renderer import Renderer


def validate():
    pygame.display.init()
    pygame.font.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    size = (960, 640)
    pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
    renderer = None
    try:
        renderer = Renderer(1024)
        scene, heli, drone = build_scene()
        camera, mission = Camera(), Mission()

        def frame(t, shadows=True):
            mission.time = t
            renderer.shadows_enabled = shadows
            apply_mission(mission, heli, drone)
            renderer.render(scene, camera, size)
            return np.frombuffer(
                gl.glReadPixels(0, 0, *size, gl.GL_RGB, gl.GL_UNSIGNED_BYTE), dtype=np.uint8
            ).copy()

        lit = frame(16, False)
        shadowed = frame(16, True)
        difference = lit.astype(int) - shadowed.astype(int)
        changed = np.count_nonzero(np.max(np.abs(difference.reshape(-1, 3)), axis=1) > 12)
        assert changed > 1000, f"Sombra não altera pixels suficientes: {changed}"
        assert difference.sum() > 0, "Sombras deveriam reduzir a contribuição de luz direta."

        def depth():
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, renderer.shadow.fbo)
            data = gl.glReadPixels(0, 0, 1024, 1024, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            return np.asarray(data, dtype=np.float32).copy()

        depth_before = depth()
        assert np.isfinite(depth_before).all()
        assert float(depth_before.min()) < 0.9, "Mapa de sombras vazio."
        later = frame(23)
        depth_after = depth()
        assert not np.array_equal(depth_before, depth_after), (
            "Mapa não acompanha os modelos animados."
        )
        assert not np.array_equal(later, shadowed), "Cena não muda durante a missão."
        mission.paused = True
        mission.advance(4)
        paused = frame(mission.time)
        assert np.array_equal(later, paused), "Pausa modificou a imagem da cena."
        camera.control(0.3, 0.1, 0, 0, 0, 0.5)
        moved = frame(mission.time)
        assert not np.array_equal(paused, moved), "Câmera parou durante a pausa."
        hud = HUD()
        hud.show_help = True
        renderer.draw_overlay(hud.draw(size, mission, renderer, 60))
        assert gl.glGetError() == gl.GL_NO_ERROR
        print(
            f"OK: shaders, texturas, FBO, {changed} pixels de sombra, sombra dinâmica, pausa, câmera e HUD."
        )
        print("OpenGL:", gl.glGetString(gl.GL_VERSION).decode())
        print("GPU:", gl.glGetString(gl.GL_RENDERER).decode())
    finally:
        if renderer is not None:
            renderer.close()
        pygame.quit()


if __name__ == "__main__":
    validate()
