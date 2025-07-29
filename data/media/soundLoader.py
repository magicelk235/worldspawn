import pygame,os,loader
def loadSound(path):
    return pygame.mixer.Sound(path)
    
path = "sounds"
validExtensions = {".oog", ".wav"}
global sounds
sounds = {}
loader.load(path,validExtensions,sounds,loadSound)

def getSound(path):
    return sounds.get[path]