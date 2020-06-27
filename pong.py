#imports
import pygame
import random
import time
import math
from pygame.locals import *
from data.imports.classes.particle import Particle
from data.imports.classes.pongball import PongBall
from data.imports.classes.block import Block
from data.imports.classes.gamecard import GameCard
from data.imports.modes.classic import ClassicMode
from data.imports.modes.burst import BurstMode
from data.imports.general import *
import sys

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
maxVol = 1
minVol = .5
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
                #can use buttons to choose player amount
                if playerSelect:
                    if event.key == K_1:
                        selectionScreen(1)
                    elif event.key == K_2:
                        selectionScreen(2)

            elif event.type == MOUSEBUTTONDOWN:
                if playerSelect:
                    mx, my = pygame.mouse.get_pos()
                    mousePos = (mx / xRatio, my / yRatio)
                    if event.button == 1:
                        if p1optRect.collidepoint(mousePos):
                            selectionScreen(1)
                        elif p2optRect.collidepoint(mousePos):
                            selectionScreen(2)
                else:
                    playerSelect = True

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
def selectionScreen(players):


    #setup
    xRatio = screen.get_width() / display.get_width()
    yRatio = screen.get_height() / display.get_height()

    #gui
    gui = pygame.Surface((display.get_width(), display.get_height()))
    gui.set_colorkey((0,0,0))

    #left arrow outside
    loVerts = ((gui.get_width() // 4 - 20, 6 * gui.get_height() // 7),
              (gui.get_width() // 3 + 15, 6 * gui.get_height() // 7 - 120),
              (gui.get_width() // 3 + 15, 6 * gui.get_height() // 7 + 120))
    
    #left arrow inside
    lVerts = ((gui.get_width() // 4, 6 * gui.get_height() // 7),
              (gui.get_width() // 3, 6 * gui.get_height() // 7 - 100),
              (gui.get_width() // 3, 6 * gui.get_height() // 7 + 100))

    #right arrow outside
    roVerts = ((3 * gui.get_width() // 4 + 20, 6 * gui.get_height() // 7),
              (2 * gui.get_width() // 3 - 15, 6 * gui.get_height() // 7 - 120),
              (2 * gui.get_width() // 3 - 15, 6 * gui.get_height() // 7 + 120))

    #right arrow inside
    rVerts = ((3 * gui.get_width() // 4, 6 * gui.get_height() // 7),
              (2 * gui.get_width() // 3, 6 * gui.get_height() // 7 - 100),
              (2 * gui.get_width() // 3, 6 * gui.get_height() // 7 + 100))

    #back button outside
    boVerts = ((0,0),
              (0, gui.get_height() // 8 + 10),
              (gui.get_width() // 4 + 10, gui.get_height() // 8 + 10),
              (gui.get_width() // 3 + 20, 0))

    #back button inside
    bVerts = ((0,0),
              (0, gui.get_height() // 8),
              (gui.get_width() // 4, gui.get_height() // 8),
              (gui.get_width() // 3, 0))

    #settings button outside
    soVerts = ((gui.get_width(), 0),
              (gui.get_width(), gui.get_height() // 8 + 10),
              (3 * gui.get_width() // 4 - 10, gui.get_height() // 8 + 10),
              (2 * gui.get_width() // 3 - 20, 0))
    
    #settings button inside
    sVerts = ((gui.get_width(), 0),
              (gui.get_width(), gui.get_height() // 8),
              (3 * gui.get_width() // 4, gui.get_height() // 8),
              (2 * gui.get_width() // 3, 0))

    #card sizes
    cardSizes = ((gui.get_width() // 4, gui.get_height() // 2),
                 (gui.get_width() // 7, gui.get_height() //3),
                 (gui.get_width() // 8, gui.get_height() // 4))

    #card centers
    cardCenters = {"farLeft":(gui.get_width() // 9, gui.get_height() // 2),
                   "left":(gui.get_width() // 4, gui.get_height() // 2),
                   "middle":(gui.get_width() // 2, gui.get_height() // 2),
                   "right":(3 * gui.get_width() // 4, gui.get_height() // 2),
                   "farRight":(8 * gui.get_width() // 9, gui.get_height() // 2)}

    #draw arrows and buttons
    lRect = pygame.draw.polygon(gui, (94, 124, 187), lVerts)
    rRect = pygame.draw.polygon(gui, (94, 124, 187), rVerts)
    bRect = pygame.draw.polygon(gui, (94, 124, 187), bVerts)
    sRect = pygame.draw.polygon(gui, (94, 124, 187), sVerts)

    #gui mask for pixel perfect collisions
    guiMask = pygame.mask.from_surface(gui)

    #card objects for gui
    classicCard = GameCard(cardCenters["middle"], cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Classic",
                           pygame.image.load("data/textures/cards/classic.png"), "")

    card1 = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Burst",
                           pygame.image.load("data/textures/cards/classic.png"), "")
    
    card2 = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Rain",
                           pygame.image.load("data/textures/cards/classic.png"), "")
                           
    card3 = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Swap",
                           pygame.image.load("data/textures/cards/classic.png"), "")
    
    card4 = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Rotation",
                           pygame.image.load("data/textures/cards/classic.png"), "")

    card5 = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Blitz",
                           pygame.image.load("data/textures/cards/classic.png"), "")

    #adding cards and matching with game mode list, also centering everything where they should be
    gameCards = [classicCard, card1, card2, card3, card4, card5]
    gameModes = ["classic", "burst", 3, 4, 5, 6]
    indices = [-2, -1, 0, 1, 2]
    gameCards[indices[0]].reposition(cardCenters["farLeft"])
    gameCards[indices[1]].reposition(cardCenters["left"])
    gameCards[indices[2]].reposition(cardCenters["middle"])
    gameCards[indices[3]].reposition(cardCenters["right"])
    gameCards[indices[4]].reposition(cardCenters["farRight"])
    cardSwap = False

    #if the player has selected something
    selected = None

    #text surfaces for back and settings
    backSurf = bigFont.render("Back", False, (249, 249, 249))
    backSurfRect = pygame.Rect(0,0,backSurf.get_width(),backSurf.get_height())
    backSurfRect.center = (bVerts[2][0] // 2, bVerts[2][1] // 2)

    settingsSurf = bigFont.render("Settings", False, (249, 249, 249))
    settingsSurfRect = pygame.Rect(0,0,settingsSurf.get_width(),settingsSurf.get_height())
    settingsSurfRect.center = (sVerts[2][0] + (sVerts[1][0] - sVerts[2][0]) // 2, sVerts[2][1] // 2)
        
    #selection loop
    running = True
    while running:

        #get mouse positioning
        mx, my = pygame.mouse.get_pos()
        mousePos = (int(mx / xRatio), int(my / yRatio))

        #resetting game value as well as score
        score = [0, 0]
        selected = None
    
        #execute events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if lRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                        for i in range(len(indices)):
                            indices[i] -= 1
                        cardSwap = True
                    elif rRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                        for i in range(len(indices)):
                            indices[i] += 1
                        cardSwap = True
                    elif bRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                        running = False
                    elif sRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                        print("settings")
                    else:
                        for card in gameCards:
                            if card.normalRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                                selected = gameModes[indices[2]]

        #check if the player selected a game
        if selected != None:
            if selected == "classic":
                vols = (maxVol, minVol)
                ballInfo = (ballSpeed, ballRadius, xDir)
                ClassicMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay)
            elif selected == "burst":
                vols = (maxVol, minVol)
                ballInfo = (ballSpeed, ballRadius, xDir)
                BurstMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay)
                                        
        #fill display
        display.fill((104, 134, 197))

        #make sure index doesn't go out of bounds
        if indices[2] >= len(gameModes):
            indices[2] = 0
        elif indices[2] < 0:
            indices[2] = len(gameModes)-1

        #reposition game cards
        if cardSwap:
            for i in range(len(indices)):
                if indices[i] >= len(gameModes):
                    indices[i] = 0
                elif indices[i] < -len(gameModes):
                    indices[i] = len(gameModes) - 1
                
            gameCards[indices[0]].reposition(cardCenters["farLeft"])
            gameCards[indices[1]].reposition(cardCenters["left"])
            gameCards[indices[2]].reposition(cardCenters["middle"])
            gameCards[indices[3]].reposition(cardCenters["right"])
            gameCards[indices[4]].reposition(cardCenters["farRight"])
            cardSwap = False
            

        #clear gui
        gui.fill((0,0,0))

        #draw outlines if mouse hovers over
        if lRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
            pygame.draw.polygon(gui, (249, 249, 249), loVerts)
        elif rRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
            pygame.draw.polygon(gui, (249, 249, 249), roVerts)
        elif bRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
            pygame.draw.polygon(gui, (249, 249, 249), boVerts)
        elif sRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
            pygame.draw.polygon(gui, (249, 249, 249), soVerts)

        #draw cards
        for i in range(len(indices)):
            gameCards[indices[i]].draw(gui, i)

        #draw arrows and buttons
        lRect = pygame.draw.polygon(gui, (94, 124, 187), lVerts)
        rRect = pygame.draw.polygon(gui, (94, 124, 187), rVerts)
        bRect = pygame.draw.polygon(gui, (94, 124, 187), bVerts)
        sRect = pygame.draw.polygon(gui, (94, 124, 187), sVerts)

        #draw text
        gui.blit(backSurf, backSurfRect)
        gui.blit(settingsSurf, settingsSurfRect)

        #gui mask for pixel perfect collisions
        guiMask = pygame.mask.from_surface(gui)

        #draw gui to display
        display.blit(gui, (0,0))

        #update the screen
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.flip()

main()
    
