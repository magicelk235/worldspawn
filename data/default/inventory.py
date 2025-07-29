import modifiers

class inventoryItem:
	def __init__(self, item, count=1):
		self.item = item
		self.count = count



	# checks
	def needsToBeEmpty(self):
		return isEmpty(self) and self.getName != None

	def sameName(self,name):
		return self.getName() == name

	def sameItemType(self,item):
		return self.sameName(item.getName())

	def isEmpty(self):
		return self.getCount() == 0



	# getters
	def getItemName(self):
		return self.getItem().getName()

	def getItem(self):
		return self.item

	def getCount(self):
		return self.count

	def getMax(self):
		return self.getItem().getMax()



	# count functions
	def setCount(self,count):
		self.count = count

	def addCount(self,count):
		if self.canAddCount(count):
			self.setCount(self.getCount()+count)
			return True
		return False

	def canAddCount(self,count):
		return self.getCount() + count <= self.getMax()

	def decCount(self,count):
		if self.canDecCount(count):
			self.setCount(self.getCount()-count)
			return True
		return False

	def canDecCount(self,count):
		return self.getCount() - count >= 0



	# inventory functions
	def copy(self, item):
		self.item = item.getItem()
		self.count = item.count

	def move(self,item):
		self.copy(item)
		item.clear()

	def clear(self,game):
		self.item = game.getItem("None")()
		self.count = 0
		
	def replace(self,item):
		self.count,item.count = item.count,self.count
		self.item,item.item = item.item,self.item

	def merge(self,item):
		if self.sameItemType(item):
			if self.canAddCount(item.getCount()):
				self.addCount(item.getCount())
				item.remove()
			else:
				item.decCount(self.getMax()-self.getCount())
				self.setCount(self.getMax())
			return True
		return False

	# modifiers

	def applyModifiers(self,object,rightClicked=False,hand=False):
		self.getItem().applyModifiers(object,rightClicked,hand)

	def __eq__(self, other):
		if isinstance(other,inventory_item):
			if other.count == self.count and other.item == self.item:
				return True
		return False

class Inventory:
	def __init__(self,w,h,owner,hasModifiers,graveTexture="grave"):
		self.inventory:list[inventoryItem] = [[None for i in range(w)]for j in range(h)]
		self.size = (w,h)
		self.graveTexture = graveTexture
		self.owner = owner
		self.hasModifiers = hasModifiers
		self.clearInventory()
		self.handPos = (4,4)



	# getters
	def getItem(self,w,h):
		return self.inventory[h][w]

	def getSize(self):
		return self.size
		
	def getH(self):
		return self.size[1]
		
	def getW(self):
		return self.size[0]

	def getHandItem(self):
		return self.getItem(*self.hand)

	def getItemByName(self, name):
		try:
			return self.getItem(*self.findItem(name))
		except:
			return None



	# setters
	def setSize(self,size):
		self.size = size
		
	def setH(self,h):
		self.size = (self.w,h)
		
	def setW(self,w):
		self.size = (w,self.h)



	# inventory functions
	def findItem(self, name):
		for w in range(self.getW()):
			for h in range(self.getH() - 1, -1, -1):
				if self.getItem(w,h).sameName(name):
					return [w, h]
		return None

	def canAddItemAt(w,h,item):
		if self.getItem(w,h).getItemName() != item.getItemName():
			return False
		return self.getItem(w,h).canAddCount(item.GetCount())

	def addItem(self, item):
		for h in range(self.getH() - 1, -1, -1):
			for w in range(self.getW()):
				if self.getItem(w,h).addCount(item.getCount()):
					self.applyModifiers()
					return True
		for h in range(self.getH() - 1, -1, -1):
			for w in range(self.getW()):
				if self.getItem(w,h).isEmpty():
					self.getItem(w,h).copy(item)
					self.applyModifiers()
					return True
		return False

	def removeItemByAmount(self, name, count):
		for h in range(self.getH() - 1, -1, -1):
			for w in range(self.getW()):
				if self.getItem(w,h).sameName(name) and self.getItem(w,h).decCount(count):
					self.applyModifiers()
					return True
		return False

	def removeAt(self,w,h):
		self.getItem(w,h).remove()
		self.applyModifiers()

	def removeItem(self, name):
		try:
			self.removeAt(self.findItem(name))
			return True
		except:
			return False

	def hasItemAt(self,w,h,name,count=-1):
		return self.getItem(w,h).sameName(name) and (count == -1 or self.getItem(w,h).canDecCount(count))

	def hasItem(self, name, count=-1):
		for h in range(self.getH() - 1, -1, -1):
			for w in range(self.getW()):
				if self.hasItemAt(w,h,name,count):
					return True
		return False

	def hasItemInHand(self, name, count=None):
		return self.hasItemAt(*self.handPos,name,count)

	def update(self):
		for row in self.inventory:
			for item in row:
				if item.needsToBeEmpty():
					item.remove()
		self.applyModifiers()

	def clearInventory(self):
		for w in range(self.getW()):
			for h in range(self.getH()):
				self.getItem(w,h).remove()
		self.applyModifiers()



	# modifiers
	def applyModifiers(self, rightClicked=False):
		self.update()
		self.owner.resetModifiers()
		self.getHandItem().applyModifiers(self.owner,rightClicked,True)
		usedNames = {}
		for row in self.inventory:
			for item in row:
				if item.getName() not in usedNames:
					usedNames.add(item.getName())
					item.applyModifiers(self.owner,rightClicked)


	# interaction
	def interact(self,w1,h1,w2,h2):
		if not self.getItem(w1,h1).merge(self.getItem(w2,h2)):
			self.getItem(w1,h1).replace(self.getItem(w2,h2))



	# load/copy function

	def copy(self,other):
		self.inventory = other.inventory
		self.w = other.w
		self.h = other.h
		self.owner = other.owner
		self.handPos =  other.handPos

	# def convertToGrave(self, game):
	# 	lootable_list = []
	# 	for row in self.inventory:
	# 		for items in row:
	# 			if items.item_data.item_name != None:
	# 				lootable_list.append(lootable(items.item_data,items.count))
	# 	if lootable_list != []:
	# 		default.create_object(game.objects, objects.object(game, self.owner.Rect.Rect.center, self.owner.Rect.dimension, objects.object_data(self.graveTexture, lootable_list)))
	# 	self.clearInventory()

	# def drop(self,w,h,game):
	# 	if self.inventory[y][x].itemData.item_name != None:
	# 		default.create_object(game.drops, item(game, (self.owner.Rect.Rect.x + 30, self.owner.Rect.Rect.y + 30), self.owner.Rect.dimension, self.inventory[y][x].count, self.inventory[y][x].itemData))
	# 		self.remove_at(x,y)
	# 		self.apply_modifiers()
