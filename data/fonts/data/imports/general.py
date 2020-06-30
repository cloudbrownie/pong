import pygame, time, random
from data.imports.classes.particle import Particle

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
