import pygame

class Block:
    def __init__(self, x, y, w, h, vel, color, bounce):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.vel = vel
        self.color = color
        self.up = False
        self.down = False
        self.bounce = bounce

    def draw(self, display):
        pygame.draw.rect(display, self.color, self.rect)

    def update(self, display, dt):
        #move the block if it is being moved
        if self.up:
            self.rect.centery -= self.vel * dt
        if self.down:
            self.rect.centery += self.vel * dt
        #make sure that the block doesnt go off screen to the top or bottom
        if self.rect.y <= 0:
            self.rect.y = 0
        elif self.rect.bottom >= display.get_height():
            self.rect.bottom = display.get_height()
        #draw the block
        self.draw(display)

    def aiUpdate(self, display, ball, dt, checkDist, tol, otherBlock, centering):
        isRight = False
        if self.rect.centerx > display.get_width() // 2:
            isRight = True
        if isRight:
            self.up = False
            self.down = False
            if not ball.out:
                if ball.rect.centerx >= checkDist and (ball.lastHit == otherBlock or ball.lastHit == None):
                    yDist = self.rect.centery - ball.rect.centery
                    if yDist > ball.radius * tol:
                        self.up = True
                        self.down = False
                    elif yDist < -ball.radius * tol:
                        self.down = True
                        self.up = False
                elif centering:
                    if self.rect.centery >= display.get_height() // 2 + self.vel:
                        self.up = True
                        self.down = False
                    elif self.rect.centery <= display.get_height() // 2 - self.vel:
                        self.up = False
                        self.down = True
        else:
            self.up = False
            self.down = False
            if not ball.out:
                if ball.rect.centerx <= checkDist and (ball.lastHit == otherBlock or ball.lastHit == None):
                    yDist = self.rect.centery - ball.rect.centery
                    if yDist > ball.radius * tol:
                        self.up = True
                        self.down = False
                    elif yDist < -ball.radius * tol:
                        self.down = True
                        self.up = False
                elif centering:
                    if self.rect.centery >= display.get_height() // 2 + self.vel:
                        self.up = True
                        self.down = False
                    elif self.rect.centery <= display.get_height() // 2 - self.vel:
                        self.up = False
                        self.down = True
        self.update(display, dt)
