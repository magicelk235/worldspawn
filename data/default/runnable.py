import pygame,platform,events,timerObject
class Runnable(events.EventManager,timerObject.Timer):
    eventRegister = events.EventRegister
    
    def __init__(self,game:platform.platform):
        timer.Timer.__init__(self,game)
        events.EventManager.__init__(self)
        self.game = game
        self.id = Nonega
    
    def addEvent(self,event):
        events.EventManager.addEvent(self,event)
        self.game.addEvent(event)

    def setID(self,id):
        self.id = id
                
    def getID(self):
        return self.id