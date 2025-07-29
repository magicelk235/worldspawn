import events,pygame
class Timer():
	eventRegister = events.EventRegister

	timerEvent = eventRegister.register("timer",None)
	pygame.time.set_timer(timerEvent,100)

	def __init__(self,game):
		self.game = game
		self.countDowns = {}
	
	def updateTimers(self):
		if game.eventHappend(self.timerEvent):
			for key in list(self.countDowns.keys()):
				if self.countDowns[key] != 0:
					self.countDowns[key] -= 0.1
					
	def addCountDown(self,name,start):
		self.countDowns[name] = start

	def countDownEnded(self,name,start=-1):
		if self.countDowns[name] == 0:
			if start != -1:
				self.countDowns[name] = start
			else:
				self.countDowns.pop(name)
			return True
		return False
		