'''
Last updated Friday August 2, 2019
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
        tk.Tk.__init__(self)
        # this calls Tk's __init__ not Astaroth's since Astaroth is a child
        # class of Tk, just so you know (and I remember)
        self.winfo_toplevel().title("A S T A R O T H")
        self.configure(bg='black')
        """
        (AST)eroid cl(A)ssification and p(RO)cessing in py(TH)on
        Yes I'm aware that "Astaroth" is a demon's name. It just sounds cool.
        This class builds "Tinder for Asteroids" a.k.a. Astaroth.
        This code file should be placed in an appropriately constructed
        filesystem such that it can naturally loop. The codebase should contain
        directories: FITS_IMAGES (with N number of files), FITS_TEXT (with N
        number of files), FITS_CSV (with zero files), YES, NO, and MAYBE.
        FITS_CSV will be populated with files one at a time as each of your FITS
        images are processed. Input the number of objects you wish to extract
        (maximum is defined by the CSV by SoEx) when prompted, and a window will
        pop up. Input the image filepath (which should start with
        'FITS_IMAGES/') into the IMAGE FILEPATH field and either click the
        SUBMIT button or hit the Enter key. Alternatively, you can click the
        'IMAGE PATH' button and choose a file from a file explorer. The window
        will then display a thumbnail of the object as well as its parent image
        (with a bounding box in the object's region). At this point you can
        click 'nah' (left arrow key), 'maybe' (down arrow key), or 'yea' (right
        arrow key). This will kill the window, put the thumbnail, parent, and
        an encoded (pickled) dictionary with data in a folder within the YES,
        NO, or MAYBE folder in your codebase directory depending on which button
        you selected. The window will then reopen automatically (it might take a
        second, be patient). Hit Enter to resubmit the same parent image path,
        or enter a new one and hit Enter. If you are using Fast Mode, there is
        no need to resubmit, but you will also not be able to enter a new image
        path. Continue this process until the 'num' parameter you input is
        exhausted. Each folder in the YES, NO, and MAYBE folders will be named
        after the thumbnail, and contains the thumbnail (.png), parent image
        (F.png with bounding box), and encoded data file (.dict) of the object's
        AsteroidProfile instance. Most of the (private) functions run
        (relatively) sequentially, so I hope this isn't too hard to follow
        :)
        *** NEW: Back Button (up arrow key) decrements 'num' and sends you back
            by one thumbnail. It's surprisingly functional now.
        *** NEW: Keybindings (arrows) are now only active after a filepath has
            been submitted, so there should be less accidents (like me lol) now
        """

        self.imgpath = None
        self.txtpath = None
        self.ImgProf = None
        self.pos = None
        self.coords = None
        self.num = num
        self.__cwidth = 680
        self.__cheight = 480
        w, h = 1550, 650
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = ((ws/2)-(w/2)), ((hs/2)-(h/2))
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ''' INPUT FILEPATHS '''
        # use file explorer
        self.submitGUI = tk.Button(self, text='IMAGE FILEPATH',
                        command=self.__fileInterface,
                        highlightthickness=0, bg='gray20', fg='gray',
                        font=('Arial',14))
        self.submitGUI.grid(row=0,sticky='e')
        # type out fileath
        self.imgpathIN = tk.Entry(self, bg='gray3', fg='gray',
                        font=('Arial',14))
        self.submit = tk.Button(self, text='SUBMIT', command=self.__getPaths,
                        highlightthickness=0, bg='gray20', fg='gray',
                        font=('Arial',20))
        self.bind('<Return>',self.__getPaths)
            # to avoid clicks, hit tab until the button is highlighted
        self.imgpathIN.grid(row=0, column=1, padx=5)
        self.submit.grid(row=1, column=1)
        ''' HELP BUTTON '''
        self.__helpButton = tk.Button(self,text='HELP',command=self.__help,
                        highlightthickness=0, bg='gray20', fg='gray',
                        font=('Arial',14))
        self.__helpButton.grid(row=0,column=2,sticky='w')

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
        # self.bind('<Left>',self.__swipeNahh)
        self.may = tk.Button(self, text='\u25c0 maybe \u25b6',
                        bg='#567bff', width=8, font=('Arial',20),
                        command=self.__swipeMayb, highlightthickness=0)
        # self.bind('<Down>',self.__swipeMayb)
        self.yea = tk.Button(self, text='yea \u25b6 \u25b6',
                        bg='#81ff54', width=8, font=('Arial',20),
                        command=self.__swipeYeah, highlightthickness=0)
        # self.bind('<Right>',self.__swipeYeah)
        self.nah.grid(row=4, column=0, padx=(5,5), pady=(5,5))
        self.may.grid(row=4, column=1, padx=(5,5), pady=(5,5))
        self.yea.grid(row=4, column=2, padx=(5,5), pady=(5,5))

        ''' EXIT button '''
        self.esc = tk.Button(self, text='EXIT',command=self.__exit,bg='gray20',
                        fg='gray', highlightthickness=0, font=('Arial',20))
        self.bind('<Escape>',self.__exit)
        self.esc.grid(row=1, column=2)

        ''' BACK button '''
        self.esc = tk.Button(self, text='BACK',command=self.__backb,bg='gray20',
                        fg='gray', highlightthickness=0, font=('Arial',20))
        # self.bind('<Up>',self.__backb)
        self.esc.grid(row=1, column=0)

    def __getPaths(self,event=None):
        # Get image and text filepaths from input (see __init__) and save it
        # If this isn't your first rodeo (iteration or asteroid), then it'll
        # take the saved path and reinput it with a 'SUBMIT' button invocation
        # Also call Astaroth.__makeImgProf()
        self.unbind('<Left>')
        self.unbind('<Down>')
        self.unbind('<Right>')
        self.unbind('<Up>')
        if not os.path.isfile('txtpath.txt'):
            self.imgpath = self.imgpathIN.get()
            pickle.dump(self.imgpath, open('txtpath.txt','wb'))
        else:
            self.imgpath = pickle.load(open('txtpath.txt','rb'))
        # self.txtpath = self.txtpathIN.get()
        self.bind('<Left>',self.__swipeNahh)
        self.bind('<Down>',self.__swipeMayb)
        self.bind('<Right>',self.__swipeYeah)
        self.bind('<Up>',self.__backb)
        # print('ARROW KEYS BOUND TO SWIPE INPUT')
        self.txtpath = 'FITS_TEXT/'+self.imgpath[12:-5]+'.txt'
        self.thumbfolder = self.imgpath[12:-5]+'_'+'{:05d}'.format(self.num+1)
            # thumbfolder --> remove imgpath FITS extension, add trailing number
            # ex: imgpath = oof.fits, num = 5 --> thumbfolder = oof_00005
            # NOTE: thumbfolder does NOT have an extension -- those are added
            # when saving files -- thumbfolder names a folder that holds files
        self.__makeImgProf()

    def __fileInterface(self):
        from tkinter.filedialog import askopenfilename
        '''
        This essentially does the same thing as __getPaths(), but instead it
        opens a file explorer so a user can browse FITS_IMAGES
        To use it, just click on the "IMAGE FILEPATH" button
        '''
        self.unbind('<Left>')
        self.unbind('<Down>')
        self.unbind('<Right>')
        self.unbind('<Up>')
        if not os.path.isfile('txtpath.txt'):
            ip = askopenfilename(initialdir='FITS_IMAGES',
                title='Select FITS File',
                filetypes=(('FITS files','*.fits'),('FITS files','*.fit')))
            try:
                if ip[ip.find('FITS_IMAGES'):] != '':
                    self.imgpath = ip[ip.find('FITS_IMAGES'):]
                    pickle.dump(self.imgpath, open('txtpath.txt','wb'))
                    self.bind('<Left>',self.__swipeNahh)
                    self.bind('<Down>',self.__swipeMayb)
                    self.bind('<Right>',self.__swipeYeah)
                    self.bind('<Up>',self.__backb)
                    self.txtpath = 'FITS_TEXT/'+self.imgpath[12:-5]+'.txt'
                    self.thumbfolder = self.imgpath[12:-5]+'_'+'{:05d}'.format(
                        self.num+1)
                    self.__makeImgProf()
                else:
                    print('ENTER OR CHOOSE A FILEPATH')
            except AttributeError:
                print('ENTER OR CHOOSE A FILEPATH')
        else:
            self.imgpath = pickle.load(open('txtpath.txt','rb'))

    def __makeImgProf(self):
        # Make an ImageProfile object and scrape it for relevant data
        # Make an AsteroidProfile object from one (1) object's worth of said
        # relevant data and then move onto calling Astaroth.__putImages()
        self.ImgProf = ImageProfile(self.imgpath,self.txtpath)
            # build parent ImageProfile
            # TODO: maybe pickle this too for all objects? Space&Speed saving
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
        # Place images into the blank canvases defined in the __init__ and label
        # them with their filenames
        # PLACE BOUNDING BOX IMAGE
        self.imgL = ImageTk.PhotoImage(Image.open(self.thumbfolder+'F.png'))
        self.canvasL.create_image(self.__cwidth/2, self.__cheight/2,
                        anchor='center', image=self.imgL)
        self.canvasL.image = self.imgL
        tk.Label(self, text=self.thumbfolder+'F.png', anchor='center',
                        bg='black', fg='gray', width=35,
                        font=('Arial',14)).grid(row=3,column=0)
        # PLACE THUMBNAIL
        self.imgR = ImageTk.PhotoImage(Image.open(self.thumbfolder+'.png'))
        self.canvasR.create_image(self.__cwidth/2, self.__cheight/2,
                        anchor='center', image=self.imgR)
        self.canvasR.image = self.imgR
        tk.Label(self, text=self.thumbfolder+'.png', anchor='center',
                        bg='black', fg='gray', width=35,
                        font=('Arial',14)).grid(row=3,column=2)

    # I got around tkinter's aversion to binding multiple buttons to the same
    # function (with different parameters) by making a helper function for the
    # three swipe buttons that does all the heavy lifting
    def __swiper(self,dec,event=None):
        if not os.path.exists(dec):
            os.mkdir(dec)
        try:
            if os.path.exists('YES/'+self.thumbfolder):
                shutil.rmtree('YES/'+self.thumbfolder)
            if os.path.exists('NO/'+self.thumbfolder):
                shutil.rmtree('NO/'+self.thumbfolder)
            if os.path.exists('MAYBE/'+self.thumbfolder):
                shutil.rmtree('MAYBE/'+self.thumbfolder)
            os.mkdir(dec+'/'+self.thumbfolder)
        except AttributeError:
            print('SUBMIT OR RESUBMIT FILEPATH (ENTER) BEFORE SWIPING')
        else:
            os.rename(self.thumbfolder+'.png',
                dec+'/'+self.thumbfolder+'/'+self.thumbfolder+'.png')
            os.rename(self.thumbfolder+'F.png',
                dec+'/'+self.thumbfolder+'/'+self.thumbfolder+'F.png')
            self.AstProf.save(
                dec+'/'+self.thumbfolder+'/'+self.thumbfolder+'.dict')
            self.destroy()

    def __swipeYeah(self,event=None):
        # "swipes" right
        self.__swiper('YES')
    def __swipeNahh(self,event=None):
        # "swipes" left
        self.__swiper('NO')
    def __swipeMayb(self,event=None):
        # "swipes" down (take notes, Tinder)
        self.__swiper('MAYBE')

    def __backb(self, event=None):
        # Takes you back by one step in the loop with each keypress.
        # Re-categorizing an object you backtracked into will take you back to
        # the object you started going back from
        if self.num == 0:
            print('NOTHING TO GO BACK TO BRUH')
        else:
            self.num = self.num - 1
            self.destroy()
            self = Astaroth(self.num)
            self.submit.invoke()

    def __help(self):
        # just a popup window with instructions/controls
        from tkinter.messagebox import showinfo
        helpstring = '''
WELCOME TO ASTAROTH

Hit "IMAGE FILEPATH" to choose a file

Or type out its relative path and hit ENTER (or click SUBMIT)

LEFT ARROW KEY: sorts object into the "NO" pile

RIGHT ARROW KEY: sorts object into the "YES" pile

DOWN ARROW KEY: sorts object into the "MAYBE" pile

LEFT ARROW KEY: back button (decrements by one)

ESC KEY: exits Astaroth and garbage-collects
        '''
        showinfo('Help',helpstring)

    def __exit(self, event=None):
        # Delete everything that we don't want just lying around
        # Removes leftover PNGs and txtpath.txt files
        # Kill literally everything until it's very, very dead.
        items = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in items:
            if f.endswith('.png'):
                os.remove(f)
        if os.path.isfile('txtpath.txt'): os.remove('txtpath.txt')
        sys.exit()

# ------------------------------ STATIC METHODS ------------------------------ #

    # These are static utility functions for running Astaroth
    @staticmethod
    def nOBJslow(r):
        # Regular mode, requires a manual invocation of the SUBMIT button
        print('PRESS ENTER TO SUBMIT IMAGE FILEPATH')
        i = 0
        temp = 0
        while i<int(r):
            app = Astaroth(i)
            temp = app.num
            print('BEFORE: ',temp)
            app.mainloop()
            temp = app.num
            print('AFTER:  ',temp)
            temp = app.num
            i = app.num+1

    @staticmethod
    def nOBJfast(r):
        # Fast mode, SUBMIT is invoked automatically after a swipe
        print('FAST MODE ENABLED -- BACK BUTTON DISABLED')
        # disable the back button
        i = 0
        temp = 0
        while i<int(r):
            print('BEFORE: ',temp)
            app = Astaroth(i)
            temp = app.num
            print('DURING: ',temp)
            if i!=0:
                app.submit.invoke()
            app.mainloop()
            i = app.num+1

    @staticmethod
    def modes(argument, r):
        # picks a mode based on user input with switchcases
        switcher = {
            0: Astaroth.nOBJfast,
            1: Astaroth.nOBJslow
        }
        func = switcher.get(argument, 'sad')
        return func(r)

    @staticmethod
    def prompts():
        # Gets user input for loop length and mode
        r = input('ENTER NUMBER OF OBJECTS: ')
        yn = None
        if int(r) != 1:
            yn = input('WOULD YOU LIKE TO USE FAST MODE? (Y/N): ')
        return r, yn

    @staticmethod
    def runAstaroth():
        # Neatly packages up everything with a bow for deployment
        r, yn = Astaroth.prompts()
        Astaroth.modes((0 if ((yn=='Y' or yn=='y') and r!=1) else 1), r)
        if os.path.isfile('txtpath.txt'):
            os.remove('txtpath.txt')

''' M A I N L O O P   T I M E '''
if __name__ == "__main__":
    # I strongly suggest running Astaroth as the main file, and not importing it
    # Like, you COULD import it, but that would just make everything marginally
    # more difficult and I don't know why you'd want that
    Astaroth.runAstaroth()
