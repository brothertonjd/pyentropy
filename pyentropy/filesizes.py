import os
import math
import datetime
import matplotlib.pyplot as plt
import paramiko
import time
import OpenSSL
from sklearn import preprocessing
import matplotlib.dates as mpld
from PIL import Image

#sets up a connection to the app state database. I can write this data to an auth file for security purposes later.
ssh= paramiko.SSHClient()
transport=paramiko.Transport(("cs.appstate.edu", 22))
transport.connect(username="bee", password="cs.13,bee")
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ftp = paramiko.SFTPClient.from_transport(transport)

def ent(file):
    #calculated the shannon entropy for a given file- this is the total amount of "randomness" that we see in a file that we can measure by looking and predicting the values of each pixel in the video frame.
    totalent = 0.0
    
    #makes and or checks file so we dont have to recalculate entropy
    #needs work / is useless until we can store by date
   # if os.path.isfile(file):
    #    print(os.path)
     #   if os.path.isfile('prevent.txt'):
      #      print("are we getting here?")
       #     writer = open('prevent.txt','a')
        #    reader = open('prevent.txt','r')
         #   for l in reader: 
          #      if l == (file):
           #         var = reader.readline() 
            #        print(var)
             #       var = reader.readline()
              #      totalent = float(var)
              #
               #     print('filesize for file {file}  is {size}:'.format(file = file, size=os.path.getsize(file)))
                #    print('entropy for file {file}:'.format(file = file))
                 #   print(str(totalent))
                  #  return totalent
           # writer.write(file)
            
           # reader.close()
       # else :
        #    writer = open("prevent.txt","w")
         #   writer.write(file)
            
   
        
    path="temp/" + file 
    print("Calculating frames for file {file}...".format(file=file))
    owd = os.getcwd()  
    getframe = "ffmpeg -i " + path + " -s 640x480 -f image2 -hide_banner -nostats -q:v 2 ent/image%d.jpg"
    print(getframe)
    imgpath = "ent/"
    
    os.system(getframe)
    os.chdir(imgpath)
    divcount = 0
    print("\nCalculating entropy for file {file}...".format(file=file))
    for c,img in enumerate(os.listdir(os.getcwd())):
        if c % 10 == 0:
            divcount += 1
            totalent += videoent(img) 
  
           
        
        
    os.chdir(owd)
    print(os.getcwd())
     
    fsize = os.path.getsize(path)
    print('filesize for file {file}:'.format(file = file))
    print(fsize)
    #average total entropy
    totalent = totalent/divcount
    print ('entropy for file {file}:'.format(file = file))
    print (totalent)
    
    

    
    return totalent
#calculating entropy of one image from the video- credits to 
#http://code.activestate.com/recipes/577476-shannon-entropy-calculation/#c3
def videoent(img):

    im = Image.open(img)
    rgbHistogram = im.histogram()
    #Snannon Entropy for Red, Green, Blue
    for rgb in range(3):
        totalPixels = sum(rgbHistogram[rgb * 256 : (rgb + 1) * 256])
        ent = 0.0
        for col in range(rgb * 256, (rgb + 1) * 256):
            freq = float(rgbHistogram[col]) / totalPixels
            if freq > 0:
                ent = ent + freq * math.log(freq, 2)
        ent = -ent
        return ent
              

def filemover(filepath, date):
   
    #checks for temp folder and deletes contents to move all files from that date into it.
    for file in os.listdir("temp"):
        if file.endswith(".h264"):
            os.remove("temp/" + file)
    filelist = []
    #makes a list of file names for sorting as well as a corresponding list for entropies
    print("Gathering files ......")
    for file in ftp.listdir():
        filelist.append(file)    
        ftp.get(os.path.join(filepath, file),os.path.join( "temp", file))
        
    entlist=[]   
    filesizelist = []
    filelist = sorted(filelist)
    
    path = "temp/" 
    
    for file in filelist:
        fp = os.path.join(path, file)
        filesizelist.append(os.path.getsize(fp))
        entlist.append(ent(file)) 
    print(filesizelist)
    #taking away the file extension for our file list data & converting it to a time

    filelist = [os.path.splitext(each)[0] for each in filelist]
      
    plotlist = []
    for file in filelist:
        h,m,s=file.split("-")
        t = h + m + s
        print(t)
       
        plotlist.append(t)

       
    print(filelist)
    print(plotlist)
    
    plotter(plotlist, entlist, filesizelist, date)
def plotter(filelist, entlist, fsizelist, date):
    #gets the file and entropy lists and plots the data to a neat line graph
    print("Would you like your graph to show:")
    print("1) entropy and filesize values over time")
    print("2) a comparison of entropy vs filesize")
    
    plotselect = input("Please select a number:   ")
    fmin = min(fsizelist)
    fmax = max(fsizelist)
    xtimes = [datetime.datetime.strptime(str(int(times)), '%H%M%S') for times in filelist]
    normalized_fsize = [((sizes - fmin)/(fmax-fmin)) + 7 for sizes in fsizelist]
    if plotselect == "1":
        fline=plt.plot(xtimes, normalized_fsize, marker='o', color = 'green', label = "filesize")
        eline=plt.plot(xtimes, entlist, marker = 'o', label="entropy")
        plt.xlabel('Time')
        plt.legend(loc=4)
        plt.title('Entropy and Filesize Over Time for {date}'.format(date=date))
        plt.show()
        return
    if plotselect == "2":
        plt.plot(entlist, normalized_fsize, marker = 'o')
        plt.xlabel('Entropy')
        plt.ylabel('Filesize')
        plt.title('Filesize and Entropy Comparison for {date}'.format(date=date))
        plt.show()
if __name__ =="__main__":
 
    pi = input('input the number of the raspberry pi you want files from:    ')
    print('connecting to rpi{pi}'.format(pi=pi))
    p = "/usr/local/bee/beemon/rpi{pi}".format(pi=pi)
    ftp.chdir(p)
    for c,i in enumerate(sorted(ftp.listdir())):
        lstatout=str(ftp.lstat(i)).split()[0]
        if 'd' in lstatout:
            print (i)
    date= input("select a date from this list    ")
    p = "/usr/local/bee/beemon/rpi{pi}/{date}/video".format(pi=pi, date=date)
    ftp.chdir(p)
    filemover(p, date)
    
