import pygame
timer = pygame.USEREVENT + 1
attack = pygame.USEREVENT + 2
heal = pygame.USEREVENT + 3
killAliveObject = pygame.USEREVENT + 4
spawnAliveObject = pygame.USEREVENT + 5
loadChunk = pygame.USEREVENT + 6
unloadChunk = pygame.USEREVENT + 7
move = pygame.USEREVENT + 8
placeObject = pygame.USEREVENT + 9

def attackEventTemplate(attackerID,attackedID,damage):
    return pygame.event.Event(attack,attackerID=attackerID,attackedID=attackedID,damage=damage)
def healEventTemplate(healedID,health):
    return pygame.event.Event(heal,healedID=healedID,health=health)
def killAliveObjectEventTemplate(killedID,killerID):
    return pygame.event.Event(killAliveObject,killedID=killedID,killerID=killerID)
def spawnAliveObjectEventTemplate(spawnedID):
    return pygame.event.Event(killAliveObject,spawnedID=spawnedID)
def loadChunkEventTemplate(pos:tuple[3]):
    return pygame.event.Event(loadChunk,pos=pos)
def unloadChunkEventTemplate(pos:tuple[3]):
    return pygame.event.Event(unloadChunk,pos=pos)
def moveEventTemplate(movedObject):
    return pygame.event.Event(move,movedObject=movedObject)
def placeObjectEventTemplate(objectID,placerID):
    return pygame.event.Event(placeObject,objectID=objectID,placerID=placerID)