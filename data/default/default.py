def setAttr(obj, path, value):
    attributes = path.split(".")
    for attr in attributes[:-1]:
        obj = getattr(obj, attr)
    setattr(obj, attributes[-1], value)

def getAttr(obj, path):
    attributes = path.split(".")
    for attr in attributes:
        obj = getattr(obj, attr)
    return obj