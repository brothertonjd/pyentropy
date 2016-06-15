import os
from math import log
import datetime
import matplotlib.pyplot as plt
import paramiko
import numpy as npy
from subprocess import call
from PIL import Image


freader = open('auth.txt', 'r')
conn = freader.read().splitlines()
host = conn[0]
port = conn[1]
usern = conn[2]
passw = conn[3]
#sets up a connection to the app state database. I can write this data to an auth file for security purposes later.
ssh= paramiko.SSHClient()
transport=paramiko.Transport((host, int(port)))
transport.connect(username= usern, password= passw)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ftp = paramiko.SFTPClient.from_transport(transport)

def isSingleFile(answer):
    if answer in ('y', 'Y', 'yes', 'Yes'):
        return True
    elif answer in ('n', 'N', 'no','No'):
        return False

def ent(filelist):
    entropylist = []
    
    #calculated the shannon entropy for a given file- this is the total amount of "randomness" that we see in a file that we can measure by looking and predicting the values of each pixel in the video frame.
    for file in filelist:
        
        totalent = 0.0    
        for f in os.listdir("ent"):
            if f.endswith(".jpg"):
                os.remove("ent/"+f)


        path="temp/" + file 
        print("Calculating frames for file {file}...".format(file=file))
        owd = os.getcwd()
        getframe = "ffmpeg -i " + path+ " -s 640x480 -f image2 -hide_banner -v 0 -q:v 2  ent/image%d.jpg"
    
        imgpath = "ent/"
    
        call(getframe, shell=True)
        os.chdir(imgpath)
        divcount = 0
        print("\nCalculating entropy for file {file}...".format(file=file))
        if len(filelist) > 1:
            for c,img in enumerate(os.listdir(os.getcwd())):
                if c % 16 == 1:
                    divcount += 1
                    totalent += videoent(img) 
        elif len(filelist) == 1:
            #Instead of getting entropy for every file, we use the entropy list to get the specific entropies for all of the images in a single file. 
            
            for img in os.listdir(os.getcwd()):
                entropylist.append(videoent(img))
            for x in entropylist:
                totalent= totalent + x
            print("Average entropy for file {file}:".format(file=file))
            print(totalent/1799)
            return entropylist
        
        
        os.chdir(owd)
    
     
        fsize = os.path.getsize(path)
        print('filesize for file {file}:'.format(file = file))
        print(fsize)
    #average total entropy
        totalent = totalent/divcount
        print ('average entropy for file {file}:'.format(file = file))
        print (totalent)
        entropylist.append(totalent)
        

    
    return entropylist
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
                ent = ent + freq * log(freq, 2)
        ent = -ent
        return ent
              

def filemover(filepath, date):
   
    #checks for temp folder and deletes contents to move all files from that date into it.
    answer = input("Would you like to calculate one single file?(y/n)")
    if isSingleFile(answer):
        for i in sorted(ftp.listdir()):
            lstatout=str(ftp.lstat(i)).split()[0]
            if 'd' not in lstatout:
                print (i)
        fy = input("select a file to calculate:   ")
     
    for file in os.listdir("temp"):
        if file.endswith(".h264"):
            os.remove("temp/" + file)
    
    filelist = []
    #makes a list of file names for sorting as well as a corresponding list for entropies
    print("Gathering files ......")
    if not isSingleFile(answer):
        filelist = [file for file in ftp.listdir()]
        for file in ftp.listdir():    
            ftp.get(os.path.join(filepath, file),os.path.join( "temp", file))
        print(os.listdir("temp"))
        filelist = sorted(filelist)
    else:
        filelist = [fy]
      
        ftp.get(os.path.join(filepath, fy),os.path.join("temp", fy))
        
    entlist=[]   
    filesizelist = []
    
    entlist= ent(filelist) 
    path = "/home/jon/pyentropy/pyentropy/temp/" 
    
    print(os.getcwd())
    for file in filelist:
        fp = os.path.join(path, file)
        filesizelist.append(os.path.getsize(fp))
        
    
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
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if len(filelist) != 1:
        while True: 
            print("Would you like your graph to show:")
            print("1) entropy and filesize values over time")
            print("2) a comparison of entropy vs filesize")

            plotselect = input("Please select a number:   ")
            if plotselect not in ('1', '2'):
                print("Please enter either 1 or 2")
                continue
            else:
                break
        xtimes = [datetime.datetime.strptime(str(int(times)), '%H%M%S') for times in filelist]
        enfsize=sorted(list(zip(filelist, fsizelist, entlist)))
        for (a,b,c) in enfsize:
            print("file:     ", a,"     filesize:     ",b,"     entropy:     ",c)    
        def onpick3(event):
            ind = event.ind
            print ('onpick3 scatter:', ind, npy.take(entlist, ind), npy.take(fsizelist, ind)) 
        if plotselect == "1":
            fmin = min(fsizelist)
            fmax = max(fsizelist)
            normalized_fsize = [((sizes - fmin)/(fmax-fmin)) + 7 for sizes in fsizelist]
            fline=ax.plot(xtimes, normalized_fsize, marker='o', color = 'green', label = "filesize")
            eline=ax.plot(xtimes, entlist, marker = 'o', label="entropy", picker=True)
      
            plt.xlabel('Time')
            plt.legend(loc=4)
            plt.title('Entropy and Filesize Over Time for {date}'.format(date=date))
            fig.canvas.mpl_connect('pick_event', onpick3)
            plt.show()
            return
        if plotselect == "2":
        
            ax.scatter(entlist, fsizelist, marker = 'o', picker = True)
            plt.xlabel('Entropy')
            plt.ylabel('Filesize')
            plt.title('Filesize and Entropy Comparison for {date}'.format(date=date))
            fig.canvas.mpl_connect('pick_event', onpick3)
            plt.show()
            return
    elif len(filelist) == 1:
        timelen = [x /30 for x in range(1,1800)]
        print(len(timelen))
        print(len(entlist))
        ax.scatter(timelen, entlist, marker = 'o')
        plt.show()
        return    
if __name__ =="__main__":
    ftp.chdir("/usr/local/bee/beemon")
    for i in sorted(ftp.listdir()):
        lstatout=str(ftp.lstat(i)).split()[0]
        if 'd' in lstatout:
            print (i)

    while True:
         try:
            pi = input('input the raspberry pi you want files from:    ')
            p = "/usr/local/bee/beemon/{pi}".format(pi=pi)
            ftp.chdir(p)   
         except FileNotFoundError:
            print("Invalid pi name, please enter a valid name")
            continue
         else:
            break
    print('connecting to {pi}'.format(pi=pi))
   # p = "/usr/local/bee/beemon/rpi{pi}".format(pi=pi)
    
    for i in sorted(ftp.listdir()):
        lstatout=str(ftp.lstat(i)).split()[0]
        if 'd' in lstatout:
            print (i)
    while True:
        try:
            date= input("select a date from this list    ")
            p = "/usr/local/bee/beemon/{pi}/{date}/video".format(pi=pi, date=date)
            ftp.chdir(p)
        except FileNotFoundError:
            print("The date is incorrect or not on this raspberry pi.")
            continue
        else:
            break
    filemover(p, date)
    
