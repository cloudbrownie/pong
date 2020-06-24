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
        self.move = [0, 0]
        self.hit = False
        self.inPlay = False
        self.out = False
        self.lastHit = None
        self.yBounce = False

    #this function checks if the ball has hit a block or not
    def collideTest(self, blocks):
        self.hit = False
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

        #if the ball hit a block, calculate the new x and y velocities based on where it hit the block
        if self.hit:
            yDist = hitBlock.rect.centery - self.rect.centery
            yDistNorm = yDist / (hitBlock.rect.h / 2)
            bounceAngle = yDistNorm * self.maxAngle
            self.xVel = self.vel * math.cos(bounceAngle) * hitBlock.bounce
            self.yVel = self.vel * math.sin(bounceAngle) * -1
            if abs(self.yVel) < 1:
                self.yVel += random.choice([-1, 1])
            
            
    #updates the ball every frame
    def update(self, hitSounds, display, blocks, dt):
        #only move the ball when the ball is in play
        if self.inPlay and not self.out:
            self.yBounce = False
            if self.rect.y <= 0:
                self.rect.top = 0
                self.yVel *= -1
                random.choice(hitSounds).play()
                self.yBounce = True
            elif self.rect.y + self.rect.h >= display.get_height():
                self.rect.bottom = display.get_height()
                self.yVel *= -1
                random.choice(hitSounds).play()
                self.yBounce = True
            self.move = [0, 0]
            self.move[0] += self.xVel * dt
            self.move[1] += self.yVel * dt
            self.collideTest(blocks)
        #draw the ball
        pygame.draw.circle(display, self.color, self.rect.center, self.radius)

    def reset(self, display, xDir):
        self.xVel = self.vel * xDir
        self.yVel = self.vel // 5
        self.out = False
        self.inPlay = True
        self.lastHit = None
        self.rect.center = (display.get_width() // 2, display.get_height() // 2)

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

    def aiUpdate(self, display, ball, dt, checkDist, tol, isRight, pause, otherBlock, centering):
        if not pause:
            if isRight:
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
                        else:
                            self.up = False
                            self.down = False
                        
                else:
                    self.up = False
                    self.down = False
            else:
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
                        
                else:
                    self.up = False
                    self.down = False
            self.update(display, dt)
        else:
            self.draw(display)
        
    

#functions
def genCollideParticles(x, y, color, amount, xVRange, yVRange, size):
    #generate a bunch of particles of ranging amount with ranging sizes and velocities
    particles = []
    for i in range(random.randint(amount[0], amount[1])):
        particles.append(Particle(x, y, random.randint(xVRange[0], xVRange[1]), random.randint(yVRange[0], yVRange[1]), random.randint(size[0], size[1]), color))
    return particles

def setVolumes(sounds, vol):
    for sound in sounds:
        sound.set_volume(vol)

def ballCrunch(sounds, playVol, delay):
    origVol = sounds[0].get_volume()
    setVolumes(sounds, playVol)
    for i in range(len(sounds)):
        random.choice(sounds).play()
        time.sleep(delay)
    setVolumes(sounds, origVol)

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
hitSounds = [pygame.mixer.Sound("data/sounds/hit.wav"), pygame.mixer.Sound("data/sounds/hit2.wav"), pygame.mixer.Sound("data/sounds/hit3.wav")]
ballSpeed = 60
ballRadius = 30
paddleSpeed = 25
xDir = random.choice([-1, 1])
maxVol = .3
minVol = .1
crunchDelay = .001
paddleHeight = 500
paddleWidth = 100

#font 
titleFont = pygame.font.Font("data/fonts/SGALSI.ttf", 400)
bigFont = pygame.font.Font("data/fonts/SGALSI.ttf", 100)

#main menu function
def main():
    global xDir

    #title
    titleSurface = titleFont.render("Pong Blitz", False, (249, 249, 249))
    titleSize = titleFont.size("Pong Blitz")
    titleCenter = (titleSize[0] // 2, titleSize[1] // 2)

    #caption
    captionSurface = bigFont.render("Press ENTER or RETURN to continue", False, (249, 249, 249))
    captionSize = bigFont.size("Press ENTER or RETURN to continue")
    captionCenter = (captionSize[0] // 2, captionSize[1] // 2)
    captionSurface.set_alpha(0)
    captionAlpha = 1
    captionConstant = 3

    #player select amount
    playerSelect = False
    playerSelectRect = pygame.Rect(0, 0, display.get_width() // 3, display.get_height() // 3)
    playerSelectRect.center = (display.get_width() // 2, display.get_height() // 2)
    
    selectScreen  = pygame.Surface((display.get_width(), display.get_height()))
    selectScreen.set_colorkey((0,0,0))
    pygame.draw.rect(selectScreen, (94, 124, 187), playerSelectRect)
    
    p1optSurf = bigFont.render("1 Player", False, (249, 249, 249))
    p1optSize = bigFont.size("1 Player")
    p1optCenter = (display.get_width() // 2 - p1optSize[0] // 2, display.get_height() // 2 - p1optSize[1])
    p1optRect = pygame.Rect(0, 0, p1optSize[0], p1optSize[1])
    p1optRect.center = (display.get_width() // 2, display.get_height() // 2 - p1optSize[1] // 2)
    selectScreen.blit(p1optSurf, (p1optCenter[0], p1optCenter[1]))

    p2optSurf = bigFont.render("2 Player", False, (249, 249, 249))
    p2optSize = bigFont.size("2 Player")
    p2optCenter = (display.get_width() // 2 - p2optSize[0] // 2, display.get_height() // 2)
    p2optRect = pygame.Rect(0, 0, p2optSize[0], p2optSize[1])
    p2optRect.center = (display.get_width() // 2, display.get_height() // 2 + p1optSize[1] // 2)
    selectScreen.blit(p2optSurf, (p2optCenter[0], p2optCenter[1]))

    #game setup
    particles = []
    prevTime = time.time()
    time.sleep(0.1)
    screenShake = [0, 0]
    setVolumes(hitSounds, maxVol)
    pause = False
    xRatio = screen.get_width() / display.get_width()
    yRatio = screen.get_height() / display.get_height()

    #create ball
    ball = PongBall(display.get_width() // 2, display.get_height() // 2, ballRadius, ballSpeed, (249, 249, 249), xDir)
    ball.inPlay = True
    ball.out = False
    hitTime = time.time()

    #create paddles
    blockOne = Block(150, display.get_height() // 2, 100, 500, paddleSpeed, (249, 249, 249), 1)
    blockTwo = Block(display.get_width() - 150, display.get_height() // 2, 100, 500, paddleSpeed, (249, 249, 249), -1)
    blocks = [blockOne, blockTwo]

    #dt
    prevTime = time.time()
    time.sleep(.001)

    #loop
    while True:

        #check events
        for event in pygame.event.get():
            #if window is closed, shutdown
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #if a key was pressed
            elif event.type == KEYDOWN:
                #closes window if escape pressed
                if event.key == K_ESCAPE:
                    if playerSelect:
                        playerSelect = False
                    else:
                        pygame.quit()
                        sys.exit()
                #starts the game
                elif event.key == K_RETURN:
                    if not playerSelect:
                        playerSelect = True
            elif event.type == MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                mousePos = (mx / xRatio, my / yRatio)
                if playerSelect:
                    if event.button == 1:
                        if p1optRect.collidepoint(mousePos):
                            game(1)
                        elif p2optRect.collidepoint(mousePos):
                            game(2)

        #dt, used to move everything at a constant 60 frames per second
        dt = (time.time() - prevTime) * 60
        prevTime = time.time()

        #referesh screen
        screen.fill((104, 134, 197))
        display.fill((104, 134, 197))

        #play the game in the background with two ais
        #update game elements
        ball.update(hitSounds, display, blocks, dt)

        #auto move paddles
        blockOne.aiUpdate(display, ball, dt, display.get_width() // 2, 2.5, True, False, blockTwo, True)
        blockTwo.aiUpdate(display, ball, dt, display.get_width() // 2, 2.5, False, False, blockOne, True)

        #create a particle at the balls location that slowly fades
        if not ball.out:
            particles.append(Particle(ball.rect.centerx, ball.rect.centery, 0, 0, ball.radius, ball.color))

        #check if the ball ever hit the top or bottom
        if not ball.out and ball.yBounce:
            particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))

        #update all particles
        for particle in particles:
            particle.update(display, dt)
            if particle.radius <= 1:
                particles.remove(particle)

        #if ball was hit, play sound and generate collision particles
        if ball.hit:
            hitTime = time.time()
            random.choice(hitSounds).play()
            particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))

        #checking if ball is out on right side
        if ball.rect.x >= display.get_width():
            if not ball.out:
                particles.extend(genCollideParticles(display.get_width(), ball.rect.centery, (255, 172, 183), (10, 15), (-20, 10), (-20, 20), (50, 100)))
                screenShake = [random.randint(5, 10), random.randint(5, 10)]
                shakeTime = time.time()
                ballCrunch(hitSounds, minVol, crunchDelay)
                xDir = 1
            ball.out = True

        #checking if ball is out on left side
        elif ball.rect.x + ball.rect.h <= 0:
            if not ball.out: 
                particles.extend(genCollideParticles(0, ball.rect.centery, (255, 172, 183), (10, 15), (10, 20), (-20, 20), (50, 100)))
                screenShake = [random.randint(5, 10), random.randint(5, 10)]
                shakeTime = time.time()
                ballCrunch(hitSounds, minVol, crunchDelay)
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

        if ball.out and len(particles) == 0:
            ball.reset(display, xDir)
            setVolumes(hitSounds, maxVol)

        #blit title and caption
        display.blit(titleSurface, (display.get_width() // 2 - titleCenter[0], display.get_height() // 2 - titleCenter[1]))
        display.blit(captionSurface, (display.get_width() // 2 - captionCenter[0], display.get_height() - display.get_height() // 6 - captionSize[1]))

        #fade caption in and out
        captionSurface.set_alpha(captionAlpha)
        if captionAlpha >= 200:
            captionAlpha = 200
            captionConstant *= -1
        elif captionAlpha <= 0:
            captionAlpha = 0
            captionConstant *= -1
        captionAlpha += captionConstant * dt

        #do the player select thing
        if playerSelect:
            display.blit(selectScreen, (0,0))

        #update screen
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.flip()
        
#selection screen function
def selectionScreen():
    pass

#game function
def game(players):
    global xDir, ballSpeed, score

    #game setup
    particles = []
    prevTime = time.time()
    time.sleep(0.1)
    screenShake = [0, 0]
    setVolumes(hitSounds, maxVol)
    pause = False

    #score
    pointSurface = bigFont.render(f"{score[0]} - {score[1]}", False, (249, 249, 249))
    pointSize = bigFont.size(f"{score[0]} - {score[1]}")
    pointCenter = (pointSize[0] // 2, pointSize[1] // 2)
    
    #gui
    gui = pygame.Surface((display.get_width(), display.get_height()))
    gui.set_colorkey((0,0,0))
    gui.blit(pointSurface, (gui.get_width() // 2 - pointCenter[0], 0 + pointCenter[1]))

    #pause screen
    pauseSurface = pygame.Surface((display.get_width(), display.get_height()))
    pauseSurface.set_alpha(100)

    #create ball
    ball = PongBall(display.get_width() // 2, display.get_height() // 2, ballRadius, ballSpeed, (249, 249, 249), xDir)
    ball.inPlay = True
    ball.out = False
    hitTime = time.time()

    #create paddles
    blockOne = Block(150, display.get_height() // 2, 100, 500, paddleSpeed, (249, 249, 249), 1)
    blockTwo = Block(display.get_width() - 150, display.get_height() // 2, 100, 500, paddleSpeed, (249, 249, 249), -1)
    p1Paddle = blockTwo
    blocks = [p1Paddle]
    if players == 2:
        p2Paddle = blockOne
        blocks.extend([p2Paddle])
    else:
        aiPaddle = blockOne
        blocks.extend([aiPaddle])


    #gameloop
    while True:

        #check the events
        for event in pygame.event.get():
            #if window is closed, shutdown
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #if key is pressed
            if event.type == KEYDOWN:
                #pause the game if not paused, exit to title if paused
                if event.key == K_ESCAPE:
                    if not pause:
                        pause = True
                        if players == 1:
                            aiPaddle.up = False
                            aiPaddle.down = False
                        ball.inPlay = False
                    else:
                        score = [0, 0]
                        main()
                #if paused resume, or if the ball was not hit for 10 secs it will restart when this is pressed
                if event.key == K_RETURN:
                    if not pause:
                        if time.time() - hitTime >= 10:
                            game()
                    if pause:
                        pause = False
                        ball.inPlay = True
                #only let the player move their block up and down if the ball is moving
                if not pause:
                    #move block up or down if up or down is pressed
                    if event.key == K_UP:
                        p1Paddle.up = True
                    elif event.key == K_DOWN:
                        p1Paddle.down = True
                    if players == 2:
                        if event.key == K_w:
                            p2Paddle.up = True
                        elif event.key == K_s:
                            p2Paddle.down = True
            #if key is released
            elif event.type == KEYUP:
                #if the up arrow is released
                if event.key == K_UP:
                    p1Paddle.up = False
                #if the down arrow is released
                elif event.key == K_DOWN:
                    p1Paddle.down = False
                if players == 2:
                    if event.key == K_w:
                        p2Paddle.up = False
                    elif event.key == K_s:
                        p2Paddle.down = False

        #everything moves at a constant 60 fps rate
        dt = (time.time() - prevTime) * 60
        prevTime = time.time()

        #refresh screen
        screen.fill((104, 134, 197))
        display.fill((104, 134, 197))

        #update game elements
        ball.update(hitSounds, display, blocks, dt)
        p1Paddle.update(display, dt)
        if players == 2:
            p2Paddle.update(display, dt)

        #auto move second block if it is 1 player
        if not pause and players == 1:
            aiPaddle.aiUpdate(display, ball, dt, display.get_width() // 2, 2, True, False, blockTwo, True)
        elif pause and players == 1:
            blockOne.aiUpdate(display, ball, dt, display.get_width() // 2, 2, True, True, blockTwo, True)
            

        #create a particle at the balls location that slowly fades
        if not pause and not ball.out:
            particles.append(Particle(ball.rect.centerx, ball.rect.centery, 0, 0, ball.radius, ball.color))

        #if ball hit ceiling or floor, gen some particles
        if not pause and ball.yBounce and not ball.out:
            particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))

        #update all particles
        for particle in particles:
            if not pause:
                particle.update(display, dt)
                if particle.radius <= 1:
                    particles.remove(particle)
            else:
                particle.draw(display)

        #if ball was hit, play sound and generate collision particles
        if not pause and ball.hit:
            hitTime = time.time()
            random.choice(hitSounds).play()
            particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))

        #checking if ball is out on right side
        if ball.rect.x >= display.get_width():
            if not ball.out:
                particles.extend(genCollideParticles(display.get_width(), ball.rect.centery, (255, 172, 183), (10, 15), (-20, 10), (-20, 20), (50, 100)))
                screenShake = [random.randint(5, 10), random.randint(5, 10)]
                shakeTime = time.time()
                ballCrunch(hitSounds, minVol, crunchDelay)
                score[0] += 1
                xDir = -1
            ball.out = True

        #checking if ball is out on left side
        elif ball.rect.x + ball.rect.h <= 0:
            if not ball.out: 
                particles.extend(genCollideParticles(0, ball.rect.centery, (255, 172, 183), (10, 15), (10, 20), (-20, 20), (50, 100)))
                screenShake = [random.randint(5, 10), random.randint(5, 10)]
                shakeTime = time.time()
                ballCrunch(hitSounds, minVol, crunchDelay)
                score[1] += 1
                xDir = 1
            ball.out = True
        
        #decreasing screen shake values
        if screenShake != [0, 0]:
            if time.time() - shakeTime > .1:
                shakeTime = time.time()
                if screenShake[0] > 0:
                    screenShake[0] -= 1
                if screenShake[1] > 0:
                    screenShake[1] -= 1

        #reset game
        if ball.out and screenShake == [0, 0] and len(particles) == 0 and not pause:
            ball.reset(display, xDir)
            setVolumes(hitSounds, maxVol)
            #re render score
            pointSurface = bigFont.render(f"{score[0]} - {score[1]}", False, (249, 249, 249))
            pointSize = bigFont.size(f"{score[0]} - {score[1]}")
            pointCenter = (pointSize[0] // 2, pointSize[1] // 2)
            #re render gui
            gui = pygame.Surface((display.get_width(), display.get_height()))
            gui.set_colorkey((0,0,0))
            gui.blit(pointSurface, (gui.get_width() // 2 - pointCenter[0], 0 + pointCenter[1]))

            
        #update gui
        display.blit(gui, (0,0))

        #update screen and pause
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0 - screenShake[0] * random.choice([-1, 1]), 0 - screenShake[1] * random.choice([-1, 1])))
        if pause:
            screen.blit(pygame.transform.scale(pauseSurface, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.flip()

main()
    
