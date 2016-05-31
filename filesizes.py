import os
import math
import datetime
#import matplotlib



def ent(file):
    totalent = 0.0
    #makes and or checks file so we dont have to recalculate entropy
    if os.path.isfile(file):
        if os.path.isfile('prevent.txt'):
            writer = open('prevent.txt','a')
            reader = open('prevent.txt','r')
            for l in reader: 
                if l == (file + '\n'):
                    var = reader.readline() 
                    print(var)
                    var = reader.readline()
                    totalent = float(var)
                    print('entropy for file {file}:'.format(file = file))
                    print(str(totalent))
                    return
            writer.write(file)
            writer.write('\n')
            reader.close()
        elif os.path.isfile(file) :
            writer = open("prevent.txt","w")
            writer.write(file)
            writer.write('\n')
   
        
    
    #puts file in byte array
    fread = open(file, 'rb')
    barr = bytearray(fread.read())
   
    fread.close()
    fsize = len(barr)
    print('filesize for file {file}:'.format(file = file))
    print(fsize)
    frequ = freq(barr)

    #shannon entropy 
  
    for v in frequ:
        if v > 0:
            fr = float(v) / fsize  
            totalent += fr * math.log(fr, 2)
    totalent = -totalent
    print()
    print ('entropy for file {file}:'.format(file = file))
    print (totalent)
    print('The minimum file size possible given this entropy is:')
    print((totalent * fsize)/8)
    writer.write('\n')
    writer.write(str(totalent) + '\n')
    writer.close()

def freq(array):
    #get frequency of bytes
    frequencies= [0] *256
    print(frequencies)
    for i in array:
       frequencies[i] += 1
    print(frequencies)
    return frequencies
    
#unused
def getFilesize(file, path=None):
    print(os.path)
    print(os.path.abspath(path))
    print(os.listdir(path))
    if file in os.listdir(path):
        print (os.path.getsize(file))
    elif os.path.isfile(path + file):
        print('wow!')

#unused
def testsssss():
    for file in sorted(os.listdir("aeiou")):
        path = "aeiou/" + file
        s = file , os.path.getsize(path)
        print(s)

if __name__ == '__main__':
    ent('19-02-17.h264')
    ent('08-59-38.h264')
   # for file in sorted(os.listdir("aeiou")):
    #    path = "aeiou/" + file
    #    s = file , os.path.getsize(path)
     #   print(s)
 
