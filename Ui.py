import pygame as py

class uimanager:
    def __init__(self, font_name=None, font_size=24):
        # Si no tienes un .ttf específico, usa None para la fuente por defecto
        self.font = py.font.SysFont(font_name, font_size)
        self.color = (255, 255, 255)

    def dibujar(self, screen, score, high_score, level, lives):
        #se renderizan los textos
        score_surf = self.font.render(f"SCORE: {score}", True, self.color)
        high_score_surf = self.font.render(f"BEST: {high_score}", True, self.color)
        level_surf = self.font.render(f"LVL: {level}", True, self.color)
        lives_surf = self.font.render(f"LIVES: {lives}", True, self.color)

        screen.blit(score_surf, (20, 10))
        screen.blit(high_score_surf, (200, 10))
        screen.blit(level_surf, (400, 10))
        screen.blit(lives_surf, (550, 10))