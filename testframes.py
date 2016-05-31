import math
import os

def getFile(filename):
    getframe = "avconv -i " + filename + " -s 640x480 -f image2 -ss 00:00:00 -vframes 1 -q:v 2 image%03d.jpg"
    os.system(getframe)
    return

def makefrarray(image):
    f = open(image, "rb")
    byteArr = list(map(ord, f.read())
    f.close()
    fileSize = len(byteArr)
    print ('File size in bytes:')
    print (fileSize)
    print ()


image1size = os.path.getsize('img001.jpg')
image2size = os.path.getsize('img002.jpg')
print('')
print( image1size)
print('')
print(image2size)

def H(size):
	entropy = size*math.log(size, 2)
	return entropy	

foo = H(image1size)
bar = H(image2size)
print(foo)
print(bar)

