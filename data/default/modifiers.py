import default,events
class modifier:
	def __init__(self,name,amount,setMode=True,handNeeded=True,rightClick=False,chooseBigger=True,percent=False):
		"""
		:param name: damage,shield,max_health
		:param amount: either int or float(%)
		:param set: false for add, true for set
		:param hand_needed: if the modifyer is needed to be on hand to apply
		:param right_click: if the modifier should apply on right click
		"""
		self.name = name
		self.amount = amount
		self.setMode = setMode
		self.handNeeded = handNeeded
		self.rightClick = rightClick
		self.chooseBigger = chooseBigger
		self.percent = percent

	def __eq__(self, other):
		if isinstance(other,modifier):
			return self.__hash__() == other.__hash__()
		return False

	@staticmethod
	def find(name,list):
		for object in list:
			if object.name == name:
				return object
			
	@staticmethod
	def get(name,list):
		for object in list:
			if object.name == name:
				return object.amount

	def __hash__(self):
		return hash(tuple(self.__dict__.items()))

	def canBeApllied(self,rightClicked,hand):
		if (self.rightClick and not rightClick):
			return False
		if (self.hand and not hand):
			return False
		return True

	def apply(self,object,rightClicked=False,hand=False):
		if self.canBeApllied(rightClicked,hand):
				if self.setMode:
					if self.chooseBigger and default.getAttr(object,self.name) < self.amount:
						default.setAttr(object,self.name,self.amount)
					elif not self.chooseBigger:
						default.setSttr(object, self.name, self.amount)
				else:
					if self.percent:
						if isinstance(default.getAttr(object,self.name),float):
							value = default.getAttr(object,self.name)*(self.amount+1.0)
							value = int(value*10)
							default.setAttr(object, self.name,value)
						else:
							default.setAttr(object,self.name,int(default.getAttr(object,self.name)*(self.amount+1.0)))
					else:
						default.setAttr(object, self.name, default.getAttr(object, self.name)+self.amount)
	@staticmethod
	def applyForList(modifiers,object,rightClicked=False,hand=False):
		for modifier in modifiers:
			modifier.apply(object,rightClicked,hand)

class TemporaryModifier:
	def __init__(self,modifier,cooldown):
		self.modifier = modifier
		self.cooldown = cooldown

	def update(self,game):
		if game.eventHappend(events.timer):
			self.cooldown -= 1
			if self.cooldown == 0:
				return True

	def __eq__(self, other):
		if isinstance(other,TemporaryModifier):
			return self.__hash__() == other.__hash__()
		return False

	def __hash__(self):
		return self.modifier.__hash__()
		
	def apply(object,rightClicked,hand):
		self.modifier.apply(object,rightClicked,hand)