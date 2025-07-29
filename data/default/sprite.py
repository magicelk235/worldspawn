import runnable,pygame,platform,rect,image,hitbox,events,math,displayType,default

class SpriteData:
	def __init__(self, hitbox,animations,save=[],clientSave=[]):
		self.hitbox = hitbox
		self.animations = animations
		self.save=["rect","objectType"]+save
		self.clientSave=["rect","objectType","currentAnimation"]+clientSave


class Sprite(pygame.sprite.Sprite,runnable.Runnable):
	eventRegister = events.EventRegister

	# event manager

	@staticmethod
	def moveEventTemplate(objectID):
		return pygame.event.Event(events.EventRegister.getID("move"),locals())

	@staticmethod
	def switchAnimationEventTemplate(newAnimation,oldAnimation,objectID):
		return pygame.event.Event(events.EventRegister.getID("switchAnimation"),locals())
	
	moveEvent = eventRegister.register("move",moveEventTemplate) 
	switchAnimationEvent = eventRegister.register("switchAnimation",switchAnimationEventTemplate)
	

	# custom classes
	class Vector:
		def __init__(self,angle,time):
			self.angle = angle%360
			self.time = time

		def getOpposedAngle(self):
			return self.angle+180

		def decTime(self):
			self.time -= 0.1
			return self.time == 0

		def update(self,sprite):
			sprite.addX(round(sprite.speed*math.cos(math.radians(self.angle))))
			sprite.addY(round(sprite.speed*math.sin(math.radians(self.angle))))
			return self.decTime()

		def mergeOpposeds(self,vectors):
			other = vectors.get(self.getOpposedAngle())
			if other != None:
				if self.time > other.time:
					vectors.pop(other.angle)
					self.time -= other.time
				elif self.time < other.time:
					vectors.pop(self.angle)
					other.time -= self.time
				else:
					vectors.pop(self.angle)
					vectors.pop(other.angle)

	class Animation:
		def __init__(self,imageData=image.ImageData(),displayType=DisplayType.topLeft,renderOrder=4,countDown=-1,weight=1,moveable=True):
			self.imageData = imageData
			self.displayType = displayType
			self.renderOrder = renderOrder
			self.countDown = countDown
			self.weight = weight
			self.moveable = moveable
		def load(self,sprite):
			sprite.addCountDown("animation",self.countDown)
			sprite.moveable = self.moveable
			sprite.rect.displayType = self.displayType
			sprite.rect.renderOrder = self.renderOrder
			sprite.image.setImageData(self.imageData)

		def getImageData(self):
			return self.imageData

		def weightCheck(self,other):
			return self.weight >= other.weight


	# object data
	objectData = SpriteData(hitbox.Hitbox(0, 0, 0, 0),{"default":Animation()})
	objectType = f"{self.__module__}.{self.__name__}"
	
	def __init__(self, game:platform.Platform, pos: tuple,dictData={}):
		pygame.sprite.Sprite.__init__(self,game)
		runnable.Runnable.__init__(self,game)
		self.game = game
		self.visible = True
		self.image: image.Image = image.Image(self,self.getAnimation().getImageData())
		size = self.image.get_size()
		self.vectors = {}
		self.speed = 1
		self.moveable = True
		self.rect = rect.Rect(pygame.rect.Rect(*pos[:2], *size), pos[2])
		self.hitbox:Rect = self.objectData.hitbox.getRect(pos)
		self.currentAnimation = "default"
		self.loadAnimation("default")
		self.dictManager(dictData)
		
	# vectors
	def addVector(self,angle,time) -> None:
		vector = self.Vector(angle,time)
		other = self.vectors.get(angle)
		if other != None:
			other.time += vector.time
		else:
			self.vectors[vector.angle] = vector
		vector.mergeOpposeds(self.vectors)
		
	def updateVectors(self) -> None:
		if self.moveable:
			if self.game.eventHappend(self.timerEvent):
				for vector in list(self.vectors.values()):
					vector.update(self)


	# animations

	def getAnimation(self,name:str="default") -> self.Animation:
		return self.objectData.animations[name]

	def loadCurrentAnimation(self) -> None:
		animation = self.getAnimation(self.currentAnimation)
		animation.load(self)
		
	def loadAnimation(self,name:str="default") -> None:
		self.addEvent(self.switchAnimationEventTemplate(name,self.currentAnimation,self.id))
		self.currentAnimation = name
		self.loadCurrentAnimation(self)

	def getCurrentAnimation(self) -> self.Animation:
		return self.getAnimation(self.currentAnimation)

	def updateAnimations(self) -> None:
		if self.game.eventHappend(self.timerEvent).self.countDownEnded("animation"):
			self.loadAnimation()

	def setAnimation(self,name) -> None:
		if self.getAnimation(name).weightCheck(self.getCurrentAnimation()):
			self.loadAnimation(name)
			
	def setUnvisible(self) -> None:
		self.visible = False

	def setVisible(self) -> None:
		self.visible = True

	def switchVisible(self) -> None:
		self.visible = not self.visible

	def isVisible(self) -> bool:
		return self.visible

	def display(self,displaySurf,player,displayOffset) -> None:
		if self.isVisible():
			self.displayImage(displayOffset,player,displayOffset)

	def displayImage(self,displaySurf:pygame,player,displayOffset) -> None:
		offset = self.rect.subPos(self.rect.subPos(self.getAxis(),self.image.getAlignmentOffset(self.getDisplayType)),self.rect.subPos(self.getAxis(),self.rect.getByDisplay())) - displayOffset
		self.image.display(displaySurf,offset)

	# rect/pos
		
	def setX(self,x:int) -> None:
		self.rect.rect.x = x
		self.visionRect.Rect.centerx = x
		self.objectData.hitbox.updateRect(self.hitbox, self.rect.getPos())
		self.game.postEvent(self.moveEventTemplate(self.id))

	def setY(self,y:int) -> None:
		self.rect.rect.y = y
		self.visionRect.Rect.centery = y
		self.objectData.hitbox.updateRect(self.hitbox, self.rect.getPos())
		self.game.postEvent(self.moveEventTemplate(self.id))
		
	def addX(self,x) -> None:
		self.setX(self.getX()+x)
		
	def addY(self,y) -> None:
		self.setY(self.getY()+y)

	def collideCheck(self,object:HitboxSprite) -> bool:
		return self.hitbox.collideRect(object.hitbox)

	def setPos(self,pos:tuple) -> None:
		self.setX(pos[0])
		self.setY(pos[1])
		self.setDimension(pos[2])
		
	def setDimension(self,dimension:str) -> None:
		self.rect.dimension = dimension
		self.visionRect.dimension = dimension
		self.hitbox.dimension = dimension
		self.game.postEvent(self.moveEventTemplate(self.id))

	def getX(self) -> int:
		return self.rect.rect.x
		
	def getY(self) -> int:
		return self.rect.rect.y

	def getPos(self) -> tuple:
		x,y = self.getAxis()
		return x,y,self.getDimension()
		
	def getAxis(self) -> tuple:
		return self.getX(),self.getY()

	def getDisplayType(self) -> displayType.DisplayType:
		return self.rect.displayType

	def getDimension(self) -> str:
		return self.rect.dimension

	# update/main

	def update(self) -> bool:
		self.updateTimers()
		self.updateVectors()
		return False
		

	# save/load/client

	def dictManager(self,data:dict[str,any]) -> None:
		if data != None:
			self.fromDict(data)
		
	def toDict(self) -> dict[str,any]:
		saveDict = {}
		for name in self.objectData.save:
			saveDict[name] = default.getAttr(self,name)
		return saveDict
			
	def toDictToClient(self) -> dict[str,any]:
		saveDict = {}
		for name in self.objectData.clientSave:
			saveDict[name] = default.getAttr(self,name)
		return saveDict
	
	def fromDict(self,data:dict[str,any]) -> None:
		for key in list(data.keys()):
			if key == "imageData":
				self.image.fromDict(data["imageData"])
			else:
				default.setAttr(self, key, data[key])