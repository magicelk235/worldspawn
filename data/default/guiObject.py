import pygame
import math
import sys,idManager
import events,runnable,sprite

class UIObject(sprite.Sprite):
    def __init__(self,game,pos,playersIDs):
        super().__init__(game,pos)
        self.playersIDs = playersIDs
        self.uiParts = []

    def setVisible(self):
        super().setVisible
        for part in self.uiPart:
            part.setVisible()
        
    def setUnvisible(self):
        super().setUnvisible
        for part in self.uiPart:
            part.setUnvisible()
        
    def switchVisible(self):
        super().switchVisible()
        for part in self.uiPart:
            part.switchVisible()
        
    def update(self):
        super().update()
        for part in self.uiPart:
            part.update()
            
    def isPlayerVisible(self, player):
        return self.hidden and player.id in self.playersIDs

    def display(self,displaySurf,player,displayOffset):
        if isPlayerVisible(player) and not self.hidden:
            self.image.display(displaySurf,self.getAxis())
