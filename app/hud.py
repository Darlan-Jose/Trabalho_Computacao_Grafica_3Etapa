"""Painel responsivo com telemetria, mapa e linha do tempo interativa."""

import math

import pygame

from app.mission import CYCLE_DURATION, DRONE_PAD, HELI_PAD, MEETING, STAGES, rotor_motion

INK = (229, 240, 240)
MUTED = (148, 175, 185)
TEAL = (91, 231, 195)
GOLD = (255, 186, 103)
PANEL = (12, 26, 37, 238)
EDGE = (82, 125, 143, 85)


class HUD:
    def __init__(self):
        self.fonts = {size: pygame.font.Font(None, size) for size in (16, 18, 20, 22, 25, 28, 36)}
        self.show_help = False
        self.scale = 1.0
        self.hit_regions = []
        self.tracking = False

    def text(self, surface, text, position, size=22, color=INK):
        surface.blit(self.fonts[size].render(text, True, color), position)

    def panel(self, surface, rect, radius=12):
        pygame.draw.rect(surface, PANEL, rect, border_radius=radius)
        pygame.draw.rect(surface, EDGE, rect, width=1, border_radius=radius)

    def wrapped(self, surface, text, position, max_width, size=20):
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

    def handle_click(self, position, mission, camera):
        """Retorna True quando o clique pertence a um controle do painel."""
        point = tuple(value / self.scale for value in position)
        for rect, action in self.hit_regions:
            if rect.collidepoint(point):
                if action == "pause":
                    mission.paused = not mission.paused
                elif action == "follow":
                    camera.tracking = not camera.tracking
                elif isinstance(action, int):
                    mission.seek(action, max(0, min(0.999999, (point[0] - rect.x) / rect.width)))
                return True
        return False

    def draw_map(self, surface, rect, pose):
        self.panel(surface, rect)
        x, y, width, height = rect
        self.text(surface, "POSIÇÃO NA BASE", (x + 16, y + 12), 18, MUTED)
        plot = pygame.Rect(x + 16, y + 36, width - 32, height - 48)

        def point(position):
            return (
                round(plot.centerx + position[0] / 10 * plot.width / 2),
                round(plot.centery + position[2] / 8 * plot.height / 2),
            )

        for i in (-1, 0, 1):
            pygame.draw.line(
                surface,
                (36, 57, 69),
                (plot.centerx + i * 40, plot.top),
                (plot.centerx + i * 40, plot.bottom),
            )
            pygame.draw.line(
                surface,
                (36, 57, 69),
                (plot.left, plot.centery + i * 20),
                (plot.right, plot.centery + i * 20),
            )
        for pad, color in ((HELI_PAD, GOLD), (DRONE_PAD, TEAL)):
            pygame.draw.circle(surface, color, point(pad), 6, 1)
        pygame.draw.circle(surface, (86, 117, 128), point(MEETING), 3, 1)
        pygame.draw.line(surface, (79, 128, 135), point(pose.helicopter), point(pose.drone), 1)
        for position, yaw, color in (
            (pose.helicopter, pose.helicopter_yaw, GOLD),
            (pose.drone, pose.drone_yaw, TEAL),
        ):
            px, py = point(position)
            triangle = [
                (px + math.sin(yaw + a) * r, py + math.cos(yaw + a) * r)
                for a, r in ((0, 7), (2.4, 5), (-2.4, 5))
            ]
            pygame.draw.polygon(surface, color, triangle)

    def draw(self, size, mission, renderer, fps):
        # Espaço lógico mínimo: evita sobreposições ao redimensionar a janela.
        self.scale = min(1.0, size[0] / 960, size[1] / 640)
        w, h = (round(dimension / self.scale) for dimension in size)
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.hit_regions = []
        pose = mission.pose
        stage = STAGES[pose.stage_index]
        self.panel(surface, (20, 20, 368, 86))
        pygame.draw.rect(surface, TEAL, (36, 39, 4, 43), border_radius=2)
        self.text(surface, "A U R O R A   /   BASE AÉREA", (53, 35), 20, TEAL)
        self.text(surface, "Operação em formação", (52, 58), 36)
        follow = pygame.Rect(20, 116, 203, 31)
        self.panel(surface, follow, 8)
        self.text(
            surface,
            "F  /  " + ("CÂMERA SEGUINDO" if self.tracking else "SEGUIR AERONAVES"),
            (32, 125),
            18,
            TEAL if self.tracking else MUTED,
        )
        self.hit_regions.append((follow, "follow"))
        x = w - 248
        status = pygame.Rect(x, 20, 228, 34)
        self.panel(surface, (x, 20, 228, 166))
        color = GOLD if mission.paused else TEAL
        pygame.draw.circle(surface, color, (x + 18, 39), 4)
        self.text(
            surface, "PAUSADO" if mission.paused else "MISSÃO EM CURSO", (x + 32, 31), 22, color
        )
        self.hit_regions.append((status, "pause"))
        for row, (label, position, color, is_drone) in enumerate(
            [
                ("04  Helicóptero", pose.helicopter, GOLD, False),
                ("03  Drone", pose.drone, TEAL, True),
            ]
        ):
            yy = 66 + row * 38
            self.text(surface, label, (x + 16, yy), 22, color)
            self.text(surface, f"{position[1]:.1f} m", (x + 167, yy), 22)
            _, power = rotor_motion(mission.time, drone=is_drone)
            pygame.draw.rect(surface, (39, 60, 70), (x + 17, yy + 23, 190, 3), border_radius=1)
            if power > 0:
                pygame.draw.rect(
                    surface, color, (x + 17, yy + 23, max(1, 190 * power), 3), border_radius=1
                )
        self.text(
            surface,
            f"Separação  {math.dist(pose.helicopter, pose.drone):.1f} m",
            (x + 16, 151),
            18,
            MUTED,
        )
        self.text(surface, f"{mission.speed:g}×", (x + 188, 151), 20, INK)
        self.draw_map(surface, pygame.Rect(x, 196, 228, 142), pose)
        bottom = h - 151
        self.panel(surface, (20, bottom, w - 40, 131))
        pause = pygame.Rect(37, bottom + 17, 39, 39)
        pygame.draw.rect(surface, (39, 71, 80), pause, border_radius=9)
        if mission.paused:
            pygame.draw.polygon(
                surface, TEAL, [(51, bottom + 27), (51, bottom + 47), (65, bottom + 37)]
            )
        else:
            for px in (49, 58):
                pygame.draw.rect(surface, TEAL, (px, bottom + 28, 5, 18), border_radius=1)
        self.hit_regions.append((pause, "pause"))
        self.text(surface, f"{pose.stage_index + 1:02d} / 09", (92, bottom + 17), 20, TEAL)
        self.text(surface, stage.name.upper(), (164, bottom + 13), 28)
        self.text(
            surface,
            f"{mission.time % CYCLE_DURATION:04.1f} / 37 s",
            (w - 163, bottom + 18),
            20,
            MUTED,
        )
        self.wrapped(surface, stage.description, (92, bottom + 41), w - 139, 20)
        gap, left = 7, 38
        segment = (w - 76 - gap * (len(STAGES) - 1)) / len(STAGES)
        for i, item in enumerate(STAGES):
            xx = left + i * (segment + gap)
            pygame.draw.rect(surface, (41, 62, 75), (xx, bottom + 77, segment, 5), border_radius=2)
            fraction = 1 if i < pose.stage_index else pose.progress if i == pose.stage_index else 0
            if fraction:
                pygame.draw.rect(
                    surface, TEAL, (xx, bottom + 77, max(1, segment * fraction), 5), border_radius=2
                )
            if w >= 1120:
                self.text(
                    surface,
                    item.name,
                    (xx, bottom + 87),
                    16,
                    TEAL if i == pose.stage_index else MUTED,
                )
            self.hit_regions.append((pygame.Rect(xx, bottom + 72, segment, 30), i))
        controls = (
            "ESPAÇO  pausar   ·   ARRASTE  orbitar   ·   SCROLL  zoom   ·   H  ajuda"
            if w >= 1120
            else "ESPAÇO  pausar   ·   ARRASTE  câmera   ·   H  ajuda"
        )
        self.text(surface, controls, (38, bottom + 108), 18, MUTED)
        self.text(
            surface,
            f"CICLO {pose.cycle + 1:02d}   /   {fps:.0f} fps",
            (w - 169, bottom + 108),
            18,
            MUTED,
        )
        if self.show_help:
            self.panel(surface, (20, 159, 390, 328))
            self.text(surface, "COMANDOS DA MISSÃO", (38, 177), 25, TEAL)
            lines = [
                "Espaço  ·  pausar / continuar",
                "Clique na linha do tempo  ·  escolher instante",
                "Arraste / setas  ·  orbitar   |   roda / Q E  ·  zoom",
                "W A S D  ·  mover   |   F  ·  seguir aeronaves",
                "1 / 2 / 3  ·  base / encontro / vista superior",
                "C  ·  restaurar câmera   |   +/-  ·  velocidade",
                "R  ·  reiniciar   |   N  ·  próxima etapa",
                f"P  ·  sombras {'ligadas' if renderer.shadows_enabled else 'desligadas'}",
                f"B  ·  faixas {'ligadas' if renderer.procedural_enabled else 'desligadas'}",
                "F12  ·  captura   |   Tab  ·  ocultar painel",
                "H  ·  fechar ajuda   |   Esc  ·  sair",
            ]
            for i, line in enumerate(lines):
                self.text(surface, line, (38, 212 + i * 23), 20, MUTED)
        return pygame.transform.smoothscale(surface, size) if self.scale != 1 else surface
