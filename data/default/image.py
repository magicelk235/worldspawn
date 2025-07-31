import pygame,gif_pygame,rect,default,default,displayType,media.imageLoader

class ImageData:
	def __init__(self,path=None,scaleSize=None,cutSize=None,flipX=None,flipY=None,color=None,angle=None,factoredSize=None,resetGif=False):
		self.path = path
		self.scaleSize = scaleSize
		self.cutSize = cutSize
		self.flipX = flipX
		self.flipY = flipY
		self.color = color
		self.angle = angle
		self.factoredSize = factoredSize
		self.resetGif = resetGif


	# hash for storing
	def toHash(self):
		return "".join(self.__dict__.values())

	def getValue(self,sprite,value):
		if str(default.getAttr(value))[0] == "@":
			return default.getAttr(sprite,default.getAttr(self,value)[1:])
		else:
			return default.getAttr(self,value)
	# loaded
	def setData(self,name,image,sprite):
		if default.getAttr(self,name) != None:
			if self.getValue(name) != default.getAttr(image,name):
				default.setAttr(image,name,self.getValue(name))
		
	def load(self,image,sprite):
		keys = ["path","scaleSize","cutSize","flipX","flipY","color","angle","factoredSize"]
		for key in keys:
			self.setData(key,image,sprite)

class Image:
	def __init__(self,sprite,imageData):
		self.sprite = sprite
		self.path = "worldspawn/gui/None"
		self.scaleSize = None
		self.cutSize = None
		self.flipX = False
		self.flipY = False
		self.color = (0,0,0,0)
		self.angle = 0
		self.factoredSize = 1
		self.image = None
		self.imageData = imageData
		self._cache = {}
		self.loadImage()
		


	# data setter
	def setImageData(self,imageData):
		self.imageData = imageData
		self.loadImage()


	def toHash(self):
		return self.imageData.toHash()+str(self.image.frame)

	def loadImage(self):
		self.imageData.load(self)
		frame = 0
		frame_time = 0
		if self.image and not self.imageData.resetGif:
			frame = self.image.frame
			frame_time = self.image.frame_time
		self.image = gif_pygame.GIFPygame(media.imageLoader.getImage(self.path))
		self.image.frame = frame
		self.image.frame_time = frame_time
		if self.cutSize == None:
			self.cutSize = self.image.get_size()
		if self.scaleSize == None:
			self.scaleSize = self.image.get_size()


	# display
	def getAlignmentOffset(self,targetPoint,basePoint=displayType.DisplayType.topLeft):
		tempRect = self.image.get_rect(**{basePoint:(0,0)})
		base = pygame.math.Vector2(tempRect.topleft)
		target = pygame.math.Vector2(default.getAttr(tempRect,targetPoint))
		offset = target - base
		return offset



	def getRawImage(self):
		self.imageData.load(self,self.sprite)
		try:
			return self._cache[self.imageData.toHash()]
		except:
			image = self.image.blit_ready().copy()
			image = pygame.transform.scale(image,self.scaleSize)
			self.cutImage(image)
			image = pygame.transform.scale_by(image,self.factoredSize)
			image.fill(self.color,special_flags=pygame.BLEND_RGBA_MULT)
			image = pygame.transform.flip(image,self.flipX,self.flipY)
			image = pygame.transform.rotate(image,self.angle)
			self._cache[self.ToHash()] = image
			return image

	def display(self, displaySurf, pos):
		rawImage = self.getRawImage() 
		displaySurf.blit(self.image.blit_ready(), pos)


	def cutSize(self,image):
		image.subsurface(pygame.Rect(0, 0, *self.cutSize))