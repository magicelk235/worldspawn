import runnable,pygame,sound,idManager,events

class DisplayManager(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.screen = pygame.display.set_mode((800, 600), pygame.SCALED | pygame.RESIZABLE)
		self.displaySurface = pygame.display.get_surface()

		self.offset = pygame.math.Vector2()
		self.halfW = self.screen.get_width() // 2
		self.halfH = self.screen.get_height() // 2

	def removeObject(self,object):
		self.remove(object)

	def update(self,player,clearTrash=True,updateAllGifs=False):
		playerOffset = pygame.math.Vector2()
		playerOffset.x = player.rect.rect.centerx - self.halfW
		playerOffset.y = player.rect.rect.centery - self.halfH
		defaultRenderOrder = []
		lateRenderOrder = []

		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.renderOrder if sprite.Rect else float('-inf')):
			if sprite.rect is not None and sprite.image is not None:
				if updateAllGifs:
					sprite.image.image._animate()
				if sprite.rect.renderOrder > 4:
					sprite.display(self.displaySurface,player,playerOffset)
				elif sprite.rect.renderOrder == 4:
					defaultRenderOrder.append(sprite)
				else:
					lateRenderOrder.append(sprite)
			elif clearTrash:
				self.remove(sprite)
			
		
		for sprite in sorted(defaultRenderOrder, key=lambda sprite: sprite.Rect.Rect.centery):
			sprite.display(self.displaySurface,player,playerOffset)
		for sprite in lateRenderOrder:
			sprite.display(self.displaySurface,player,playerOffset)

class AudioManager(idManager.IDManager):
	def __init__(self,game):
		self.game = game
		self.activeSources = {}
		super().__init__(self.activeSources)
		
	def addSound(self, soundPath, pos, loop, follow):
		sound.Sound(self.game,soundPath=soundpath, pos=pos, loop=loop, follow=follow)
		self.addObject(self.activeSources,source)

	def removeObjectByID(self,id):
		channel = self.activeSources[id].channel
		sound.Sound._channel_to_source.pop(channel)
		super().removeObjectByID(id)
		

	def update(self, player):
		for source in list(self.activeSources.values()):
			source.update(player)
		for event in game.getEventList(sound.Sound.soundEndedEvent,[]):
			source = sound.Sound._channel_to_source.get(pygame.mixer.Channel(event.channel))
			self.removeObject(source)

class multiMedia:
	def __init__(game):
		self.displayManager = DisplayManager()
		self.audioManager = AudioManager(game)
		
	def addSound(self, soundPath, pos, loop=False, follow=None):
		self.audioManager.addSound(soundPath,pos,loop,follow)
		
	def update(self,player,clearTrash=True,updateAllGifs=False):
		self.displayManager.update(player,clearTrash=clearTrash,updateAllGifs=updateAllGifs)
		self.audioManager.update(player)
		
	def removeObject(self,object):
		self.displayManager.removeOBject(object)