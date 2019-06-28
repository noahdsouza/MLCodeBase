'''
Last updated Friday June 28, 2019
Author: Noah D'Souza
Designed and tested in Python 3.6.3
'''

import tkinter as tk
from PIL import ImageTk, Image
from AsteroidProfile import AsteroidProfile
from ImageProfile import ImageProfile
import os
import pickle
import sys
import shutil

class Astaroth(tk.Tk):

    def __init__(self, num):
    # def __init__(self, num, fastmode=False):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("A S T A R O T H")
        self.configure(bg='black')
        # self.fastmode = fastmode
        '''
        Yes I'm aware that "Astaroth" is a demon's name. It sounds cool.
        This class builds "Tinder for Asteroids" a.k.a. Astaroth.
        This code file should be placed in an appropriately constructed
        filesystem such that it can naturally loop. The codebase should contain
        directories: FITS_IMAGES (with N number of files), FITS_TEXT (with N
        number of files), FITS_CSV (with zero files), YES, NO, and MAYBE.
        FITS_CSV will be populated with N number of files one at a time as FITS
        images are processed. Input the number of objects you wish to extract
        (maximum is defined by the CSV by SoEx) when prompted, and a window will
        pop up. Input the image filepath (which should start with
        'FITS_IMAGES/') into the IMAGE FILEPATH field and either click the
        SUBMIT button or hit the Enter key. The window will then display a
        thumbnail of the object as well as its parent image (with a bounding box
        in the object's region). At this point you can click 'nah' (left arrow
        key), 'maybe' (down arrow key), or 'yea' (right arrow key). This will
        kill the window, put the thumbnail, parent, and a dictionary with data
        in a folder within the YES, NO, or MAYBE folder in your codebase
        directory depending on which button you selected. The window will then
        reopen automatically. Hit Enter to resubmit the same parent image path,
        or enter a new one and hit Enter. Continue this process until the 'num'
        parameter you input is exhausted. Each folder in the YES, NO, and MAYBE
        folders will be named after the thumbnail, and contains the thumbnail
        (.png), parent image (F.png with bounding box), and data file (.dict) of
        the object's AsteroidProfile instance. Most of the (private) functions
        run (relatively) sequentially, so I hope this isn't too hard to follow
        :)
        *** NEW (optional) Fast Mode removes the need to hit Enter to resubmit,
            and does it automatically. This does mean, however, that you can't
            submit a different image easily in the middle, and the new back
            button (see below) also probably won't work too well
        *** NEW Back Button (up arrow key) decrements 'num' and sends you back
            by one thumbnail. Keep in mind, this one is new and developed
            hastily. It may not work super well at the moment.
        *** NEW static functions at the bottom of the class, specifically
            Astaroth.runAstaroth(), help make running the program a bit easier
        '''

        self.imgpath = None
        self.txtpath = None
        self.ImgProf = None
        self.num = num
        self.coords = None
        self.pos = None
        self.__cwidth = 680
        self.__cheight = 480
        w, h = 1550, 650
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = ((ws/2)-(w/2)), ((hs/2)-(h/2))
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        ''' INPUT FILEPATHS '''
        tk.Label(self, text='IMAGE FILEPATH', anchor='e', width=20, bg='black',
                        fg='gray', font=('Arial',14)).grid(row=0, sticky='e')
        self.imgpathIN = tk.Entry(self, bg='gray3', fg='gray',
                        font=('Arial',14))
        self.submit = tk.Button(self, text='SUBMIT', command=self.__getPaths,
                        highlightthickness=0, bg='gray20', fg='gray',
                        font=('Arial',20))
        self.bind('<Return>',self.__getPaths)
            # to avoid clicks, hit tab until the button is highlighted
        self.imgpathIN.grid(row=0, column=1, padx=5)
        self.submit.grid(row=1, column=1)

        ''' Make image canvases in advance for scaling '''
        self.canvasL = tk.Canvas(self, width=self.__cwidth,
                        height=self.__cheight, bg='black', bd=0,
                        highlightthickness=0)
        self.canvasL.grid(row=2, column=0)
        self.canvasR = tk.Canvas(self, width=self.__cwidth,
                        height=self.__cheight, bg='black', bd=0,
                        highlightthickness=0)
        self.canvasR.grid(row=2, column=2)

        ''' 'SWIPE' BUTTONS '''
        self.nah = tk.Button(self, text='\u25c0 \u25c0 nah',
                        bg='#ff5454', width=8, font=('Arial',20),
                        command=self.__swipeNahh, highlightthickness=0)
        self.bind('<Left>',self.__swipeNahh)
        self.may = tk.Button(self, text='\u25c0 maybe \u25b6',
                        bg='#567bff', width=8, font=('Arial',20),
                        command=self.__swipeMayb, highlightthickness=0)
        self.bind('<Down>',self.__swipeMayb)
        self.yea = tk.Button(self, text='yea \u25b6 \u25b6',
                        bg='#81ff54', width=8, font=('Arial',20),
                        command=self.__swipeYeah, highlightthickness=0)
        self.bind('<Right>',self.__swipeYeah)
        self.nah.grid(row=4, column=0, padx=(5,5), pady=(5,5))
        self.may.grid(row=4, column=1, padx=(5,5), pady=(5,5))
        self.yea.grid(row=4, column=2, padx=(5,5), pady=(5,5))

        ''' EXIT button '''
        self.esc = tk.Button(self, text='EXIT',command=self.__exit, bg='gray20',
                        fg='gray', highlightthickness=0, font=('Arial',20))
        self.bind('<Escape>',self.__exit)
        self.esc.grid(row=1, column=2)

        ''' BACK button '''
        self.esc = tk.Button(self, text='BACK',command=self.backb, bg='gray20',
                        fg='gray', highlightthickness=0, font=('Arial',20))
        self.bind('<Up>',self.backb)
        self.esc.grid(row=1, column=0)

    def __getPaths(self,event=None):
        # Get image and text filepaths from input (see __init__) and save it
        # If this isn't your first rodeo (iteration or Asteroid), then it'll
        # take the saved path and reinput it with a 'SUBMIT' button  invocation
        # Also define an ImageProfile object
        if not os.path.isfile('txtpath.txt'):
            self.imgpath = self.imgpathIN.get()
            pickle.dump(self.imgpath, open('txtpath.txt','wb'))
        else:
            self.imgpath = pickle.load(open('txtpath.txt','rb'))
        # self.txtpath = self.txtpathIN.get()
        self.txtpath = 'FITS_TEXT/'+self.imgpath[12:-5]+'.txt'
        self.thumbfolder = self.imgpath[12:-5]+'_'+'{:05d}'.format(self.num+1)
            # thumbfolder --> remove imgpath FITS extension, add trailing number
            # ex: imgpath = oof.fits, num = 5 --> thumbfolder = oof_00005
            # NOTE: thumbfolder does NOT have an extension -- those are added
            # when saving files -- thumbfolder names a folder that holds files
        self.__makeImgProf()

    def __makeImgProf(self):
        self.ImgProf = ImageProfile(self.imgpath,self.txtpath)
            # build parent ImageProfile
            # FIXME: maybe pickle this too for all objects? Space&Speed saving
        self.coords = self.ImgProf.getCoords(
            '#_5_XWIN_IMAGE_Windowed_position_estimate_along_x_[pixel]',
            '#_6_YWIN_IMAGE_Windowed_position_estimate_along_y_[pixel]',
            '#_1_NUMBER_Running_object_number_',
            '#_2_FLAGS_Extraction_flags_')
        self.pos = (float(self.coords[self.num-1][0]),
                    float(self.coords[self.num-1][1]))
        cut = (self.pos,self.thumbfolder+'.png',False,40)
            # cutout image --> fitsname_num.png
            # boundingbox image --> fitsname_numF.png
        self.AstProf = AsteroidProfile(self.num,self.imgpath,
                        self.ImgProf.csvpath,cut)
        self.__putImages()

    def __putImages(self):
        # place images into the window
        # BOUNDING BOX IMAGE
        self.imgL = ImageTk.PhotoImage(Image.open(self.thumbfolder+'F.png'))
        self.canvasL.create_image(self.__cwidth/2, self.__cheight/2,
                        anchor='center', image=self.imgL)
        self.canvasL.image = self.imgL
        tk.Label(self, text=self.thumbfolder+'F.png', anchor='center',
                        bg='black', fg='gray', width=35,
                        font=('Arial',14)).grid(row=3,column=0)
        # THUMBNAIL
        self.imgR = ImageTk.PhotoImage(Image.open(self.thumbfolder+'.png'))
        self.canvasR.create_image(self.__cwidth/2, self.__cheight/2,
                        anchor='center', image=self.imgR)
        self.canvasR.image = self.imgR
        tk.Label(self, text=self.thumbfolder+'.png', anchor='center',
                        bg='black', fg='gray', width=35,
                        font=('Arial',14)).grid(row=3,column=2)

    def __swipeYeah(self,event=None):
        # add AsteroidProfile to 'YES' pile
        # kill window
        if not os.path.exists('YES'):
            os.mkdir('YES')
        try:
            if os.path.exists('YES/'+self.thumbfolder):
                shutil.rmtree('YES/'+self.thumbfolder)
            os.mkdir('YES/'+self.thumbfolder)
        except AttributeError:
            print('SUBMIT OR RESUBMIT FILEPATH (ENTER) BEFORE SWIPING')
        else:
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
        if not os.path.exists('NO'):
            os.mkdir('NO')
        try:
            if os.path.exists('NO/'+self.thumbfolder):
                shutil.rmtree('NO/'+self.thumbfolder)
            os.mkdir('NO/'+self.thumbfolder)
        except AttributeError:
            print('SUBMIT OR RESUBMIT FILEPATH (ENTER) BEFORE SWIPING')
        else:
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
        if not os.path.exists('MAYBE'):
            os.mkdir('MAYBE')
        try:
            if os.path.exists('MAYBE/'+self.thumbfolder):
                shutil.rmtree('MAYBE/'+self.thumbfolder)
            os.mkdir('MAYBE/'+self.thumbfolder)
        except AttributeError:
            print('SUBMIT OR RESUBMIT FILEPATH (ENTER) BEFORE SWIPING')
        else:
            os.rename(self.thumbfolder+'.png',
                'MAYBE/'+self.thumbfolder+'/'+self.thumbfolder+'.png')
            os.rename(self.thumbfolder+'F.png',
                'MAYBE/'+self.thumbfolder+'/'+self.thumbfolder+'F.png')
            self.AstProf.save(
                'MAYBE/'+self.thumbfolder+'/'+self.thumbfolder+'.dict')
            # print(str(self.num) + ' ' + self.thumbfolder + '\n')
            self.destroy()

    def __exit(self, event=None):
        if hasattr(self, 'thumbfolder'):
            if (os.path.isfile(self.thumbfolder+'.png') and
                os.path.isfile(self.thumbfolder+'F.png')):
                os.remove(self.thumbfolder+'.png')
                os.remove(self.thumbfolder+'F.png')
                os.remove('txtpath.txt')
        sys.exit()

    def backb(self, event=None):
        if self.num == 1:
            print('NOTHING TO GO BACK TO BRUH')
        else:
            self.num = self.num - 1
            self.destroy()
            self = Astaroth(self.num)
            self.submit.invoke()

    # These are static utility functions for running Astaroth
    @staticmethod
    def nOBJslow(r):
        print('PRESS ENTER TO SUBMIT IMAGE FILEPATH')
        i = 0
        while i<int(r):
            app = Astaroth(i)
            # app = Astaroth(i, fastmode=False)
            app.mainloop()
            i+=1

    @staticmethod
    def nOBJfast(r):
        print('FAST MODE ENABLED -- BACK BUTTON DISABLED')
        # disable the back button
        i = 0
        while i<int(r):
            app = Astaroth(i)
            # app = Astaroth(i, fastmode=True)
            if i!=0:
                app.submit.invoke()
            app.mainloop()
            i+=1

    @staticmethod
    def modes(argument, r):
        switcher = {
            0: Astaroth.nOBJfast,
            1: Astaroth.nOBJslow
        }
        func = switcher.get(argument, 'sad')
        return func(r)
    @staticmethod
    def prompts():
        r = input('ENTER NUMBER OF OBJECTS: ')
        yn = None
        if int(r) != 1:
            yn = input('WOULD YOU LIKE TO USE FAST MODE? (Y/N): ')
        return r, yn

    @staticmethod
    def runAstaroth():
        r, yn = Astaroth.prompts()
        Astaroth.modes((0 if ((yn=='Y' or yn=='y') and r!=1) else 1), r)
        os.remove('txtpath.txt')

''' M A I N L O O P   T I M E '''
if __name__ == "__main__":
    # Do this stuff if the file is called as the main piece of code
    # This will be ignored if the file is imported for other purposes
    Astaroth.runAstaroth()


# FITS_IMAGES/g19960516960516061758d.fits
    # new dark FITS image
# FITS_IMAGES/20020109022041d.fits
    # old, trashy FITS image
# FITS_IMAGES/g19960516960516063059a.fits
    # new check FITS image

# astor==0.6.2
# astropy==3.0.5
# astropy-healpix==0.3.1
# astroscrappy==1.0.5
# Cython==0.28.3
# feedparser==5.1.3
# fitsio==0.9.11
# future==0.16.0
# ipykernel==4.8.0
# ipython==6.2.1
# numpy==1.14.0
# opencv-python==3.4.0.12
# pep8==1.7.0
# pickle==4.0
# PIL==1.1.7
# pycosat==0.6.3
# pycups==1.9.73
# pycurl==7.43.0
# pydot==1.2.4
# pygcode==0.2.1
# pyparsing==2.2.0
# python-apt==1.1.0b1
# python-dateutil==2.6.1
# python-debian==0.1.27
# python-systemd==231
# ubuntu-drivers-common==0.0.0


# big oof
