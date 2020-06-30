import pygame, math, random

class EffectBubble:
    def __init__(self, x, y, radius, vel, effect):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (242, 163, 101)
        self.vel = vel
        self.effect = effect
        self.rect = pygame.Rect(0, 0, radius*2, radius*2)
        self.rect.center = (x, y)
        self.out = False

    def draw(self, display):
        pygame.draw.circle(display, self.color, self.rect.center, self.radius)

    def update(self, display, dt):
        self.rect.centery += self.vel * dt
        if self.rect.top == display.get_height():
            self.out = True
        self.draw(display)
