#imports
import pygame, random, time, math, sys, json
from pygame.locals import *
from data.imports.classes.particle import Particle
from data.imports.classes.pongball import PongBall
from data.imports.classes.block import Block
from data.imports.classes.gamecard import GameCard
from data.imports.classes.scrollbar import HorizScrollBar
from data.imports.modes.classic import ClassicMode
from data.imports.modes.burst import BurstMode
from data.imports.modes.rain import RainMode
from data.imports.modes.swap import SwapMode
from data.imports.general import *

#extracting settings from json file
with open("data/settings/settings.json", "r") as readJson:
    settingsData = json.load(readJson)

#window setup
pygame.init()
pygame.mixer.init()
pygame.font.init()
flags = 0
if settingsData["fullscreen"]:
    flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
screen = pygame.display.set_mode(size=(1200, 700), flags=flags)
display = pygame.Surface((screen.get_width()*2, screen.get_height()*2))

#caption and icon
pygame.display.set_caption("Pong")
icon = pygame.Surface((32, 32))
pygame.draw.circle(icon, (249, 249, 249), (16, 16), 10)
icon.set_colorkey((0,0,0))
pygame.display.set_icon(icon)

#global vars
score = [0, 0]
hitSounds = [pygame.mixer.Sound("data/sounds/hit.wav"), pygame.mixer.Sound("data/sounds/hit2.wav"), pygame.mixer.Sound("data/sounds/hit3.wav")]
ballSpeed = 60
ballRadius = 30
paddleSpeed = 25
xDir = random.choice([-1, 1])
maxVol = settingsData["volume"]
minVol = maxVol - .2
crunchDelay = .001
paddleHeight = 500
paddleWidth = 100

#font
titleFont = pygame.font.Font("data/fonts/SGALSI.ttf", 400)
bigFont = pygame.font.Font("data/fonts/SGALSI.ttf", 100)
smallFont = pygame.font.Font("data/fonts/SGALSI.ttf", 75)

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

    #game setup
    particles = []
    prevTime = time.time()
    time.sleep(0.1)
    setVolumes(hitSounds, maxVol)
    pause = False
    xRatio = screen.get_width() / display.get_width()
    yRatio = screen.get_height() / display.get_height()

    #create ball
    ball = PongBall(display.get_width() // 2, display.get_height() // 2, ballRadius, ballSpeed, (249, 249, 249), xDir)

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
                    pygame.quit()
                    sys.exit()
                #starts the game
                elif event.key == K_RETURN:
                    selectionScreen()
                #can use buttons to choose player amount

        #dt, used to move everything at a constant 60 frames per second
        dt = (time.time() - prevTime) * 60
        prevTime = time.time()

        #referesh screen
        screen.fill((104, 134, 197))
        display.fill((104, 134, 197))

        #play the game in the background with two ais
        #update game elements
        ball.update(display, blocks, dt)

        #auto move paddles
        blockOne.aiUpdate(display, ball, dt, display.get_width() // 2, 2.5, blockTwo, True)
        blockTwo.aiUpdate(display, ball, dt, display.get_width() // 2, 2.5, blockOne, True)

        #create a particle trail for the ball
        if not ball.out:
            if settingsData['particles']:
                particles.append(Particle(ball.rect.centerx, ball.rect.centery, 0, 0, ball.radius, ball.color))

        #update all particles
        for particle in particles:
            particle.update(display, dt)
            if particle.radius <= 1:
                particles.remove(particle)

        #if ball was hit, play sound and generate collision particles
        if ball.hit:
            if not settingsData['mute']:
                random.choice(hitSounds).play()
            if settingsData['particles']:
                particles.extend(genCollideParticles(ball.rect.centerx, ball.rect.centery, (255, 224, 172), (5, 5), (-5, 5), (-5, 5), (50, 100)))

        #checking if ball is out on right side
        if ball.rect.x >= display.get_width():
            if not ball.out:
                if settingsData['particles']:
                    particles.extend(genCollideParticles(display.get_width(), ball.rect.centery, (255, 172, 183), (10, 15), (-20, 10), (-20, 20), (50, 100)))
                if not settingsData['mute']:
                    ballCrunch(hitSounds, minVol, crunchDelay)
                xDir = 1
            ball.out = True

        #checking if ball is out on left side
        elif ball.rect.right <= 0:
            if not ball.out:
                if settingsData['particles']:
                    particles.extend(genCollideParticles(0, ball.rect.centery, (255, 172, 183), (10, 15), (10, 20), (-20, 20), (50, 100)))
                if not settingsData['mute']:
                    ballCrunch(hitSounds, minVol, crunchDelay)
                xDir = -1
            ball.out = True

        if ball.out and len(particles) == 0:
            ball.reset(display, xDir)
            if not settingsData['mute']:
                setVolumes(hitSounds, maxVol)

        #blit title and caption
        try:
            display.blit(titleSurface, (display.get_width() // 2 - titleCenter[0], display.get_height() // 2 - titleCenter[1]))
            display.blit(captionSurface, (display.get_width() // 2 - captionCenter[0], 5 * display.get_height() // 6 - captionSize[1]))
        except:
            pass

        #fade caption in and out
        captionSurface.set_alpha(captionAlpha)
        if captionAlpha >= 200:
            captionAlpha = 200
            captionConstant *= -1
        elif captionAlpha <= 0:
            captionAlpha = 0
            captionConstant *= -1
        captionAlpha += captionConstant * dt

        #update screen
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.flip()

#selection screen function
def selectionScreen():

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
    classicCard = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Classic",
                           pygame.image.load("data/textures/cards/classic.png"), "")

    burstCard = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Burst",
                           pygame.image.load("data/textures/cards/burst.png"), "")

    rainCard = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Rain",
                           pygame.image.load("data/textures/cards/rain.png"), "")

    swapCard = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Swap",
                           pygame.image.load("data/textures/cards/swap.png"), "")

    card5 = GameCard((0,0), cardSizes, (94, 124, 187), bigFont, (249, 249, 249), "Blank",
                           pygame.image.load("data/textures/cards/classic.png"), "")

    #adding cards and matching with game mode list, also centering everything where they should be
    gameCards = [classicCard, burstCard, rainCard, swapCard, card5]
    gameModes = ["classic", "burst", "rain", "swap", 6]
    indices = [-2, -1, 0, 1, 2]
    gameCards[indices[0]].reposition(cardCenters["farLeft"])
    gameCards[indices[1]].reposition(cardCenters["left"])
    gameCards[indices[2]].reposition(cardCenters["middle"])
    gameCards[indices[3]].reposition(cardCenters["right"])
    gameCards[indices[4]].reposition(cardCenters["farRight"])
    cardSwap = False

    #if the player has selected something
    selected = None
    players = 0

    #player select amount
    playerSelect = False
    playerSelectRect = pygame.Rect(0, 0, display.get_width() // 3, display.get_height() // 3)
    playerSelectRect.center = display.get_width() // 2, display.get_height() // 2

    playerSelectBorderRect = pygame.Rect(0, 0, playerSelectRect.w + 20, playerSelectRect.h + 20)
    playerSelectBorderRect.center = display.get_width() // 2, display.get_height() // 2

    selectScreen  = pygame.Surface((display.get_width(), display.get_height()))
    selectScreen.set_colorkey((0,0,0))

    pygame.draw.rect(selectScreen, (249, 249, 249), playerSelectBorderRect)
    pygame.draw.rect(selectScreen, (94, 124, 187), playerSelectRect)

    p1optSurf = bigFont.render("1 Player", False, (249, 249, 249))
    p1optSize = bigFont.size("1 Player")
    p1optCenter = (display.get_width() // 2 - p1optSize[0] // 2, display.get_height() // 2 - p1optSize[1])
    p1optRect = pygame.Rect(0, 0, p1optSize[0], p1optSize[1])
    p1optRect.center = selectScreen.get_width() // 2, playerSelectRect.top + 2 * playerSelectRect.h // 7
    selectScreen.blit(p1optSurf, p1optRect)
    p1optRect.w = 500
    p1optRect.center = selectScreen.get_width() // 2, playerSelectRect.top + 2 * playerSelectRect.h // 7
    pygame.draw.rect(selectScreen, (84, 114, 177), p1optRect, 10)

    p2optSurf = bigFont.render("2 Player", False, (249, 249, 249))
    p2optSize = bigFont.size("2 Player")
    p2optCenter = (display.get_width() // 2 - p2optSize[0] // 2, display.get_height() // 2)
    p2optRect = pygame.Rect(0, 0, p2optSize[0], p2optSize[1])
    p2optRect.center = selectScreen.get_width() // 2, playerSelectRect.top + 5 * playerSelectRect.h // 7
    selectScreen.blit(p2optSurf, p2optRect)
    p2optRect.w = 500
    p2optRect.center = selectScreen.get_width() // 2, playerSelectRect.top + 5 * playerSelectRect.h // 7
    pygame.draw.rect(selectScreen, (84, 114, 177), p2optRect, 10)

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
        players = 0

        #execute events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if selected == None:
                        running = False
                    else:
                        selected = None
                elif event.key == K_RETURN:
                    selected = gameModes[indices[2]]
                elif event.key == K_LEFT:
                    for i in range(len(indices)):
                        indices[i] -= 1
                    cardSwap = True
                elif event.key == K_RIGHT:
                    for i in range(len(indices)):
                        indices[i] += 1
                    cardSwap = True
                elif event.key == K_1:
                    if selected != None:
                        players = 1
                elif event.key == K_2:
                    if selected != None:
                        players = 2
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if selected != None:
                        if p1optRect.collidepoint(mousePos):
                            players = 1
                        elif p2optRect.collidepoint(mousePos):
                            players = 2
                    elif lRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
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
                        settingsMenu()
                    else:
                        for card in gameCards:
                            if card.normalRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                                selected = gameModes[indices[2]]

        #check if the player selected a game
        if selected != None:
            if players > 0:
                if selected == "classic":
                    vols = (maxVol, minVol)
                    ballInfo = (ballSpeed, ballRadius, xDir)
                    ClassicMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay, settingsData['mute'], settingsData['particles'])
                    selected = None
                    players = 0
                elif selected == "burst":
                    vols = (maxVol, minVol)
                    ballInfo = (ballSpeed, ballRadius, xDir)
                    BurstMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay, settingsData['mute'], settingsData['particles'])
                    selected = None
                    players = 0
                elif selected == "rain":
                    vols = (maxVol, minVol)
                    ballInfo = (ballSpeed, ballRadius, xDir)
                    RainMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay, settingsData['mute'], settingsData['particles'])
                    selected = None
                    players = 0
                elif selected == "swap":
                    vols = (maxVol, minVol)
                    ballInfo = (ballSpeed, ballRadius, xDir)
                    SwapMode(display, screen, players, hitSounds, vols, bigFont, score, ballInfo, paddleSpeed, crunchDelay, settingsData['mute'], settingsData['particles'])
                    selected = None
                    players = 0

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

        #draw player amount selector
        if selected != None:
            display.blit(selectScreen, (0,0))

        #update the screen
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
        pygame.display.flip()

def settingsMenu():
    global screen, settingsData

    #setup to change settings
    settingsInstance = settingsData

    #gui that only contains the back and apply buttons
    gui = pygame.Surface((display.get_width(), display.get_height()))
    gui.set_colorkey((0,0,0))

    #settings border
    borderRect = pygame.Rect(0, 0, 3 * display.get_width() // 5, 3 * display.get_height() // 5)
    borderRect.center = display.get_width() // 2, display.get_height() // 2

    #settings menu
    menuRect = pygame.Rect(0, 0, 59 * display.get_width() // 100, 59 * display.get_height() // 100)
    menuRect.center = display.get_width() // 2, display.get_height() // 2

    #settings title
    titleSurf = bigFont.render("Settings", False, (249, 249, 249))
    titleSize = bigFont.size("Settings")

    #volume setting
    volScrollBar = HorizScrollBar((menuRect.centerx + menuRect.w // 4, menuRect.top + menuRect.h // 5), (borderRect.w // 2.25, 50), (249, 249, 249), 1, settingsInstance['volume'])
    volSurf = smallFont.render("Volume", False, (249, 249, 249))
    volSize = smallFont.size("Volume")

    #mute setting
    muteButton = pygame.Rect(0, 0, 50, 50)
    muteButton.center = menuRect.centerx + menuRect.w // 4, menuRect.top + 2 * menuRect.h // 5
    muteSurf = smallFont.render("Mute Sounds", False, (249, 249, 249))
    muteSize = smallFont.size("Mute Sounds")

    #fullscreen setting
    fullscreenButton = pygame.Rect(0, 0, 50, 50)
    fullscreenButton.center = menuRect.centerx + menuRect.w // 4, menuRect.top + 3 * menuRect.h // 5
    fullscreenSurf = smallFont.render("Fullscreen", False, (249, 249, 249))
    fullscreenSize = smallFont.size("Fullscreen")

    #particle setting
    particleButton = pygame.Rect(0, 0, 50, 50)
    particleButton.center =  menuRect.centerx + menuRect.w // 4, menuRect.top + 4 * menuRect.h // 5
    particleSurf = smallFont.render("Display Particles", False, (249, 249, 249))
    particleSize = smallFont.size("Display Particles")

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
    bRect = pygame.draw.polygon(gui, (94, 124, 187), bVerts)
    backSurf = bigFont.render("Back", False, (249, 249, 249))
    backSurfRect = pygame.Rect(0,0,backSurf.get_width(),backSurf.get_height())
    backSurfRect.center = (bVerts[2][0] // 2, bVerts[2][1] // 2)

    #apply button
    applyButton = pygame.Rect(0, 0, 500, 200)
    applyButton.center = gui.get_width() // 2, gui.get_height() - 150
    applyButtonBorder = pygame.Rect(0, 0, 520, 220)
    applyButtonBorder.center = applyButton.center
    applySurf = bigFont.render("Apply", False, (249, 249, 249))
    applySurfRect = pygame.Rect(0, 0, bigFont.size("Apply")[0], bigFont.size("Apply")[1])
    applySurfRect.center = applyButton.center

    #gui mask for perfect collisions
    guiMask = pygame.mask.from_surface(gui)

    #mouse settings
    xRatio = screen.get_width() / display.get_width()
    yRatio = screen.get_height() / display.get_height()

    #appl changes bool
    apply = False
    fullscreen = settingsInstance['fullscreen']
    moveScroller = False

    running = True
    while running:

        #mouse position
        mx, my = pygame.mouse.get_pos()
        mousePos = int(mx / xRatio), int(my / yRatio)

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
                    if muteButton.collidepoint(mousePos):
                        settingsInstance['mute'] = not settingsInstance['mute']
                    elif fullscreenButton.collidepoint(mousePos):
                        settingsInstance['fullscreen'] = not settingsInstance['fullscreen']
                    elif particleButton.collidepoint(mousePos):
                        settingsInstance['particles'] = not settingsInstance['particles']
                    elif applyButton.collidepoint(mousePos):
                        apply = True
                    elif bRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
                        running = False
                    elif volScrollBar.scrollerRect.collidepoint(mousePos):
                        moveScroller = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if moveScroller:
                        moveScroller = False

        #clear screen
        display.fill((104, 134, 197))
        gui.fill((0,0,0))

        #draw border and menu surface and title
        pygame.draw.rect(display, (249, 249, 249), borderRect)
        pygame.draw.rect(display, (104, 134, 197), menuRect)
        display.blit(titleSurf, (display.get_width() // 2 - titleSize[0] // 2, borderRect.top - titleSize[1]))

        #move the scroller on the scrollbar
        if moveScroller:
            volScrollBar.move(mousePos[0])

        #draw settings options to the screen
        display.blit(volSurf, (menuRect.left + 50, menuRect.top + menuRect.h // 5 - volSize[1] // 2))
        volScrollBar.draw(display)

        if settingsInstance['mute']:
            pygame.draw.rect(display, (249, 249, 249), muteButton)
        else:
            pygame.draw.rect(display, (249, 249, 249), muteButton, 2)
        display.blit(muteSurf, (menuRect.left + 50, menuRect.top + 2 * menuRect.h // 5 - muteSize[1] // 2))

        if settingsInstance['fullscreen']:
            pygame.draw.rect(display, (249, 249, 249), fullscreenButton)
        else:
            pygame.draw.rect(display, (249, 249, 249), fullscreenButton, 2)
        display.blit(fullscreenSurf, (menuRect.left + 50, menuRect.top + 3 * menuRect.h // 5 - fullscreenSize[1] // 2))

        if settingsInstance['particles']:
            pygame.draw.rect(display, (249, 249, 249), particleButton)
        else:
            pygame.draw.rect(display, (249, 249, 249), particleButton, 2)
        display.blit(particleSurf, (menuRect.left + 50, menuRect.top + 4 * menuRect.h // 5 - particleSize[1] // 2))

        #draw back and apply buttons
        if bRect.collidepoint(mousePos) and guiMask.get_at(mousePos):
            pygame.draw.polygon(gui, (249, 249, 249), boVerts)
        pygame.draw.polygon(gui, (94, 124, 187), bVerts)
        gui.blit(backSurf, backSurfRect)

        if applyButton.collidepoint(mousePos) and guiMask.get_at(mousePos):
            pygame.draw.rect(gui, (249, 249, 249), applyButtonBorder)
        pygame.draw.rect(gui, (94, 124, 187), applyButton)
        gui.blit(applySurf, applySurfRect)

        #remaking the mask
        guiMask = pygame.mask.from_surface(gui)

        #blit gui to the display
        display.blit(gui, (0,0))

        #if changes need to be done, apply them
        if apply:
            if settingsInstance['fullscreen'] and not fullscreen:
                flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                screen = pygame.display.set_mode(size=(1200, 700), flags=flags)
                fullscreen = True
            elif not settingsInstance['fullscreen'] and fullscreen:
                screen = pygame.display.set_mode(size=(1200, 700))
            settingsInstance['volume'] = volScrollBar.getOutput()
            if not settingsInstance['mute']:
                setVolumes(hitSounds, settingsInstance['volume'])
                random.choice(hitSounds).play()
            xRatio = screen.get_width() / display.get_width()
            yRatio = screen.get_height() / display.get_height()
            apply = False

        #update the window
        screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0, 0))
        pygame.display.flip()

    #save the new settings in the json file
    with open("data/settings/settings.json", "w") as writeFile:
        json.dump(settingsInstance, writeFile)
    settingsData = settingsInstance

#run the program
main()
