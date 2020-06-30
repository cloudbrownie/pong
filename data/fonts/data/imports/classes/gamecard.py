import pygame

class GameCard:
    def __init__(self, center, sizes, cardColor, font, fontColor, title, img, description):
        #create surfaces
        self.title = title
        self.normalSurf = pygame.Surface((sizes[0][0], sizes[0][1]))
        self.normalSurf.fill(cardColor)
        self.smallSurf = pygame.Surface((sizes[1][0], sizes[1][1]))
        self.smallSurf.fill(cardColor)
        self.eSmallSurf = pygame.Surface((sizes[2][0], sizes[2][1]))
        self.eSmallSurf.fill(cardColor)
        #creates rects                 
        self.normalRect = pygame.Rect(0, 0, sizes[0][0], sizes[0][1])
        self.normalRect.center = center
        self.smallRect = pygame.Rect(0, 0, sizes[1][0], sizes[1][1])
        self.smallRect.center = center
        self.eSmallRect = pygame.Rect(0, 0, sizes[2][0], sizes[2][1])
        self.eSmallRect.center = center
        #title and image rendering  
        titleSurf = font.render(title, False, fontColor)
        scaledImg = pygame.Surface((5 * sizes[0][0] // 6, sizes[0][1] // 3))
        scaledImg.blit(pygame.transform.scale(img, (scaledImg.get_width(), scaledImg.get_height())), (0,0))
        #blit to normal surface then scale and blit to smaller surfaces
        self.normalSurf.blit(titleSurf, (sizes[0][0] // 2 - font.size(title)[0] // 2, font.size(title)[1] // 2))
        self.normalSurf.blit(scaledImg, ((sizes[0][0] - scaledImg.get_width()) // 2, sizes[0][1] // 3))
        self.smallSurf.blit(pygame.transform.scale(self.normalSurf, (sizes[1][0], sizes[1][1])), (0,0))
        self.eSmallSurf.blit(pygame.transform.scale(self.normalSurf, (sizes[2][0], sizes[2][1])), (0,0))
        

    def draw(self, display, index):
        if index == 2:
            display.blit(self.normalSurf, self.normalRect)
        elif index == 1 or index == 3:
            display.blit(self.smallSurf, self.smallRect)
        elif index == 0 or index == 4:
            display.blit(self.eSmallSurf, self.eSmallRect)

    def reposition(self, center):
        self.normalRect.center = center
        self.smallRect.center = center
        self.eSmallRect.center = center
