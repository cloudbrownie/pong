import pygame, time, random, sys
from data.imports.general import *
from data.imports.classes.particle import Particle
from data.imports.classes.pongball import PongBall
from data.imports.classes.block import Block
from pygame.locals import *

#mode specific function
def genNewBall(center, xVel, yVel, ballInfo):
    ball = PongBall(center[0], center[1], ballInfo[0], ballInfo[1], ballInfo[2], ballInfo[3])
    ball.xVel = xVel
    ball.yVel = yVel * 1.5
    return ball

def BurstMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay, mute, particleEffects):

    #unpack params
    maxVol = vols[0]
    minVol = vols[1]
    ballSpeed = ballInfo[0]
    ballRadius = ballInfo[1]
    xDir = ballInfo[2]

    #game setup
    particles = []
    prevTime = time.time()
    time.sleep(0.1)
    setVolumes(hitSounds, maxVol)
    pause = False

    #score
    pointSurface = bigFont.render(f"{score[0]} - {score[1]}", False, (249, 249, 249))
    pointSize = bigFont.size(f"{score[0]} - {score[1]}")
    pointCenter = pointSize[0] // 2, pointSize[1] // 2

    #gui
    gui = pygame.Surface((display.get_width(), display.get_height()))
    gui.set_colorkey((0,0,0))
    gui.blit(pointSurface, (gui.get_width() // 2 - pointCenter[0], 0 + pointCenter[1]))

    #pause screen
    pauseSurface = pygame.Surface((display.get_width(), display.get_height()))
    pauseSurface.set_alpha(100)

    #create ball
    balls = [PongBall(display.get_width() // 2, display.get_height() // 2, ballRadius, ballSpeed, (255, 172, 183), xDir)]

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
    running = True
    while running:

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
                        running = False
                #if paused resume, or if the ball was not hit for 10 secs it will restart when this is pressed
                if event.key == K_RETURN:
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
        for ball in balls:
            if not pause:
                ball.update( display, blocks, dt)
            else:
                ball.draw(display)
        p1Paddle.update(display, dt)
        if players == 2:
            p2Paddle.update(display, dt)

        #auto move second block if it is 1 player
        if len(balls) > 0 and players == 1:
            if not pause:
                if balls[0].out:
                    aiPaddle.aiUpdate(display, balls[1], dt, display.get_width() // 2, 2, blockTwo, True)
                else:
                    aiPaddle.aiUpdate(display, balls[0], dt, display.get_width() // 2, 2, blockTwo, True)
            else:
                aiPaddle.draw(display)

        #update every ball on screen
        for ball in balls:
            while len(particles) >= 50:
                particles.pop(0)

            if not pause:
                if not ball.out:
                    if particleEffects:
                        particles.append(Particle(ball.rect.centerx, ball.rect.centery, 0, 0, ball.radius, ball.color))
                if ball.hit: #if the ball hit anything
                    if particleEffects:
                        particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))
                    if ball.color == balls[0].color:
                        #only create a new ball if the red ball collides with something
                        if not mute:
                            random.choice(hitSounds).play()
                        balls.append(genNewBall(ball.rect.center, ball.xVel, ball.yVel, (ball.radius, ball.vel, (249, 249, 249), xDir)))

            #checking if ball is out on right side
            if ball.rect.x >= display.get_width():
                if not ball.out:
                    score[0] += 1
                    xDir = -1
                ball.out = True

            #checking if ball is out on left side
            elif ball.rect.right <= 0:
                if not ball.out:
                    score[1] += 1
                    xDir = 1
                ball.out = True

            #check if the ball goes out
            if ball.out and not pause:
                if ball.color != balls[0].color:
                    balls.pop(balls.index(ball))
                if not mute:
                    setVolumes(hitSounds, maxVol)
                #re render score
                pointSurface = bigFont.render(f"{score[0]} - {score[1]}", False, (249, 249, 249))
                pointSize = bigFont.size(f"{score[0]} - {score[1]}")
                pointCenter = pointSize[0] // 2, pointSize[1] // 2
                #re render gui
                gui.fill((0,0,0))
                gui.blit(pointSurface, (gui.get_width() // 2 - pointCenter[0], 0 + pointCenter[1]))

        #update all particles
        for particle in particles:
            if not pause:
                particle.update(display, dt)
                if particle.radius <= 1:
                    particles.remove(particle)
            else:
                particle.draw(display)

        #if the spawn ball is out, wait for all balls to be cleared and then reset
        if balls[0].out and len(balls) < 2:
            balls[0].reset(display, xDir)

        #update gui
        display.blit(gui, (0,0))

        #update screen and pause
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0, 0))
        if pause:
            screen.blit(pygame.transform.scale(pauseSurface, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.flip()
