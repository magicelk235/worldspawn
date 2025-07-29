import pygame
import math
import sys,idManager
import events,runnable,media.soundLoader,sprite,hitbox,image,enum

class AliveObjectData(sprite.SpriteData):
    def __init__(self, hitbox,animations,save=[],clientSave=[],health=1,damage=1,shield=0,speed=1,react=0,visionRadius=200):
        super().__init__(hitbox,animations,save,clientSave)
        self.health = health
        self.damage = damage
        self.sheild = shield
        self.speed = speed
        self.react = react
        self.visionRadius = visionRadius

class AliveObject(sprite.Sprite):

    class directionType(enum.Enum):
        left = False
        right = True

    # object data
    objectData = AliveObjectData(hitbox.Hitbox(1,1),{"default":Animation(image.ImageData(flipX="@direction")),"damage":Animation(flipX="@direction",imageData=image.ImageData(color=(270,0,0,0)))})

    def __init__(self, game, pos: tuple[3],tag=None, dict=None):
        super().__init__(game, pos,dict)
        self.direction = directionType.left
        self.tag = tag
        self.health: int = data.health
        self.damage: int = data.damage
        self.shield: float = data.sheild
        self.speed: int = data.speed
        self.hitbox:rect = data.hitbox.getRect(self.rect.getPos())
        self.range:int = data.range
        self.vision:int = data.vision
        self.visionRect:rect = rect(pygame.rect.Rect(*self.rect.getPos()[:2],data.vision,data.vision),self.rect.dimension,DisplayType.center)
        self.temporary_modifiers = []
        self.attacker = None
        self.target = None

    def collideVisionCheck(self,other):
        return other.rect.colliderect(self.visionRect)

    # damage effects like red tint
    def damageEffectOn(self):...
    def damageEffectOff(self):...

    def resetModifiers(self):
        self.health: int = self.data.health
        self.damage: int = self.data.damage
        self.shield: float = self.data.sheild
        self.speed: int = self.data.speed
        self.hitbox: rect = self.data.hitbox.getRect(self.rect.getPos())
        self.range: int = self.data.range
        self.visionRect.updateSize(self.vision,self.vision)

    def collideCheck(self,object):
        return self.hitbox.colliderect(object.hitbox)

    def setPos(self,pos:tuple[3],game):
        self.setX(pos[0],game)
        self.setY(pos[1],game)
        self.setDimension(pos[2],game)

    def setDimension(self,dimension:str,game):
        self.rect.dimension = dimension
        self.visionRect.dimension = dimension
        self.hitbox.dimension = dimension
        game.post_event(game_events.moveEventTemplate(self.id))

    def setX(self,x:int,game):
        self.rect.rect.x = x
        self.visionRect.rect.centerx = x
        self.data.hitbox.updateRect(self.hitbox, self.rect.getPos())
        game.post_event(game_events.moveEventTemplate(self.id))

    def setY(self,y:int,game):
        self.rect.rect.y = y
        self.visionRect.rect.centery = y
        self.data.hitbox.updateRect(self.hitbox, self.rect.getPos())
        game.post_event(game_events.moveEventTemplate(self.id))
        
    def attack(self, attacked,game):
        attacked.applyDamage(self.damage)
        game.post_event(game_events.attackEventTemplate(self.id,self.attacker.id,self.damage))

    def applyDamage(self, game, damage, attacker=None):
        if self.timers.get("damage", None) == None:
            self.timers["damage"] = 0
            self.damageEffectOn()
        if attacker != None and not default.has_one_tag(self, attacker):
            self.attacker = attacker
            for object in list(game.objects.values()):
                if object.tag == self.id:
                    object.attacker = attacker
        self.health -= round(damage * (1.00 - self.shield))