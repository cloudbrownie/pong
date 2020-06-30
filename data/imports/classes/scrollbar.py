import pygame

class HorizScrollBar:
    def __init__(self, center, size, color, origScale, startVal):
        self.centerx = center[0]
        self.centery = center[1]
        self.width = size[0]
        self.height = size[1]
        self.color = color

        self.origScale = origScale
        self.drawScale = size[0] / origScale

        self.outlineRect = pygame.Rect(0, 0, size[0], size[1])
        self.outlineRect.center = center
        self.outlineWidth = 2

        startWidthVal = startVal * self.drawScale
        self.insideRect = pygame.Rect(0, 0, size[0], size[1])
        self.insideRect.center = center
        self.insideRect.w = startWidthVal

        self.scrollerRect = pygame.Rect(0, 0, size[1] + 10, size[1] + 10)
        self.scrollerRect.center = self.insideRect.x + startWidthVal, center[1]


    def draw(self, display):
        #draw the outline rectangle
        pygame.draw.rect(display, self.color, self.outlineRect, self.outlineWidth)
        #draw the inside rectangle
        pygame.draw.rect(display, self.color, self.insideRect)
        #draw the scroller
        pygame.draw.rect(display, self.color, self.scrollerRect)

    def move(self, x):
        self.scrollerRect.centerx = x
        if self.scrollerRect.centerx < self.outlineRect.left:
            self.scrollerRect.centerx = self.outlineRect.left
        elif self.scrollerRect.centerx > self.outlineRect.right:
            self.scrollerRect.centerx = self.outlineRect.right
        self.insideRect.w = self.scrollerRect.centerx - self.outlineRect.left

    def getOutput(self):
        return (self.scrollerRect.centerx - self.insideRect.left) / self.drawScale
