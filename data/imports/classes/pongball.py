import pygame, math, random

class PongBall:
    def __init__(self, x, y, radius, vel, color, xDir):
        self.vel = vel
        self.xVel = vel * xDir
        self.yVel = vel // 5
        self.maxAngle = math.pi / 4
        self.radius = radius
        self.rect = pygame.Rect(0, 0, radius*2, radius*2)
        self.rect.center = (x, y)
        self.color = color
        self.origColor = color
        self.move = [0, 0]
        self.hit = False
        self.out = False
        self.lastHit = None
        self.effects = []

    #this function checks if the ball has hit a block or not
    def collideTest(self, blocks, bubbles=None):
        hitBlock = None
        #move the ball in the x direction first and check if it hits a block
        self.rect.centerx += self.move[0]
        for block in blocks:
            if self.rect.colliderect(block.rect):
                #remember which block it hits
                hitBlock = block
                #only let the ball hit the block once, this makes sure a block cant double hit
                if self.lastHit != hitBlock:
                    self.lastHit = hitBlock
                    self.hit = True
                    #makes puts the side of the ball to the correct side of the block it hit
                    if self.move[0] > 0:
                        self.rect.right = block.rect.left
                    elif self.move[0] < 0:
                        self.rect.left = block.rect.right

        #repeat steps above, but for the y direction
        self.rect.centery += self.move[1]
        for block in blocks:
            if self.rect.colliderect(block.rect):
                hitBlock = block
                if self.lastHit != hitBlock:
                    self.lastHit = hitBlock
                    self.hit = True

                    if self.move[1] > 0:
                        self.rect.bottom = block.rect.top
                    elif self.move[1] < 0:
                        self.rect.top = block.rect.bottom

        #used for the rain gamemode to check collisions with the bubbles
        if bubbles != None:
            for bubble in bubbles:
                if self.rect.colliderect(bubble.rect):
                    self.effects.append(bubble.effect)
                    self.color = bubble.color
                    bubble.out = True

        #if the ball hit a block, calculate the new x and y velocities based on where it hit the block
        if hitBlock != None:
            yDist = hitBlock.rect.centery - self.rect.centery
            yDistNorm = yDist / (hitBlock.rect.h / 2)
            bounceAngle = yDistNorm * self.maxAngle
            self.xVel = self.vel * math.cos(bounceAngle) * hitBlock.bounce
            self.yVel = self.vel * math.sin(bounceAngle) * -1
            if abs(self.yVel) < 1:
                self.yVel += random.choice([-1, 1])

    #draw the pongball
    def draw(self, display):
        pygame.draw.circle(display, self.color, self.rect.center, self.radius)

    #updates the ball every frame
    def update(self, display, blocks, dt):
        #only move the ball when the ball is in play
        self.hit = False
        if not self.out:
            if self.rect.top <= 0:
                self.rect.top = 0
                self.yVel *= -1
                self.hit = True
            elif self.rect.bottom >= display.get_height():
                self.rect.bottom = display.get_height()
                self.yVel *= -1
                self.hit = True
            self.move = [0, 0]
            self.move[0] += self.xVel * dt
            self.move[1] += self.yVel * dt
            self.collideTest(blocks)
        #draw the ball
        self.draw(display)

    #reset the ball to the center of the field
    def reset(self, display, xDir):
        self.xVel = self.vel * xDir
        self.yVel = self.vel // 5
        self.out = False
        self.lastHit = None
        self.rect.center = (display.get_width() // 2, display.get_height() // 2)
        self.effects = []
        self.color = self.origColor

    #function to update pongball in the rain mode
    def rainUpdate(self, display, blocks, bubbles, dt):
        #only move the ball when the ball is in play
        self.hit = False
        if not self.out:
            if self.rect.y <= 0:
                self.rect.top = 0
                self.yVel *= -1
                self.hit = True
            elif self.rect.y + self.rect.h >= display.get_height():
                self.rect.bottom = display.get_height()
                self.yVel *= -1
                self.hit = True
            self.move = [0, 0]
            self.move[0] += self.xVel * dt
            self.move[1] += self.yVel * dt
            self.collideTest(blocks, bubbles=bubbles)
        #draw the balls
        self.draw(display)
