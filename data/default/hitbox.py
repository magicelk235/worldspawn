class Hitbox:
    def __init__(self,w:int,h:int,xOffset:int=0,yOffset:int=0):
        self.w = w
        self.h = h
        self.xOffset = xOffset
        self.yOffset = yOffset

    def getCenter(self):
        return self.w//2,self.h//2

    def UpdateRect(self,rect:rect,pos:tuple):
        rect.rect.x = pos[0] + self.xOffset
        rect.rect.y = pos[1] + self.yOffset

    def getRect(self,pos:tuple):
        return Rect(pygame.rect.Rect(*pos[:2], self.w, self.h), pos[2])