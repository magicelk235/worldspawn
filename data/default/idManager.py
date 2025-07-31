import uuid
class IDManager:
	def __init__(self,mainGroup:dict):
		self.usedIDs = set()
		self.group:dict = mainGroup
		
	def idUsed(self,id:str) -> bool:
		return id in self.usedIDs
		
	def generateID(self) -> str:
		while True:
			id = uuid.uuid4()
			if not self.idUsed(id):
				return id
		
	def getObject(self,id:str) -> any:
		return self.group.get(id)

	def addObject(self,object) -> None:
		self.addObjectByID(object,self.generateID())
		
	def addObjectByID(self,object,id:str) -> None:
		self.usedIDs.add(id)
		self.group[id] = object
		object.setID(id)
		
	def objectExist(self,id:str) -> bool:
		return self.idUsed(id)

	def removeOBject(self,object) -> None:
		self.removeObjectByID(object)
		
	def removeObjectByID(self,id) -> None:
		self.usedIDs.remove(id)
		self.group.pop(id)