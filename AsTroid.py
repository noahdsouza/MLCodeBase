'''
Last updated Monday June 17, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

import tkinter as tk
from PIL import ImageTk, Image
from AsteroidProfile import AsteroidProfile
from ImageProfile import ImageProfile
import os
import pickle
import sys

class AsTroid(tk.Tk):

    def __init__(self,num):
        tk.Tk.__init__(self)
        '''
        This class builds "Tinder for Asteroids" a.k.a. AsTroid
        This code file should be placed in an appropriately constructed
        filesystem such that it can naturally loop. The codebase should contain
        directories: FITS_IMAGES (with N number of files), FITS_TEXT (with N
        number of files), FITS_CSV (with zero files), YES, NO, and MAYBE.
        FITS_CSV will be populated with N number of
        files one at a time as FITS images are processed. Input the number of
        objects you wish to extract (maximum is defined by the CSV by SoEx) when
        prompted, and a window will pop up. Input the image filepath (which
        should start with 'FITS_IMAGES/') into the IMAGE FILEPATH field and
        either click the SUBMIT button or hit the Enter key. The window will
        then display a thumbnail of the object as well as its parent image (with
        a bounding box in the object's region). At this point you can click
        'nah' (left arrow key), 'maybe' (down arrow key), or 'yea' (right arrow
        key). This will kill the window, put the thumbnail, parent, and a
        dictionary with data in a folder within the YES, NO, or MAYBE folder in
        your codebase directory depending on which button you selected. The
        window will then reopen automatically. Hit Enter to resubmit the same
        parent image path, or enter a new one and hit Enter. Continue this
        process until the 'num' parameter you input is exhausted. Each folder
        in the YES, NO, and MAYBE folders will be named after the thumbnail, and
        contains the thumbnail (.png), parent image (F.png with bounding box),
        and data file (.dict) of the object's AsteroidProfile instance.
        '''

        self.imgpath = None
        self.txtpath = None
        self.ImgProf = None
        self.num = num
        self.coords = None
        self.pos = None

        # INPUT FILEPATHS
        tk.Label(self, text='IMAGE FILEPATH', anchor='e', width=80).grid(row=0)
        # tk.Label(self, text='TEXT FILEPATH', anchor='e', width=80).grid(row=1)
        self.imgpathIN = tk.Entry(self)
        # self.txtpathIN = tk.Entry(self)
        self.submit = tk.Button(self, text='SUBMIT', command=self.__getPaths)
        self.bind('<Return>',self.__getPaths)
            # to avoid clicks, hit tab until the button is highlighted and then
            # hit the space bar. That clicks it instead of Enter (idk why)
        self.imgpathIN.grid(row=0, column=1)
        # self.txtpathIN.grid(row=1, column=1)
        self.submit.grid(row=2, column=1)

        # Make image canvases in advance for scaling
        self.canvasL = tk.Canvas(self, width=600, height=500)
        self.canvasL.grid(row=3, column=0)
        self.canvasR = tk.Canvas(self, width=600, height=500)
        self.canvasR.grid(row=3, column=2)

        # 'SWIPE' BUTTONS
        self.nah = tk.Button(self, text='\u25c0 \u25c0 nah',
                        bg='#ff5454', height=5, width=8,
                        command=self.__swipeNahh)
        self.bind('<Left>',self.__swipeNahh)
        self.may = tk.Button(self, text='\u25c0 maybe \u25b6',
                        bg='#567bff', height=5, width=8,
                        command=self.__swipeMayb)
        self.bind('<Down>',self.__swipeMayb)
        self.yea = tk.Button(self, text='yea \u25b6 \u25b6',
                        bg='#81ff54', height=5, width=8,
                        command=self.__swipeYeah)
        self.bind('<Right>',self.__swipeYeah)
        self.nah.grid(row=5, column=0)
        self.may.grid(row=5, column=1)
        self.yea.grid(row=5, column=2)

        # EXIT button
        self.esc = tk.Button(self, text='EXIT',command=self.__exit)
        self.bind('<Escape>',self.__exit)
        self.esc.grid(row=0, column=2)

    def __getPaths(self,event=None):
        # Get image and text filepaths from input (see __init__) and save it
        # If this isn't your first rodeo (iteration or Asteroid), then it'll
        # take the saved path and reinput it with a <Return> keypress
        # Also define an ImageProfile object
        if not os.path.isfile('txtpath.txt'):
            self.imgpath = self.imgpathIN.get()
            pickle.dump(self.imgpath, open('txtpath.txt','wb'))
        else:
            self.imgpath = pickle.load(open('txtpath.txt','rb'))
        # self.txtpath = self.txtpathIN.get()
        self.txtpath = 'FITS_TEXT/'+self.imgpath[12:-5]+'.txt'
        self.thumbfolder = self.imgpath[12:-5]+'_'+'{:05d}'.format(self.num)
        # print(self.imgpath,self.txtpath)
        self.ImgProf = ImageProfile(self.imgpath,self.txtpath)
        self.__makeImgProf()

    def __makeImgProf(self):
        if self.imgpath != None and self.txtpath != None:
            self.ImgProf = ImageProfile(self.imgpath,self.txtpath)
            # FIXME this is redundant, but it still works, so fix later
            self.coords = self.ImgProf.getCoords(
                '#_5_XWIN_IMAGE_Windowed_position_estimate_along_x_[pixel]',
                '#_6_YWIN_IMAGE_Windowed_position_estimate_along_y_[pixel]')
            self.pos = (float(self.coords[self.num-1][0]),
                        float(self.coords[self.num-1][1]))
            cut = (self.pos,self.thumbfolder+'.png',False,40)
                # cutout = fitsname_num.png
                # boundingbox = fitsname_numF.png
            self.AstProf = AsteroidProfile(self.num,self.imgpath,
                            self.ImgProf.csvpath,cut)
            # os.mkdir(imgfolder)
            self.__putImages()
        else:
            # not sure if this is necessary anymore????
            if self.imgpath == None:
                print('ENTER IMAGE FILEPATH')
            if self.txtpath == None:
                print('ENTER TEXT FILEPATH')
        # print(self.AstProf.)

    def __putImages(self):
        # place images into the window
        # BOUNDING BOX IMAGE
        self.imgL = ImageTk.PhotoImage(Image.open(self.thumbfolder+'F.png'))
        self.canvasL.create_image(20, 20, anchor='nw', image=self.imgL)
        self.canvasL.image = self.imgL
        tk.Label(self, text=self.thumbfolder+'F.png', anchor='e',
                        width=80).grid(row=4,column=0)
        # THUMBNAIL
        self.imgR = ImageTk.PhotoImage(Image.open(self.thumbfolder+'.png'))
        self.canvasR.create_image(20, 20, anchor='nw', image=self.imgR)
        self.canvasR.image = self.imgR
        tk.Label(self, text=self.thumbfolder+'.png', anchor='e',
                        width=80).grid(row=4,column=2)

    def __swipeYeah(self,event=None):
        # add AsteroidProfile to 'YES' pile
        # kill window
        os.mkdir('YES/'+self.thumbfolder)
        os.rename(self.thumbfolder+'.png',
            'YES/'+self.thumbfolder+'/'+self.thumbfolder+'.png')
        os.rename(self.thumbfolder+'F.png',
            'YES/'+self.thumbfolder+'/'+self.thumbfolder+'F.png')
        self.AstProf.save(
            'YES/'+self.thumbfolder+'/'+self.thumbfolder+'.dict')
        # print(str(self.num) + ' ' + self.thumbfolder + '\n')
        self.destroy()

    def __swipeNahh(self,event=None):
        # add AsteroidProfile to 'NO' pile
        # kill window
        os.mkdir('NO/'+self.thumbfolder)
        os.rename(self.thumbfolder+'.png',
            'NO/'+self.thumbfolder+'/'+self.thumbfolder+'.png')
        os.rename(self.thumbfolder+'F.png',
            'NO/'+self.thumbfolder+'/'+self.thumbfolder+'F.png')
        self.AstProf.save(
            'NO/'+self.thumbfolder+'/'+self.thumbfolder+'.dict')
        # print(str(self.num) + ' ' + self.thumbfolder + '\n')
        self.destroy()

    def __swipeMayb(self,event=None):
        # add AsteroidProfile to 'MAYBE' pile
        # kill window
        os.mkdir('MAYBE/'+self.thumbfolder)
        os.rename(self.thumbfolder+'.png',
            'MAYBE/'+self.thumbfolder+'/'+self.thumbfolder+'.png')
        os.rename(self.thumbfolder+'F.png',
            'MAYBE/'+self.thumbfolder+'/'+self.thumbfolder+'F.png')
        self.AstProf.save(
            'MAYBE/'+self.thumbfolder+'/'+self.thumbfolder+'.dict')
        # print(str(self.num) + ' ' + self.thumbfolder + '\n')
        self.destroy()

    def __exit(self, event=None):
        sys.exit()

if __name__ == "__main__":
    # Do this stuff if the file is called as the main piece of code
    # This will be ignored if the file is imported for other purposes
    r = input('ENTER NUMBER OF OBJECTS: ')
    for i in range(int(r)):
        app = AsTroid(i)
        app.mainloop()





# FITS_IMAGES/20020109022041d.fits







# big oof
