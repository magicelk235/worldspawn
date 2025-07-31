import os,pygame,loader
from PIL import Image

def loadImage(path):
    if ".png" in path:
        return [[pygame.image.load(path).convert_alpha(),1]]
    elif ".gif" in path:
        gif = Image.open(path)
        frames = []
        for frame in range(gif.n_frames):
            gif.seek(frame)
            if frame == 0:
                frames.append([pygame.image.load(path).convert_alpha(), gif.info.get("duration", 1000)*0.001])
            else:
                frames.append([pygame.image.frombytes(gif.tobytes(), gif.size, gif.mode).convert_alpha(), gif.info["duration"]*.001])
        gif.close()
        return frames

path = "assets"
validExtensions = {".png", ".gif"}
global images
images = {}
loader.load(path,validExtensions,images,loadImage)

def getImage(path):
    return images.get(path,images["gui/falied"])
