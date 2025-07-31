import rect,pygame
class Hitbox:
    def __init__(self,w:int,h:int,xOffset:int=0,yOffset:int=0):
        self.w = w
        self.h = h
        self.xOffset = xOffset
        self.yOffset = yOffset

    def getCenter(self):
        return self.w//2,self.h//2

    def UpdateRect(self,hitbox,rect):
        hitbox.setX(rect.getX() + self.xOffset)
        hitbox.setY(rect.getY() + self.yOffset)
        hitbox.setDimension(rect.dimension)
        

    def getRect(self,pos:tuple):
        return rect.Rect(pygame.rect.Rect(*pos[:2], self.w, self.h), pos[2])