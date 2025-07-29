class IDManager:
	def __init__(self,mainGroup):
		self.usedIDs = set()
		self.group = mainGroup
		
	def idUsed(self,id):
		return id in self.usedIDs
		
	def generateID(self):
		while True:
			id = uuid.uuid4()
			if not self.idUsed(id):
				return id
		
	def addObject(self,object):
		self.addObjectByID(object,self.generateID())
		
	def addObjectByID(self,object,id):
		self.usedIDs.add(id)
		self.group[id] = object
		object.setID(id)
		
	def removeOBject(self,object):
		self.removeObjectByID(object)
		
	def removeObjectByID(self,id):
		self.usedIDs.remove(id)
		self.group.pop(id)