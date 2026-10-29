"""Gera as imagens originais da cena; execução opcional, PNGs já incluídos.

Somente desenho 2D com Pygame e ruído determinístico; sem arquivos externos.
"""

import os
import random
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

ROOT = Path(__file__).resolve().parents[1]


def generate():
    pygame.font.init()
    out = ROOT / "assets" / "textures"
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2026)
    concrete = pygame.Surface((256, 256))
    for y in range(256):
        for x in range(256):
            gray = 215 + rng.randrange(-15, 16)
            concrete.set_at((x, y), (gray, gray, min(255, gray + 3)))
    pygame.image.save(concrete, str(out / "concrete.png"))
    for letter, filename, color in [
        ("H", "helipad_h.png", (243, 180, 65)),
        ("D", "helipad_d.png", (74, 217, 190)),
    ]:
        surface = pygame.Surface((512, 512))
        surface.fill((35, 55, 62))
        pygame.draw.circle(surface, color, (256, 256), 236, 12)
        pygame.draw.circle(surface, (77, 96, 100), (256, 256), 212, 2)
        font = pygame.font.Font(None, 280)
        text = font.render(letter, True, (233, 240, 236))
        surface.blit(text, text.get_rect(center=(256, 250)))
        font = pygame.font.Font(None, 28)
        text = font.render("AURORA  /  " + ("01" if letter == "H" else "02"), True, color)
        surface.blit(text, text.get_rect(center=(256, 415)))
        pygame.image.save(surface, str(out / filename))
    surface = pygame.Surface((640, 80))
    surface.fill((20, 36, 46))
    text = pygame.font.Font(None, 62).render("A U R O R A   /   BASE 01", True, (214, 243, 231))
    surface.blit(text, text.get_rect(center=(320, 40)))
    pygame.image.save(surface, str(out / "aurora.png"))
    solar = pygame.Surface((256, 256))
    solar.fill((20, 43, 68))
    for row in range(6):
        for col in range(4):
            cell = pygame.Rect(6 + col * 62, 6 + row * 41, 58, 37)
            pygame.draw.rect(
                solar, (30 + row * 2, 63 + row * 3, 94 + row * 3), cell, border_radius=3
            )
            pygame.draw.rect(solar, (100, 139, 161), cell, width=1, border_radius=3)
            pygame.draw.line(
                solar, (74, 112, 142), (cell.centerx, cell.top), (cell.centerx, cell.bottom)
            )
    pygame.draw.rect(solar, (174, 194, 202), solar.get_rect(), width=4)
    pygame.image.save(solar, str(out / "solar.png"))
    pygame.font.quit()


if __name__ == "__main__":
    generate()
    print("Texturas gravadas em assets/textures/.")
