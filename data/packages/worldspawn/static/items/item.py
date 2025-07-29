import default.modifiers
class Item:
	def __init__(self, name, max=32, modifiers=[default.modifiers.modifier("damage", 1), default.modifiers.modifier("attack_cooldown", 0.5)], toolType=None, color=None):
		self.toolType = toolType
		self.modifiers = modifiers
		self.name = name
		self.max = max
		self.color = color

	def applyModifiers(self,object,rightClicked=False,hand=False):
		modifiers.modifier.applyForList(self.modifiers,rightClicked,hand)

	def getName(self):
		return self.name
		
	def getMax(self):
		return self.max
		
	def getModifiers(self):
		return self.modifiers
		
	def getColor(self):
		return self.color

	def update(self):
		pass

	def __eq__(self, other):
		return self.toolType == other.toolType and self.modifiers == other.modifiers and self.item_name == other.item_name and self.max == other.max and self.color == other.color
		

class lootable:
	def __init__(self, itemID, count=1, chance=1.0):
		self.itemID = itemID
		self.count = count
		self.chance = chance
	def generateItem(self,seed):
		random.seed(seed)
		if random.random() < self.chance:
			if isinstance(self.itemID,set):
				random.seed(seed)
				return random.choice(list(self.itemID))
			return self.itemID
		return None

