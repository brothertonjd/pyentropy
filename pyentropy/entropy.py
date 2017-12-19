import os
from math import log
import datetime
import matplotlib.pyplot as plt
import paramiko
from writeTo import writeTo
import numpy as npy
from subprocess import call
from PIL import Image
from scipy import stats
from HighLowEntImg import HighLowEnt

answer = None
date = None
pi = None
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
widg = None
calcSnr = False
#calculating entropy if the user has selected to choose from local files. Skips the step of getting files from the server
def localent(filelist, filepath):
    global calcSnr
    snrCheck =input("Do you want to calculate snr?(y/n)")
    if snrCheck in ("y","Y","yes", "Yes", "YES"):
        calcSnr = True
    print(calcSnr)
    entropylist=[]
    snrlist = []
    #creates a temporary directory for storing images of videos
    print(os.getcwd())
    if not os.path.exists("ent"):
            os.makedirs("ent")
    for file in filelist:
        totalent = 0.0
        totalsnr = 0.0
        divcount=0
        owd = os.getcwd() #brings us back to the current working directory for filesize calculation
        ptemp = filepath +file 
        #clears past images from past videos
        for f in os.listdir("ent"):
            if f.endswith(".jpg"):
                os.remove("ent/"+f)

        print("Calculating frames for file {file}...".format(file=file))
        #gets each video frame and stores it
        getframe = "ffmpeg -i " + ptemp + " -s 640x480  -vf format=gray -f image2 -hide_banner  -q:v 2  /home/jon/pyentropy/pyentropy/ent/image%d.jpg"
        call(getframe, shell=True)
        os.chdir("/home/jon/pyentropy/pyentropy/ent/")
        print("\nCalculating entropy for file {file}...".format(file=file))
        
        if len(filelist) > 1:
            for c,img in enumerate(os.listdir(os.getcwd())):
                #only calculates entropy for every 16th image, this number can be adjusted for speed, but 16 is pretty accurate.
                if c % 16 != 17:
                    divcount += 1
                    vident, vidsnr = videoent(img)
                    totalent += vident
                    totalsnr += vidsnr
                     
        elif len(filelist) == 1:
            #Instead of getting entropy for every file, we use the entropy list to get the specific entropies for all of the images in a single file. 
            
            for img in sorted(os.listdir(os.getcwd())):
                #gets video entropy for the video
                print(img)
                vident, vidsnr = videoent(img)
                entropylist.append(vident)
                snrlist.append(vidsnr)
            for x in entropylist:
                
                totalent= totalent + x
            print(totalent)
            divcount = len(list(f for f in os.listdir('.')))
            print(divcount)
            print("Average entropy for file {file}:".format(file=file))
            print(totalent/divcount)
            return entropylist, snrlist
#mark a
        os.chdir(owd)#unsure what this does tbh...
        #fsize = os.path.getsize(ptemp)
        #print('filesize for file {file}:'.format(file = file))
        #print(fsize)
        
        #average total entropy
        totalent = totalent/divcount
        totalsnr = totalsnr/divcount
        print ('average entropy for file {file}:'.format(file = file))
        print (totalent)
        print("Average snr for file {file}:".format(file=file))
        print(totalsnr)
        entropylist.append(totalent)
        snrlist.append(totalsnr)
    #removes temporary folder for video images
    for f in os.listdir("ent"):
        if f.endswith(".jpg"):
            os.remove("ent/"+f)
    return entropylist, snrlist
        
        
        
def ent(filelist):
    global calcSnr
    entropylist = []
    snrlist = []
    snrCheck =input("Do you want to calculate snr?(y/n)")
    if snrCheck in ("y","Y","yes", "Yes", "YES"):
        calcSnr = True
    print(calcSnr)
    #calculated the shannon entropy for a given file- this is the total amount of "randomness" that we see in a file that we can measure by looking and predicting the values of each pixel in the video frame.
    for file in filelist:
        totalent = 0.0    
        totalsnr = 0.0 
        path="temp/" + file 
        print("Calculating frames for file {file}...".format(file=file))
        owd = os.getcwd()
        getframe = "ffmpeg -i " + path+ " -s 640x480 -vf format=gray -f image2 -hide_banner -c:v mjpeg -q:v 2  ent/image%04d.jpg"
        imgpath = "ent/"
        call(getframe, shell=True)
        os.chdir(imgpath)
        divcount = 0
        print("\nCalculating entropy for file {file}...".format(file=file))
        #caluclates for multiple remote files
        if len(filelist) > 1:
            for c,img in enumerate(os.listdir(os.getcwd())):
                #gets every 16th image for speed purposes
                if os.path.isfile(img):
                    divcount += 1
                    vident, vidsnr = videoent(img)
                    totalent += vident
                    if calcSnr:
                        totalsnr += vidsnr
        elif len(filelist) == 1:
            #Instead of getting entropy for every file, we use the entropy list to get the specific entropies for all of the images in a single file. 
            print(os.getcwd())            
            for img in sorted(os.listdir(os.getcwd())):
                print(img)
                vident, vidsnr = videoent(img)
                entropylist.append(vident)
                if calcSnr:
                    snrlist.append(vidsnr)
            divcount = len(entropylist)
            print(entropylist)
            HighLowEnt(entropylist)
            for x in entropylist:
                totalent= totalent + x
            if calcSnr:
                for x in snrlist:
                    totalsnr = totalsnr + x
            print(totalent)
            if totalsnr > 0:
                print(totalsnr)
            print(divcount)
            print("Average entropy for file {file}:".format(file=file))
            print(totalent/divcount)
            if totalsnr > 0:
                print("Average snr for file {file}:".format(file=file))
                print(totalsnr/divcount)
            print(os.getcwd())
            #for f in os.listdir("."):
             #   if f.endswith(".jpg"):
              #      os.remove(f)
            return entropylist, snrlist
        
        
        os.chdir(owd)
    
     #commented out filesize portions of ent calculation since it occurs later during plotting
        #fsize = os.path.getsize(path)
        #print('filesize for file {file}:'.format(file = file))
        #print(fsize)
    #average total entropy
        totalent = totalent/divcount
        if totalsnr > 0:
            totalsnr = totalsnr/divcount
        print ('average entropy for file {file}:'.format(file = file))
        print (totalent)
        entropylist.append(totalent)
        if totalsnr > 0:
            snrlist.append(totalsnr)
        

    #for f in os.listdir("ent"):
	    #if f.endswith(".jpg"):
		    #os.remove("ent/"+f)
    return entropylist, snrlist
#calculating entropy of one image from the video- credits to 
#http://code.activestate.com/recipes/577476-shannon-entropy-calculation/#c3

def videoent(img):
    global calcSnr
    im = Image.open(img)
    num = 0
    if calcSnr:
        num = stats.signaltonoise(im, None, 0)
        print(num)
    rgbHistogram = im.histogram()
    totalPixels = sum(rgbHistogram[0:256])
    ent = 0.0
    for col in range(0, 256):
        freq = float(rgbHistogram[col])/ totalPixels
        if freq > 0:
            ent = ent + freq * log(freq, 2)
    ent = -ent
    return ent,num



def localmover(fp):
    global widg
    answer = input("Would you like to calculate one single file?(y/n)   ")
    if answer in ('y', 'Y', 'yes', 'Yes'):
        answer = True
    elif answer in ('n', 'N', 'no','No'):
        answer = False

    if answer:
        print(os.getcwd())
        for i in sorted(os.listdir()):
            if i.endswith(".h264"):print(i)
        ftc = input("Please select a file:   ")
        filelist = [ftc]
        
    else:
        filelist = []
        for file in os.listdir(fp):
            if file.endswith(".h264"): 
                filelist.append(file)
        filelist = sorted(filelist)
    entlist = []
    snrlist= []
    filesizelist= []
    entlist, snrlist = localent(filelist, fp)
    for file in filelist:
        fip = os.path.join(fp, file)
        filesizelist.append(os.path.getsize(fip))
    fylist = [os.path.splitext(each)[0] for each in filelist]
    plotlist = []
    for file in fylist:
        h,m,s=file.split("-")
        t = h + m + s
        print(t)

        plotlist.append(t)


    print(len(snrlist))
    if widg == 1:
        return fylist, entlist, filesizelist, snrlist
    plotter(fylist, entlist, filesizelist, snrlist)

#for remote selection
def filemover(filepath, date):
    global widg
    filelist = []
    #checks for temp folder and deletes contents to move all files from that date into it.
    for file in os.listdir("temp"):
        if file.endswith(".h264"):
            os.remove("temp/" + file)
    
   
    answer = input("Would you like to calculate one single file?(y/n)   ")
     #makes a list of file names for sorting as well as a corresponding list for entropies
    if answer in ('y', 'Y', 'yes', 'Yes'):
        answer = True
    elif answer in ('n', 'N', 'no','No'):
        answer = False

    print("Gathering files ......")
    if answer:
        for i in sorted(ftp.listdir()):
            lstatout=str(ftp.lstat(i)).split()[0]
            if 'd' not in lstatout:
                print (i)
        fy = input("select a file to calculate:   ")
        filelist = [fy]
        print(filelist)
        ftp.get(os.path.join(filepath, fy),os.path.join("temp", fy))
  
    
    else:
        filelist = [file for file in ftp.listdir()]
        for file in ftp.listdir():    
            ftp.get(os.path.join(filepath, file),os.path.join( "temp", file))
        filelist = sorted(filelist)
    
        
        
    entlist=[]   
    filesizelist = []
    snrlist = []
    entlist, snrlist = ent(filelist) 
    path = "/home/jon/pyentropy/pyentropy/temp/" 
    
    print(os.getcwd())
    #gets file size for each video for plotting purposes?
    for file in filelist:
        fp = os.path.join(path, file)
        filesizelist.append(os.path.getsize(fp))
        
    
    #taking away the file extension for our file list data & converting it to a time
    
    fylist = [os.path.splitext(each)[0] for each in filelist]
    print(fylist)  
    plotlist = []
    for file in fylist:
        h,m,s=file.split("-")
        t = h + m + s
        plotlist.append(t)
    print(plotlist)
    entcount = 0
    totalentday = 0
    #total average entropy for the whole day
    for i in entlist:
        totalentday += i
        entcount += 1
    
    print("Entropy for " + date + ":")
    print(totalentday/entcount)
    print(widg)
    print(fylist)
    print(entlist)
    print(filesizelist)
    print(snrlist)
    if widg == 1:
         return fylist, entlist, filesizelist, snrlist
    plotter(fylist, entlist, filesizelist, snrlist)
    return

def plotter(filelist, entlist, fsizelist, snrlist):
    global date
    global pi
    #gets the file and entropy lists and plots the data to a neat line graph
    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    plotlist = []
    for fyle in filelist:
        h,m,s=fyle.split("-")
        t = h + m + s
        plotlist.append(t)
    #basically checks if it's a single file
    if len(filelist) > 1: #if not a single file
        while True: 
            print("1) entropy and filesize values over time")
            print("2) a comparison of entropy vs filesize")

            plotselect = input("Please select a number:   ")
            if plotselect not in ('1', '2'):
                print("Please enter either 1 or 2")
                continue
            else:
                break
        pat = os.getcwd() # for local file path
        laziness = []
        for x in plotlist:
            laziness.append(datetime.datetime.strptime(str(int(x)), '%H%M%S'))
        xtimes = npy.array([datetime.datetime.strptime(times,'%H-%M-%S').time() for times in filelist])#changes a concatenated string to a datetime
        xtimes = [str(time) for time in xtimes]
        count = list(range(len(filelist)))
        print(xtimes)
        print(laziness)
        print(pat)
        #lists the files, entropies, and filesizes for each file
        enfsize=sorted(list(zip(count,filelist, fsizelist, entlist, snrlist)))
        print(enfsize)
        print(date)
        bloop = writeTo(enfsize, pat, date)
        bloop.writeTo(enfsize, pat, date)
        for (g,a,b,c, d) in enfsize:
                print("",g,"    file:     ", a,"     filesize:     ",b,"     entropy:     ",c,"     snr:    ",d)
        #a selector to be used when clicking on a graph. You can click and it will show current coordinates of the click
        print("select a point on the graph, the point will provide information as follows: entropy,filesize,time")
        def onpick3(event):
            ind = event.ind
            print ('onpick3 scatter:', ind, npy.take(entlist, ind), npy.take(fsizelist, ind), npy.take(xtimes, ind)) 
        select1xaxis = [int(i) for i in plotlist]
        #entropy and filesize values over time
        if plotselect == "1":
            fmin = min(fsizelist)
            fmax = max(fsizelist)
            #normalized to provide a better looking graph that helps the user correlate changes in filesizes and entropies of the same files
            normalized_fsize = [((sizes - fmin)/(fmax-fmin)) + 7 for sizes in fsizelist]
            fline=ax.plot(laziness, normalized_fsize, marker='o', color = 'green', label = "filesize")
            plt.xticks(laziness, xtimes, rotation=90)
            eline=ax.plot(laziness, entlist, marker = 'o', label="entropy", picker=True)
            if len(snrlist):
                sline = ax.plot(laziness, snrlist, marker = 'o', color='red', label='snr')
            
            plt.xlabel('Time')
            plt.legend(loc=4)
            if pi != None:
                plt.title('Entropy, SNR and Filesize Over Time for {date} using {pi}'.format(date=date, pi=pi))
            else:
                plt.title('Filesize, SNR and Entropy Over Time for local path {pat}'.format(pat = pat))
            fig.canvas.mpl_connect('pick_event', onpick3)
            plt.show()
            return
        #comparison of entropy and filesize
        if plotselect == "2":
            #much more drab graph, needs work
            ax.scatter(entlist, fsizelist, marker = 'o', picker = True)
            plt.xlabel('Entropy')
            plt.ylabel('Filesize')
            if pi != None:
                plt.title('Filesize and Entropy Comparison for {date} using {pi}'.format(date=date, pi=pi))
            else:
                plt.title('Filesize and Entropy Comparison for local path {pat}'.format(pat = pat))
            fig.canvas.mpl_connect('pick_event', onpick3)
            plt.show()
            return
    else:           #single file
        #only graph for calculating single files. Tracks the change in entropy throughout the length of the video. Useful for finding specific peaks in a video 	
        timelen = [x/30 for x in range(len(entlist))]
        print(len(timelen))
        print(len(entlist))
        print("filesize: ")
        print(fsizelist[0]) 
        ax.scatter(timelen, entlist, marker = 'o', color='black')
        if len(snrlist):
            ax.scatter(timelen, snrlist, marker='o', color='blue')
        plt.xlabel('Time(seconds)')
        plt.ylabel('Entropy values for each image')
        fe = filelist[0]
        print(os.getcwd())
        if pi != None: plt.title('Entropy values over time for {pi} , date: {date}, file: {file}'.format(date = date, file = fe, pi = pi ))
        else : plt.title('Entropy values over time for file {file}'.format(date = date,file = fe))
        plt.show()
        return

def main(FromWidget = 0):
    global widg
    print("Would you want to calculate files locally or remotely?")
    widg = FromWidget    
    fileget = input("Please choose 'local' or 'remote'.    ")
    if fileget in ('remote', 'Remote', 'REMOTE'):
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
                if len(ftp.listdir(p)) == 0:
                    print("Empty directory, please select a different date")
                    p= "/usr/local/bee/beemon/{pi}/".format(pi=pi)
                    continue
            except FileNotFoundError:
                print("The date is incorrect or not on this raspberry pi.")
                continue
            else:
                break
        return filemover(p, date)
    elif fileget in ('local', 'Local', 'LOCAL'):
        print('Please copy or type the filepath of the directory you would like to use.')
        while True:
            try:
                p = input(">  ")
                if p.startswith("/"):
                    pass
                else:
                    p = "/" + p
                if p.endswith("/"):
                    pass
                else:
                    p = p + "/"

                os.chdir(p)
               
                
            except FileNotFoundError:
                print("The filepath is incorrect or not on your filesystem.")
                continue
            else:
                break

        if p.startswith("/"):
            pass
        else:
            p = "/" + p
        if p.endswith("/"):
            pass
        else: 
            p = p + "/"
			
        os.chdir(p)
        print(os.getcwd())
        localmover(p)
if __name__ == "__main__":
    main()
    

