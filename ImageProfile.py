'''
Last updated Thursday June 13, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

class ImageProfile:
    # Class to store a lorg FITS image and its dummy thicc SoEx output

    # from TXTtoCSV import TXTtoCSV
    # from makeThumbnail import FITSprocess

    def __init__(self,imgpath,txtpath=None):
        from makeThumbnail import FITSprocess
        from TXTtoCSV import TXTtoCSV
        from astropy.io import fits
        # from astropy.wcs import WCS
        # imgpath is the filepath of the FITS image
        # txtpath is the filepath of the original .txt SoEx data
        # imgdata is an astropy data frame of the FITS image
        # csvpath is the filepath of the SoEx data in a new CSV table
        self.imgpath = imgpath
        if txtpath == None:
            self.txtpath = imgpath[:-4]+'txt'
            # if no text filepath is given, then it has the same name as the
            # FITS image but with a different extension
        else:
            self.txtpath = txtpath
            # text filepath given, define as an attribute here
        self.imgdata = FITSprocess(self.imgpath)
            # prepare data for AsteroidProfile class objects later
        self.hdu = fits.open(self.imgpath)[0]
            # make header data units
        self.header = self.hdu.header
            # get header from header data units
        self.csvpath = (self.txtpath[:-3]+'csv').replace('TEXT','CSV',1)
            # FIXME remember this is HARD-CODED into the FITS_CSV folder.
            # That's like, BAD.
        TXTtoCSV(self.txtpath, self.csvpath)
            # makes a CSV with the same name as the text file

    def __str__(self):
        return 'Image "%s" with data "%r"' % (self.imgpath, self.csvpath)

    def __repr__(self):
        return 'ImageProfile("%s","%r")' % (self.imgpath, self.txtpath)

    def getCoords(self,xparam,yparam):
        # REVIEW:
        # Turns the two given columns into a zero-indexed list of tuples.
        # If you have a columns X and Y with elements |X1;X2;X3| and |Y1;Y2;Y3|,
        # then this will return [(X1,Y1),(X2,Y2),(X3,Y3)]
        # xparam and yparam are (generally) the SoEx output parameters that
        # represent coordinates of found objects
        from csv import DictReader
        with open(self.csvpath) as m:
            Xcoords = [row[xparam] for row in DictReader(m)]
        with open(self.csvpath) as n:
            Ycoords = [row[yparam] for row in DictReader(n)]
        # make a list of (X,Y) tuples
        coords = []
        for i in range(len(Xcoords)-1):
            coords.append((Xcoords[i],Ycoords[i]))
        return coords

    # def getHeader(self):
    #     # REVIEW: this should(?) spit out a header and wcs object?
    #     from astropy.io import fits
    #     from astropy.wcs import WCS
    #     self.hdu = fits.open(self.imgpath)[0]
    #     self.wcs = WCS(self.hdu.header)


# from ImageProfile import ImageProfile
# imgprof = ImageProfile('20020109022041d.fits','p20020109-20020109022041d-sex-cat.txt')
# from AsteroidProfile import AsteroidProfile
# ast = AsteroidProfile(5,imgprof,(500,500),'thumbtest1.png',0)
