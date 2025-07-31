import pygame,math
import sys,idManager
import events,media.soundLoader,sprite,hitbox,image,enum,rect,displayType,inventory,platform

class AliveObjectData(sprite.SpriteData):
    def __init__(self, hitbox,animations,save=[],clientSave=[],maxHealth=1,damage=1,shield=0,speed=1,react=0,visionRadius=200):
        super().__init__(hitbox,animations,save,clientSave)
        self.maxHealth = maxHealth
        self.damage = damage
        self.sheild = shield
        self.speed = speed
        self.react = react
        self.visionRadius = visionRadius

class AliveObject(sprite.Sprite):
    eventRegister = events.EventRegister


    @staticmethod
    def attackEventTemplate(attacker:str,attacked:str,remaining:int):
        return pygame.event.Event(events.EventRegister.getID("attack"),locals())

    @staticmethod
    def healEventTemplate(healed:str,amount:int):
        return pygame.event.Event(events.EventRegister.getID("attack"),locals())

    attackEvent = eventRegister.register("attack",attackEventTemplate)

    healEvent = eventRegister.register("heal",healEventTemplate)

    class directionType(enum.Enum):
        left = False
        right = True

    # object data
    objectData = AliveObjectData(hitbox.Hitbox(1,1),{"default":Animation(image.ImageData(flipX="@direction")),"walk":Animation(image.ImageData(flipX="@direction")),"damage":Animation(flipX="@direction",imageData=image.ImageData(color=(270,0,0,0)))}) # type: ignore

    def __init__(self, game, pos: tuple[3],tag=None, dict=None):
        super().__init__(game, pos,dict)
        self.health = self.objectData.maxHealth
        self.direction = self.directionType.left
        self.tag = tag
        self.resetModifiers()
        self.temporaryModifiers = []
        self.allies = []
        self.attacker = None
        self.target = None
        self.inventory = inventory.Inventory(5,5,self)

    def searchForAllies(self):
        for aliveObject in list(self.game.getAliveObjects().values()):
            if self.shareID(aliveObject):
                self.allies.append(aliveObject.id)

    def collideCheck(self,other,inflate) -> bool:
        return self.collideCheckRect(other.hitbox)

    def collideCheckRect(self,rect:rect.Rect,inflate) -> bool:
        return self.hitbox.collideRect(rect)


    def heal(self,amount:int):
        if self.health+amount > self.maxHealth:
            amount = self.health+amount-self.maxHealth
        self.health += amount
        self.addEvent(self.healEventTemplate(self.id,amount))

    def setX(self,x:int) -> None:
        super().setX(x)
        self.visionRect.setX(self.getX())

    def setY(self,y:int) -> None:
        super().setY(y)
        self.visionRect.setY(self.getY())
    
    def setDimension(self,dimension:str) -> None:
        super().setDimension(dimension)
        self.visionRect.setDimension(self.getDimension())

    def shareID(self,other:"AliveObject") -> bool:
        if self.id == other.tag:
            return True
        if self.tag == other.id:
            return True
        return self.tag == other.tag
        

    def collideVisionCheck(self,other:"AliveObject") -> bool:
        return other.collideCheckRect(self.visionRect)

    def resetModifiers(self) -> None:
        self.maxHealth: int = self.objectData.maxHealth
        self.heal(0)
        self.damage: int = self.objectData.damage
        self.shield: float = self.objectData.sheild
        self.speed: int = self.objectData.speed
        self.range: int = self.objectData.range
        self.vision:int = self.objectData.vision
        try:
            self.visionRect.updateSize(self.vision,self.vision)
        except:
            self.visionRect:rect.Rect = rect(pygame.rect.Rect(*self.rect.getAxis(),self.vision,self.vision),self.rect.dimension,displayType.DisplayTypes.center)
        
    def attack(self, attacked) -> None:
        attacked.applyDamage(self.damage)
        self.addEvent()

    def applyDamage(self, damage, attacker=None) -> None:
        if self.timers.get("damage", None) == None:
            self.timers["damage"] = 0
            self.damageEffectOn()
        if attacker != None and not self.shareID(attacker):
            self.attacker = attacker
            for id in self.allies:
                self.game.getObject(id).attacker = self.attacker
        self.health -= round(damage * (1.00 - self.shield))