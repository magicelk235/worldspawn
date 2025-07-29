import pygame

class RegisteredEvent():
    def __init__(self,id,createFunction):
        self.id = id
        self.createFunction = createFunction

    def getID(self):
        return self.id

    def create(self):
        return self.createFunction


class EventRegister:
    nextID = pygame.USEREVENT
    registeredEvents = {}

    @classmethod
    def register(cls, name,createFunction):
        id = cls.nextID
        cls.nextID += 1
        cls.registeredEvents[name] = RegisteredEvent(id,createFunction)
        return id

    @staticmethod
    def getEvent(cls,name):
        return cls.registeredEvents[name]

    @classmethod
    def getID(cls, name):
        return cls.getEvent(name).getID()

    @staticmethod
    def create(cls,name):
        return cls.getEvent(name).create() 


timer = pygame.USEREVENT + 1
attack = pygame.USEREVENT + 2
heal = pygame.USEREVENT + 3
killAliveObject = pygame.USEREVENT + 4
spawnAliveObject = pygame.USEREVENT + 5
loadChunk = pygame.USEREVENT + 6
unloadChunk = pygame.USEREVENT + 7
move = pygame.USEREVENT + 8
placeObject = pygame.USEREVENT + 9
eventSwitch = pygame.USEREVENT + 10
updateClient = pygame.USEREVENT + 11
clientJoin = pygame.USEREVENT + 12
clientDisconnect = pygame.USEREVENT + 13
projectileHit = pygame.USEREVENT + 14
entityBreed = pygame.USEREVENT + 15
plantGrow = pygame.USEREVENT + 16
doorSwitch = pygame.USEREVENT + 17
dropItem = pygame.USEREVENT + 18
banPlayer = pygame.USEREVENT + 19
inventoryInteract = pygame.USEREVENT + 20
spritePathChanged = pygame.USEREVENT + 21
guiStateChanged = pygame.USEREVENT + 22
soundCreated = pygame.USEREVENT + 23
soundEnded = pygame.USEREVENT + 24

def attackEventTemplate(attackerID,attackedID,damage):
    return pygame.event.Event(attack,locals())

def healEventTemplate(healedID,health):
    return pygame.event.Event(heal,locals())

def killAliveObjectEventTemplate(killedID,killerID,killedType):
    return pygame.event.Event(killAliveObject,locals())

def spawnAliveObjectEventTemplate(spawnedID):
    return pygame.event.Event(killAliveObject,locals())

def loadChunkEventTemplate(pos:tuple[3]):
    return pygame.event.Event(loadChunk,locals())

def unloadChunkEventTemplate(pos:tuple[3]):
    return pygame.event.Event(unloadChunk,locals())

def moveEventTemplate(movedObject):
    return pygame.event.Event(move,locals())

def placeObjectEventTemplate(objectID,placerID):
    return pygame.event.Event(placeObject,locals())

def eventSwitchEventTemplate(eventID,state):
    return pygame.event.Event(eventSwitch,locals())

def updateClientEventTemplate(clientIP,clientID):
    return pygame.event.Event(clientJoin,locals())

def clientJoinEventTemplate(clientIP,clientID):
    return pygame.event.Event(clientJoin,locals())

def clientDisconnectEventTemplate(clientIP,clientID):
    return pygame.event.Event(clientDisconnect,locals())

def projectileHitEventTemplate(projectileID,attackedID):
    return pygame.event.Event(projectileHit,locals())

def entityBreedEventTemplate(fatherID,motherID):
    return pygame.event.Event(entityBreed,locals())

def doorSwitchEventTemplate(objectID,doorState):
    return pygame.event.Event(doorSwitch,locals())

def dropItemEventTemplate(itemID):
    return pygame.event.Event(dropItem,locals())

def banPlayerEventTemplate(playerID,playerIP):
    return pygame.event.Event(banPlayer,locals())
    
def inventoryInteractEventTemplate(playerID):
    return pygame.event.Event(inventoryInteract,locals())

def spritePathChangedEventTemplate(spriteID,newPath):
    return pygame.event.Event(spritePathChanged,locals())
    
def guiStateChangedEventTemplate(playerIDs,state):
    return pygame.event.Event(guiStateChanged,locals())


class EventManager:
    def __init__(self):
        self.events = {}
        
    def addEvent(self,event):
        eventID = event.type
        if self.events.get(eventID,False):
            self.events[eventID].append(event)
        else:
            self.events[eventID] = [event]
    
    def eventHappend(self,eventID):
        return eventID in self.events
        
    def clearEvents(self):
        self.events.clear()
        
    def getEventList(self,eventID):
        return self.events.get(eventID,[])

    def convertEventList(self,events):
        for event in events:
            self.addEvent(event)