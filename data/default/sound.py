import runnable,pygame,sys,events,media.soundLoader
class Sound(runnable.Runnable):

	soundEndedEvent = eventRegister.register("soundEnded",None)


	_channel_to_source = {}
	def __init__(self,game, soundPath, pos, loops=1, followID=None, maxHearDistance=300):
		super().__init__(game)
		self.loop = loop
		self.pos = pos
		self.maxHearDistance = maxHearDistance
		self.followID = followID

		self.sound = pygame.mixer.Sound(media.soundLoader.getSound(soundPath))
		self.channel = pygame.mixer.find_channel()
		
		self.channel.play(self.sound, loops=loops)
		self.channel.set_endevent(self.soundEndedEvent)
		Sound._channel_to_source[self.channel] = self

	def updatePos(self):
		if self.followID:
			if self.game.objectExist(self.followID):
				if self.game.getObjectByID(self.followID).eventHappend(events.EventRegister.getID("move")):
					self.pos = self.game.getObjectByID(self.followID).getAxis()
			else:
				self.followID = None

	def update(self, player):
		self.updatePos()
		delta = player.getAxis() - self.pos
		dist = delta.length()
		volume = max(0.0, min(1.0, 1 - dist/self.max_hear))
		pan = max(-1.0, min(1.0, delta.x/self.max_hear))
		left  = volume * (1 - pan) / 2
		right = volume * (1 + pan) / 2
		self.channel.set_volume(left, right)