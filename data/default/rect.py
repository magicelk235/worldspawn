import pygame,enum,default,displayType    

class Rect:
    def __init__(self, rect, dimension,displayType=displayType.DisplayType.topLeft,renderOrder=4):
        # default rect object
        self.rect:pygame.rect.Rect = rect
        # dimension
        self.dimension = dimension
        # used in more animations, from where to display rhe object
        self.displayType = displayType
        # what order in the "z-axis" the object will display, 4 is normal and calculated by y,the bigger the later
        self.renderOrder = renderOrder

    @staticmethod
    def addPos(pos1,pos2):
        return pos1[0] + pos2[0],pos1[1] + pos2[1]
    @staticmethod
    def subPos(pos1,pos2):
        return pos1[0] - pos2[0],pos1[1]-pos2[1]

    def moveToPoint(self, targetPos, speed):
        if self.dimension != targetPos[2]:
            return
        cx, cy = self.rect.center
        tx, ty = targetPos
        dx = tx - cx
        dy = ty - cy
        distance = math.hypot(dx, dy)
        if distance <= speed or distance == 0:
            self.rect.center = targetPos[:2]

        else:
            nx = dx / distance
            ny = dy / distance
            self.rect.centerx += nx * speed
            self.rect.centery += ny * speed
        return self.rect.center == targetPos[:2]

    def setByDisplay(self,pos):
        default.setAttr(self,"rect." + self.displayType, pos)

    def setW(self, w):
        self.rect.w = w

    def setH(self, h):
        self.rect.h = h

    def setSize(self,w,h):
        self.setW(w)
        self.setH(h)

    

    def setXY(self,x,y):
        self.setX(x)
        self.setY(y)

    def getXY(self):
        return self.rect.x,self.rect.y

    def getPos(self):
        return self.rect.x,self.rect.y,self.dimension

    def getByDisplay(self):
        return default.getAttr(self,"rect." + self.displayType)

    def getSize(self):
        return self.rect.size

    def getX(self):
        return self.rect.x

    def getY(self):
        return self.rect.y

    def copy(self):
        return Rect(self.rect.copy(), self.dimension)

    def getW(self):
        return self.rect.w

    def getH(self):
        return self.rect.h

    def calculateDistanceX(self,otherRect):
        return ((otherRect.Rect.centerx - self.rect.centerx) ** 2)**0.5

    def calculateDistanceY(self,otherRect):
        return ((otherRect.Rect.centery - self.rect.centery) ** 2)**0.5

    def calculateDistance(self,otherRect):
        return self.calculateDistanceX(otherRect) + self.calculateDistanceY(otherRect)

    def __eq__(self, other):
        if isinstance(other, Rect):
            if self.sameDimension(other):
                return False
            return self.rect.x == other.rect.x and self.rect.y == other.rect.y and self.rect.w == other.rect.w and self.rect.h == other.rect.h
        return False

    def sameDimension(self,other):
        return self.dimension == other.dimension

    def collideRectIgnoreDimension(self,other):
        return self.rect.colliderect(other.rect)

    def containsRect(self,other):
        return self.sameDimension(other) and self.rect.contains(other)

    def collideRect(self, other,additionalRange=0):
        return self.sameDimension(other) and self.rect.inflate(additionalRange,additionalRange).colliderect(other.rect)

    

    def collidePoint(self, x, y, dimension):
        return self.dimension == dimension and self.rect.collidepoint(x,y)