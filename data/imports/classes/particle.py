import pygame

class Particle:
    def __init__(self, x, y, xVel, yVel, radius, color):
        self.x = x
        self.y = y
        self.xVel = xVel
        self.yVel = yVel
        self.radius = radius
        self.color = color

    #updates the particle every frame
    def update(self, display, dt):
        #move the particle using its velocities
        self.x += self.xVel * dt
        self.y += self.yVel * dt
        #the particle's radius is reduced each frame
        self.radius -= 1 * dt
        #draw the particle
        self.draw(display)

    def draw(self, display):
        pygame.draw.circle(display, self.color, (self.x, self.y), self.radius)
