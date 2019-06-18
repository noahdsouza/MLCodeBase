'''
Last updated Tuesday June 11, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

class AsteroidProfile():
    # Let's try this shit again

    def __init__(self,num,imgpath,csvpath,cut):
        from makeThumbnail import FITSthumbnail
        from makeThumbnail import FITSprocess
        from astropy.io import fits
        # num is the 'NUMBER' (Running object number) parameter in SoEx ouput
        #   NOTE: this is the number label WITHIN the column, not the row index
        # imgpath is the parent image filepath
        # csvpath is the parent csv data filepath
        # cut is a tuple (pos,loc,show,size) for the FITSthumbnail function
        self.num = num # int (running object number within parent SoEx data)
        self.imgpath = imgpath # String (parent image filepath)
        self.imgdata = FITSprocess(self.imgpath) # numpy.ndarray (image data)
        self.originHeader = fits.open(self.imgpath)[0].header
            # astropy.io.fits.header.Header (parent FITS header)
        self.cutout = FITSthumbnail(   # astropy.nddata.utils.Cutout2D
                        self.imgdata,  # (thumbnail object data)
                        cut[0],
                        cut[3],
                        cut[1],
                        cut[2])
        self.thumbpath = cut[1] # String (thumbnail image filepath)
        self.thumbHeader = self.__thumbHeaderMake()
            # astropy.io.fits.header.Header (thumbnail FITS header)
        self.csvpath = csvpath # String (parent CSV table filepath)
        self.SoExData = self.__SoExDataMake() # dict (SoEx data of object only)

    def __str__(self):
        # this is what '>>> print(self)' returns
        return 'Object #%s from %s, \n %s' % (
                        self.num,
                        self.imgpath,
                        self.__printDict())

    def __repr__(self):
        # this is what '>>> self' returns
        return 'Object #%s from %s' % (self.num,self.imgpath)

    # def __getstate__(self):
    #     state = self.__dict__.copy()
    #     del state['imgdata'], state['cutout']
    #     return state
    #
    # def __setstate__(self,d):
    #     self.__dict__ = d
    #     from makeThumbnail import FITSthumbnail
    #     from makeThumbnail import FITSprocess
    #     self.imgdata = FITSprocess(self.imgpath)
    #     self.cutout = FITSthumbnail(
    #                     self.imgdata,
    #                     cut[0],
    #                     cut[3],
    #                     cut[1],
    #                     cut[2])

    def __thumbHeaderMake(self):
        # Creates an updated header for the thumbnail from the parent FITS image
        # NOTE: this header is separate from the PNG thumbnai
        from astropy.io import fits
        hdu = fits.open(self.imgpath)[0].copy()
        hdu.data = self.cutout.data
        return hdu.header

    def __SoExDataMake(self):
        # Slices out the object's corresponding row in the parent CSV and turns
        # it into a dictionary for easy access
        import csv
        from itertools import islice as islc
        reader = csv.reader(open(self.csvpath,'r'))
        rows = list(islc(reader,0,None))
        SoExDict = dict(zip(rows[0],rows[self.num]))
        return SoExDict

    def __printDict(self):
        # Literally just turns the SoExData dictionary into a readble string
        output = ''
        for i in self.SoExData:
            output = output + i + '\n'
        return output

    def displayProfile(self):
        # TODO: I'll get to it eventually. Unless Tinder for Asteroids does it.
        return

    def save(self,filename):
        # filename is string with the filename.
        # NOTE: savefile excludes 'imgdata' and 'cutout' to save space and so
        # that pickle doesn't get angry at you for saving unsupported filetypes
        # NOTE: save with a .dict extension. For organization.
        # if y'all are too lazy to do that, uncomment the next line.
        # filename = filename + '.dict'
        import pickle
        out = {
            'num': self.num,
            'imgpath': self.imgpath,
            'thumbpath': self.thumbpath,
            'originHeader': self.originHeader,
            'thumbHeader': self.thumbHeader,
            'csvpath': self.csvpath,
            'SoExData':self.SoExData
            }
        with open(filename, 'wb') as savefile:
            pickle.dump(out, savefile, pickle.HIGHEST_PROTOCOL)

    def HelloThere(self):
        # NOTE: very important method DO NOT REMOVE
        print('General Kenobi')
