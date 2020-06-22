#imports
import pygame
import random
import time
import math
from pygame.locals import *
import sys

#classes
class Particle:
    def __init__(self, x, y, xVel, yVel, radius, color):
        self.x = x
        self.y = y
        self.xVel = xVel
        self.yVel = yVel
        self.radius = radius
        self.color = color

    def update(self, display, dt):
        self.x += self.xVel * dt
        self.y += self.yVel * dt
        self.radius -= 1 * dt
        pygame.draw.circle(display, self.color, (self.x, self.y), self.radius)

class PongBall:
    def __init__(self, x, y, radius, vel, color, xDir):
        self.vel = vel
        self.xVel = vel * xDir
        self.yVel = vel // 10
        self.maxAngle = math.pi / 4
        self.radius = radius
        self.rect = pygame.Rect(0, 0, radius*2, radius*2)
        self.rect.center = (x, y)
        self.color = color
        self.move = [0, 0]
        self.hit = False
        self.inPlay = False
        self.out = False

    def collideTest(self, blocks):
        self.hit = False
        hitBlock = None
        self.rect.centerx += self.move[0]
        for block in blocks:
            if self.rect.colliderect(block.rect):
                self.hit = True
                hitBlock = block
                
                if self.move[0] > 0:
                    self.rect.right = block.rect.left
                elif self.move[0] < 0:
                    self.rect.left = block.rect.right
                                    
        self.rect.centery += self.move[1]
        for block in blocks:
            if self.rect.colliderect(block.rect):
                self.hit = True
                hitBlock = block
                
                if self.move[1] > 0:
                    self.rect.bottom = block.rect.top
                elif self.move[1] < 0:
                    self.rect.top = block.rect.bottom

        if self.hit:
            yDist = hitBlock.rect.centery - self.rect.centery
            yDistNorm = yDist / (hitBlock.rect.h / 2)
            bounceAngle = yDistNorm * self.maxAngle
            self.xVel = self.vel * math.cos(bounceAngle) * hitBlock.bounce
            self.yVel = self.vel * math.sin(bounceAngle) * -1
            

    def update(self, display, blocks, dt):
        if self.inPlay and not self.out:
            if self.rect.y <= 0:
                self.rect.top = 0
                self.yVel *= -1
            elif self.rect.y + self.rect.h >= display.get_height():
                self.rect.bottom = display.get_height()
                self.yVel *= -1
            self.move = [0, 0]
            self.move[0] += self.xVel * dt
            self.move[1] += self.yVel * dt
            self.collideTest(blocks)
        pygame.draw.circle(display, self.color, self.rect.center, self.radius)

class Block:
    def __init__(self, x, y, w, h, vel, color, bounce):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.vel = vel
        self.color = color
        self.up = False
        self.down = False
        self.bounce = bounce

    def update(self, display, dt):
        if self.up:
            self.rect.centery -= self.vel * dt
        if self.down:
            self.rect.centery += self.vel * dt
        if self.rect.y <= 0:
            self.rect.y = 0
        elif self.rect.bottom >= display.get_height():
            self.rect.bottom = display.get_height()
        pygame.draw.rect(display, self.color, self.rect)

#functions
def genCollideParticles(x, y, color, amount, xVRange, yVRange, size):
    particles = []
    for i in range(random.randint(amount[0], amount[1])):
        particles.append(Particle(x, y, random.randint(xVRange[0], xVRange[1]), random.randint(yVRange[0], yVRange[1]), random.randint(size[0], size[1]), color))
    return particles


#window setup
pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode(size=(1200, 700))
display = pygame.Surface((screen.get_width()*2, screen.get_height()*2))

#caption and icon
pygame.display.set_caption("Pong")
icon = pygame.Surface((32, 32))
pygame.draw.circle(icon, (249, 249, 249), (16, 16), 16)
icon.set_colorkey((0,0,0))
pygame.display.set_icon(icon)

#global vars
score = [0, 0]
hitSound = pygame.mixer.Sound("data/sounds/hit.wav")
ballSpeed = 50
ballRadius = 30
paddleSpeed = 20
xDir = random.choice([-1, 1])

#font 
titleFont = pygame.font.Font("data/fonts/OpenSans-Regular.ttf", 400)
bigFont = pygame.font.Font("data/fonts/OpenSans-Regular.ttf", 100)

#main menu function
def main():
    global score

    #title
    titleSurface = titleFont.render("Pong", False, (249, 249, 249))
    titleSize = titleFont.size("Pong")
    titleCenter = (titleSize[0] // 2, titleSize[1] // 2)

    #reset score
    score = [0, 0]

    #loop
    while True:

        #check events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_RETURN:
                    game()

        #referesh screen
        screen.fill((104, 134, 197))
        display.fill((104, 134, 197))

        #blit title
        display.blit(titleSurface, (display.get_width() // 2 - titleCenter[0], display.get_height() // 2 - titleCenter[1]))

        #update screen
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.update()

#game function
def game():
    global xDir, ballSpeed

    #game setup
    particles = []
    prevTime = time.time()
    time.sleep(0.1)
    screenShake = [0, 0]
    hitSound.set_volume(.3)

    #score
    scoreSurface = bigFont.render("Score", False, (249, 249, 249))
    scoreSize = bigFont.size("Score")
    scoreCenter = (scoreSize[0] // 2, scoreSize[1] // 2)
    pointSurface = bigFont.render(f"{score[0]} - {score[1]}", False, (249, 249, 249))
    pointSize = bigFont.size(f"{score[0]} - {score[1]}")
    pointCenter = (pointSize[0] // 2, pointSize[1] // 2)
    
    #gui
    gui = pygame.Surface((display.get_width(), display.get_height()))
    gui.set_colorkey((0,0,0))
    gui.blit(scoreSurface, (gui.get_width() // 2 - scoreCenter[0], 0 + scoreCenter[1]))
    gui.blit(pointSurface, (gui.get_width() // 2 - pointCenter[0], 0 + scoreCenter[1] * 2 + pointCenter[1]))

    #create ball
    ball = PongBall(display.get_width() // 2, display.get_height() // 2, ballRadius, ballSpeed, (249, 249, 249), xDir)
    ball.inPlay = True
    hitTime = time.time()

    #create paddles
    blockOne = Block(100, display.get_height() // 2, 75, 500, paddleSpeed, (249, 249, 249), 1)
    blockTwo = Block(display.get_width() - 100, display.get_height() // 2, 75, 500, paddleSpeed, (249, 249, 249), -1)
    blocks = [blockOne, blockTwo]

    #gameloop
    while True:

        #check the events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    main()
                if not ball.inPlay:
                    hitTime = time.time()
                    ball.inPlay = True
                    
                if event.key == K_RETURN:
                    if time.time() - hitTime >= 10:
                        game()

                if not ball.out:
                    if event.key == K_UP:
                        blockOne.up = True
                    elif event.key == K_DOWN:
                        blockOne.down = True
            elif event.type == KEYUP:
                if event.key == K_UP:
                    blockOne.up = False
                elif event.key == K_DOWN:
                    blockOne.down = False

        #everything moves at a constant 60 fps rate
        dt = (time.time() - prevTime) * 60
        prevTime = time.time()

        #refresh screen
        screen.fill((104, 134, 197))
        display.fill((104, 134, 197))

        #update game elements
        ball.update(display, blocks, dt)
        blockOne.update(display, dt)

        #auto move second block
        if not ball.out:
            checkDist = display.get_width() // 2
            if ball.rect.centerx >= checkDist:
                yDist = blockTwo.rect.centery - ball.rect.centery
                if yDist > 0:
                    blockTwo.up = True
                    blockTwo.down = False
                elif yDist < 0:
                    blockTwo.down = True
                    blockTwo.up = False
            else:
                blockTwo.up = False
                blockTwo.down = False
                
        blockTwo.update(display, dt)

        #create a particle at the balls location that slowly fades
        if not ball.out:
            particles.append(Particle(ball.rect.centerx, ball.rect.centery, 0, 0, ball.radius, ball.color))

        #update all particles
        for particle in particles:
            particle.update(display, dt)
            if particle.radius <= 1:
                particles.remove(particle)

        #if ball was hit, play sound and generate collision particles
        if ball.hit:
            hitTime = time.time()
            hitSound.play()
            particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))

        #check if ball hasnt been in too long of a time frame, then game resets
        if ball.inPlay:
            if time.time() - hitTime >= 10:
                if ball.rect.left >= blockTwo.rect.right or ball.rect.right <= blockOne.rect.left:
                    game()

        #checking if ball is out on right side
        if ball.rect.x >= display.get_width():
            if not ball.out:
                particles.extend(genCollideParticles(display.get_width(), ball.rect.centery, (255, 172, 183), (10, 15), (-20, 10), (-20, 20), (50, 100)))
                screenShake = [random.randint(5, 10), random.randint(5, 10)]
                shakeTime = time.time()
                hitSound.set_volume(.1)
                for i in range(random.randint(5, 10)):
                    hitSound.play()
                    time.sleep(.001)
                score[0] += 1
                xDir = 1
            ball.out = True

        #checking if ball is out on left side
        elif ball.rect.x + ball.rect.h <= 0:
            if not ball.out: 
                particles.extend(genCollideParticles(0, ball.rect.centery, (255, 172, 183), (10, 15), (10, 20), (-20, 20), (50, 100)))
                screenShake = [random.randint(5, 10), random.randint(5, 10)]
                shakeTime = time.time()
                hitSound.set_volume(.1)
                for i in range(random.randint(5, 10)):
                    hitSound.play()
                    time.sleep(.001)
                score[1] += 1
                xDir = -1
            ball.out = True
        
        #decreasing screen shake values
        if screenShake != [0, 0]:
            if time.time() - shakeTime > .1:
                shakeTime = time.time()
                if screenShake[0] > 0:
                    screenShake[0] -= 1
                if screenShake[1] > 0:
                    screenShake[1] -= 1

        if ball.out and screenShake == [0, 0] and len(particles) == 0:
            game()

        #update gui
        display.blit(gui, (0,0))

        #update screen
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0 - screenShake[0] * random.choice([-1, 1]), 0 - screenShake[1] * random.choice([-1, 1])))
        pygame.display.update()

main()
    
