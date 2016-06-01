import os
import math
import datetime
import matplotlib
import paramiko

ssh= paramiko.SSHClient()
transport=paramiko.Transport(("cs.appstate.edu", 22))
transport.connect(username="bee", password="cs.13,bee")
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ftp = paramiko.SFTPClient.from_transport(transport)
writer = open('prevent.txt', 'a')
def ent(file):
    totalent = 0.0
    global writer
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
              
                    print('filesize for file {file}  is {size}:'.format(file = file, size=os.path.getsize(file)))
                    print('entropy for file {file}:'.format(file = file))
                    print(str(totalent))
                    return totalent
            writer.write(file)
            writer.write('\n')
            reader.close()
        else :
            writer = open("prevent.txt","w")
            writer.write(file)
            writer.write('\n')
   
        
    path="temp/" + file 
    #puts file in byte array
    fread = open(path, 'rb')
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
    
    return totalent

def freq(array):
    #get frequency of bytes
    frequencies= [0] *256
   
    for i in array:
       frequencies[i] += 1
  
    return frequencies

def filemover(filepath):
    #if not os.path.isdir("temp"):
     #   os.makedirs("temp")
    for file in os.listdir("temp"):
        if file.endswith(".h264"):
            os.remove("temp/" + file)
    for file in ftp.listdir():
        ftp.get(os.path.join(filepath, file),os.path.join( "temp", file))
    #filelist=filter(os.path.isfile, os.listdir("temp"))
    #print (filelist)
    #filelist = [os.path.join("/temp", f) for f in filelist]
    #print(filelist)
    #filelist.sort(key=lambda x: os.path.getmtime(x))
    for file in ftp.listdir():
        ent(file) 

def plotter(date):
    return

if __name__ =="__main__":
 
    pi = input('input the number of the raspberry pi you want files from:    ')
    print('connecting to rpi{pi}'.format(pi=pi))
    p = "/usr/local/bee/beemon/rpi{pi}".format(pi=pi)
    ftp.chdir(p)
    for i in sorted(ftp.listdir()):
        lstatout=str(ftp.lstat(i)).split()[0]
        if 'd' in lstatout:
            print (i)
    date= input("select a date from this list    ")
    p = "/usr/local/bee/beemon/rpi{pi}/{date}/video".format(pi=pi, date=date)
    ftp.chdir(p)
    filemover(p)
    writer.close() 
