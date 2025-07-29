import pygame,default

class Platform:
	def __init__(self):
		self.cameraGroup = gui.CameraGroup()
		self.systemEventDict = {}
		self.allTypes = {}
		self.objects = {}
		self.entities = {}
		self.drops = {}
		self.projectiles = {}
		self.particles = {}
		self.events = {}
		self.players = {}
		self.guis = {}
		self.usedIDs = set()
		self.typeDict = {}

	def objectExist(objectID):
		return self.allTypes.get(objectID,0) != 0

	def getObjectByID(self,id):
		return self.allTypes.get(id)

	def loadTypes(self):
		from runnableTypes import getRunnableTypes
		typeDict = getRunnableTypes()
		for dictType in list(typeDict.keys()):
			setattr(self,typeDict[dictType],{})
			self.typeDict[dictType] = getattr(self,typeDict[dictType])

	def getTypeByPath(self,path:str):
		try:
			module = importlib.import_module(f"data.{path}")
			return getattr(module, path.split(".")[-1])
		except:
			newPath = ""
			for char in path.split("."):
				newPath = newPath+char+"."
			module = importlib.import_module(f"data.{newPath[:-1]}")
			return getattr(module, path.split(".")[-1])

	def loadTypesGetter(self, type,objectType):
		# Define the getter function specific to this type
		def getter(id):
			try:
				# Dynamically import module: data.<type>.<id>
				module = importlib.import_module(f"data.{objectType}.{type}.{id}")
				return getattr(module, id)
			except Exception as e:
				raise ImportError(f"Failed to load class '{id}' from 'data.{type_name}.{id}': {e}")

		# Format method name: e.g., getPlayers
		method_name = f"get{type_name.capitalize()}"

		# Attach the function to the object
		setattr(self, method_name, getter)

	def main(self):...

	def appendToDictByType(self,object,objectID,type=None):
		self.usedIDs.add(id)
		self.allTypes[objectID] = object
		self.getDictByType(object,type)[objectID] = object

	def getDictByType(self,object,type=None):
		type = type if type != None else type(object)
		for objectType in list(self.typeDict.keys()):
			if issubclass(type,objectType):
				return self.typeDict[objectType]

	@staticmethod
	def CreateObjectForExternalDict(objectDict,object):
		objectDict[Platform.generateID(objectDict)] = object

	def removeObjectByID(self,id):
		self.removeObject(self.allTypes[id])

	def removeObject(self,object):
		del self.getDictByType(object)[object.id]
		del self.allTypes[object.id]

				
	def createObject(self,object,forceType=None):
		self.loadObject(object,self.generateID(self.usedIDs),forceType)

	def loadObject(self,object,id,forceType=None):
		self.appendToDictByType(object,id,forceType)

class OnlinePlatform(Platform):
	def __init__(self,ip,port,path):
		self.ip = ip
		self.port = port
		self.path = path
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ipCryptKey = bidict.bidict({"0": "h", "1": "g", "2": "y", "3": "a", "4": "j", "5": "m", "6": "c", "7": "t", "8": "x", "9": "s", ".": "f",":": "w"})
		pygame.display.set_caption(f"WorldSpawn Code:{self.ip}")
		pygame.display.set_icon(pygame.image.load(default.resource_path("assets/gui/world_icon.png")))

	def encryptIp(self):
		cryptedIp = ""
		for char in self.ip:
			cryptedIp += self.ipCryptKey[char]
		return cryptedIp

	def decryptIp(self,cryptedIp):
		self.ip = ""
		for char in cryptedIp:
			self.ip += self.ipCryptKey[char]

	def receive(self):
		rawPacketLen = recvall(sock, 4)
		if not rawPacketLen:
			return None
		packetLen = struct.unpack('>I', rawPacketLen)[0]
		data = pickle.loads(recvall(self.socket, packetLen))
		return data

	def send(self, packet):
		packet = pickle.dumps(packet)
		packet = struct.pack('>I', len(packet)) + packet
		self.socket.sendall(packet)
