"""Criação de contexto com antisserrilhamento MSAA e fallback sem amostras."""

import pygame


def create_window(size, samples=4):
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    for count in (samples, 0) if samples else (0,):
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, int(count > 0))
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, count)
        try:
            pygame.display.set_mode(size, flags)
            return pygame.display.gl_get_attribute(pygame.GL_MULTISAMPLESAMPLES)
        except pygame.error:
            if count == 0:
                raise
            print(f"MSAA {count}x indisponível; tentando contexto sem MSAA.")
