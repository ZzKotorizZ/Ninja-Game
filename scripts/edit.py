import pygame
class Score:
    def __init__(self, score):
        self.score = score
        
    def update(self, score):
        self.score = score
    def render(self, surf):
        font = pygame.font.Font(None, 36)
        text = font.render("Score: " + str(self.score), 1, (255, 255, 255))
        textpos = text.get_rect(centerx = surf.get_width() / 2)
        surf.blit(text, textpos)