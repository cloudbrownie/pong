import pygame, time, random, sys
from data.imports.general import *
from data.imports.classes.particle import Particle
from data.imports.classes.pongball import PongBall
from data.imports.classes.block import Block
from pygame.locals import *

def ClassicMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay):

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
