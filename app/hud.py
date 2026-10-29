"""Painel 2D renderizado como textura RGBA por um triângulo em tela cheia."""

import math

import pygame

from app.mission import CYCLE_DURATION, STAGES

INK = (226, 239, 238)
MUTED = (148, 176, 183)
TEAL = (86, 224, 195)
GOLD = (255, 192, 91)


class HUD:
    def __init__(self):
        self.fonts = {size: pygame.font.Font(None, size) for size in (18, 20, 22, 25, 28, 38, 44)}
        self.show_help = False

    def text(self, surface, text, position, size=22, color=INK):
        surface.blit(self.fonts[size].render(text, True, color), position)

    def wrapped(self, surface, text, position, max_width, size=22):
        x, y = position
        line = ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if self.fonts[size].size(candidate)[0] > max_width and line:
                self.text(surface, line, (x, y), size, MUTED)
                y += size
                line = word
            else:
                line = candidate
        if line:
            self.text(surface, line, (x, y), size, MUTED)

    def draw(self, size, mission, renderer, fps):
        w, h = size
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pose = mission.pose
        stage = STAGES[pose.stage_index]
        pygame.draw.rect(surface, (10, 23, 32, 228), (20, 20, 350, 80), border_radius=12)
        pygame.draw.rect(surface, TEAL, (36, 38, 4, 42), border_radius=2)
        self.text(surface, "BASE AURORA", (53, 31), 38)
        self.text(surface, "OPERAÇÃO DE APOIO  /  DRONE + HELICÓPTERO", (54, 69), 18, MUTED)
        if w >= 780:
            panel_x = w - 240
            pygame.draw.rect(surface, (10, 23, 32, 220), (panel_x, 20, 220, 154), border_radius=12)
            pygame.draw.circle(surface, GOLD if mission.paused else TEAL, (panel_x + 20, 42), 4)
            self.text(
                surface,
                "PAUSADO" if mission.paused else "MISSÃO EM CURSO",
                (panel_x + 33, 33),
                22,
                GOLD if mission.paused else TEAL,
            )
            distance = math.dist(pose.helicopter, pose.drone)
            for row, (label, value) in enumerate(
                [
                    ("Helicóptero", f"{pose.helicopter[1]:.1f} m"),
                    ("Drone", f"{pose.drone[1]:.1f} m"),
                    ("Separação", f"{distance:.1f} m"),
                    (
                        "Tempo / ritmo",
                        f"{mission.time % CYCLE_DURATION:04.1f}s / {mission.speed:g}x",
                    ),
                ]
            ):
                self.text(surface, label, (panel_x + 16, 63 + row * 23), 20, MUTED)
                self.text(surface, value, (panel_x + 142, 63 + row * 23), 20)
        # Rodapé de missão: descrição visível e progresso de cada etapa.
        bottom = h - 157
        pygame.draw.rect(surface, (10, 23, 32, 238), (20, bottom, w - 40, 137), border_radius=12)
        self.text(surface, f"{pose.stage_index + 1:02d}", (37, bottom + 14), 44, TEAL)
        self.text(surface, stage.name.upper(), (89, bottom + 12), 28)
        self.wrapped(surface, stage.description, (89, bottom + 41), w - 145, 20)
        segment_width = (w - 76 - 8 * (len(STAGES) - 1)) / len(STAGES)
        for i in range(len(STAGES)):
            x = 38 + i * (segment_width + 8)
            pygame.draw.rect(
                surface, (45, 65, 74), (x, bottom + 79, segment_width, 5), border_radius=2
            )
            fraction = 1 if i < pose.stage_index else pose.progress if i == pose.stage_index else 0
            if fraction:
                pygame.draw.rect(
                    surface,
                    TEAL,
                    (x, bottom + 79, max(1, segment_width * fraction), 5),
                    border_radius=2,
                )
        controls = (
            "ESPAÇO  pausar     SETAS  orbitar     W A S D  mover     Q / E  zoom     H  ajuda"
            if w >= 1000
            else "ESPAÇO  pausar    SETAS  câmera    H  ajuda"
        )
        self.text(surface, controls, (38, bottom + 102), 20, MUTED)
        if w >= 780:
            self.text(surface, f"{fps:04.1f} fps", (w - 100, bottom + 102), 18, MUTED)
        if self.show_help:
            pygame.draw.rect(surface, (10, 23, 32, 245), (20, 116, 360, 296), border_radius=12)
            self.text(surface, "CONTROLES", (39, 133), 25, TEAL)
            lines = [
                "Espaço  ·  pausar / continuar",
                "R  ·  reiniciar missão     N  ·  próxima etapa",
                "1 / 2 / 3  ·  vistas da base / encontro / topo",
                "C  ·  restaurar câmera     +/-  ·  velocidade",
                f"P  ·  sombras: {'ligadas' if renderer.shadows_enabled else 'desligadas'}",
                f"B  ·  faixas procedurais: {'ligadas' if renderer.procedural_enabled else 'desligadas'}",
                "F12  ·  salvar captura em captures/",
                "H  ·  fechar ajuda     Esc  ·  sair",
                "Câmera permanece livre durante a pausa.",
            ]
            for i, line in enumerate(lines):
                self.text(surface, line, (39, 169 + i * 25), 20, MUTED)
        return surface
