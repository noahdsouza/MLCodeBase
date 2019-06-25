'''
Last updated Friday June 21, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

def makeThumbnail(img, coord, loc, show, m=5):
    # img should be a string path for an image of FITS type
    # coord should either be a tuple of (X,Y) or (minX,minY,maxX,maxY) format
    # m is the crop margin provided if coord is only (X,Y), default of 5 pixels
    # loc is the save path
    # show decides if the thumbnail will be displayed, default set to no
    # works with everything but FITS images
    from PIL import Image
    imgobj = Image.open(img)
    if len(coord) == 2:
        coordin = (coord[0]-m,coord[1]-m,coord[0]+m,coord[1]+m)
        crop = imgobj.crop(coordin)
        crop.save(loc)
    if len(coord) == 4:
        crop = imgobj.crop(coord)
        crop.save(loc)
    if show==True:
        crop.show()

def FITSprocess(img):
    # img is the FITS image's filepath
    from astropy.io import fits
    from astropy.visualization import ZScaleInterval
    from astropy.visualization import LogStretch
    interval = ZScaleInterval()
    stretch = LogStretch()
    image_data = interval(stretch(fits.getdata(img)))
    return image_data

def FITSthumbnail(image_data, pos, size, loc, show=0):
    # image data is an array with FITS image data (from FITSprocess())
    # pos is the center (X,Y) of the object you want cut out of the FITS image
        # (not pixels)
    # size is a (Y,X) tuple for how large the cutout will be (pixels)
    # if size is a single value, then the thumbnail will be a square
    # loc is the filepath/name (IMPORT PNG+LABELS CLASS LATER)
    # show=0 displays nothing
    # show=1 displays just the cutout
    # show=2 displays the cutout as a bounding box on the original image
    # show=3 displays the cutout and the original image (with bounding box)
    from astropy.nddata import Cutout2D
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as ptch
    import numpy as np

    imgrows = image_data.shape[0]
    imgcols = image_data.shape[1]

    # make cutout data
    cutout = Cutout2D(image_data, pos, size)

    # XXX
    # save the cutout as a PNG
    figC, axC = plt.subplots()
    axC.imshow(cutout.data, cmap='gray', origin='lower')
    axC.spines['bottom'].set_color('blue')
    axC.spines['top'].set_color('blue')
    axC.spines['left'].set_color('blue')
    axC.spines['right'].set_color('blue')
    axC.tick_params(axis='x',colors='blue')
    axC.tick_params(axis='y',colors='blue')
    figC.savefig(loc,facecolor='black')
    plt.close('all')

    # # save cutout image again but with a dot in the center of the objects
    # figD, axD = plt.subplots()
    # im = axD.imshow(image_data, cmap='gray', origin='lower')
    # axD.plot(pos[0],pos[1])
    # axD.spines['bottom'].set_color('blue')
    # axD.spines['top'].set_color('blue')
    # axD.spines['left'].set_color('blue')
    # axD.spines['right'].set_color('blue')
    # axD.tick_params(axis='x',colors='blue')
    # axD.tick_params(axis='y',colors='blue')
    # # barr = np.array([[pos[0]-int(size/2),pos[1]-int(size/2)],
    # #                  [pos[0]+int(size/2),pos[1]+int(size/2)]])
    # # b = matplotlib.transforms.Bbox.from_bounds(pos[0]/100,pos[1]/100,0.4,0.4)
    # patch = ptch.Rectangle((pos[0],pos[1]),40,40)
    # im.set_clip_path(patch)
    # figD.savefig(loc[:-4]+'DOT.png',facecolor='black')
    # plt.close('all')

    # save big image with bounding box
    figB, axB = plt.subplots()
    axB.imshow(image_data, cmap='gray', origin='lower')
    cutout.plot_on_original(color='red')
    axB.spines['bottom'].set_color('blue')
    axB.spines['top'].set_color('blue')
    axB.spines['left'].set_color('blue')
    axB.spines['right'].set_color('blue')
    axB.tick_params(axis='x',colors='blue')
    axB.tick_params(axis='y',colors='blue')
    figB.savefig(loc[:-4]+'F.png',facecolor='black')
    plt.close('all')
    # XXX

    # optional plotting
    plt.close('all')
    if show==1:
        # cutout only
        plt.figure(1)
        plt.imshow(cutout.data, cmap='gray', origin='lower')
        plt.show()
    if show==2:
        # bounding box image only
        plt.figure(1)
        plt.imshow(image_data, cmap='gray', origin='lower')
        cutout.plot_on_original(color='red')
        plt.colorbar()
        plt.show()
    if show==3:
        # both
        plt.figure(1)
        plt.imshow(image_data, cmap='gray', origin='lower')
        cutout.plot_on_original(color='red')
        plt.colorbar()
        plt.figure(2)
        plt.imshow(cutout.data, cmap='gray', origin='lower')
        plt.show()

    return cutout
