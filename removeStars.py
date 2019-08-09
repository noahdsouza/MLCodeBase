'''
Last updated Wednesday August 7, 2019
Author: Noah D'Souza
Many functions taken from: http://ps1images.stsci.edu/ps1_dr2_api.html
Designed and tested on Python 3.6.3
'''
'''
If you get a "requests.exceptions.SSLError: HTTPSConnectionPool(): Max retries
exceeded with url" error, run "pip install ndg-httpsclient" to fix it
'FITS_CSV/g19960516960516063059a.csv'
'''
def removeStars(csvpath,mag=20):
    # things greater than 20 on the red band can stay
    import pandas as pd
    from time import time
    import multiprocessing
    radius = 1/3600
    data = loadCSV(csvpath)
    # noStars = data.copy()
    manager = multiprocessing.Manager()
    ns = manager.Namespace()
    ns.noStars = data.copy()
    # ret_dict = manager.dict()
    processes = []
    st = time()
    for index,row in data.iterrows():
        process = multiprocessing.Process(target=worker,
            args=(index,row,radius,ns,mag))
        processes.append(process)
    for j in processes:
        j.start()
    print('Working...')
    for k in processes:
        n.join()
    # for index,row in data.iterrows():
    #     ra = row['#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]']
    #     dec = row['#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]']
    #     stars = findStars(ra,dec,radius,{'nDetections.gt':1})
    #     if isinstance(stars, pd.DataFrame):
    #         for i in stars['rMeanPSFMag']:
    #             if i < mag:
    #                 noStars = noStars.drop(index)
    #                 break
    # noStars = noStars.reset_index(drop=True)
    foo = type('foo',(),{'csvpath':csvpath,'radius':radius,
                         'data':data,'noStars':ns.noStars})
    print(time()-st,' seconds')
    return foo

def worker(index,row,radius,ns,mag):
    import pandas as pd
    ra = row['#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]']
    dec = row['#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]']
    stars = findStars(ra,dec,radius,{'nDetections.gt':1})
    if isinstance(stars, pd.DataFrame):
        for i in stars['rMeanPSFMag']:
            if i < mag:
                ns.noStars.drop(index,inplace=True)
                break


def findStars(ra,dec,radius,constraints):
    import pandas as pd
    from io import StringIO
    columns = """objID,raMean,decMean,nDetections,ng,nr,ni,nz,ny,
    gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag""".split(',')
    columns = [x.strip() for x in columns]
    columns = [x for x in columns if x and not x.startswith('#')]
    results = ps1cone(ra,dec,radius,release='dr2',columns=columns,
              verbose=False,**constraints)
    # print first few lines
    # lines = results.split('\n')
    # print(len(lines),"rows in results -- first 5 rows:")
    # print('\n'.join(lines[:6]))
    if results != '':
        return pd.read_csv(StringIO(results),sep=',')
    else:
        return ''

def ps1cone(ra,dec,radius,table="mean",release="dr1",format="csv",columns=None,
            baseurl="https://catalogs.mast.stsci.edu/api/v0.1/panstarrs",
            verbose=False, **kw):
    """
    Do a cone search of the PS1 catalog
    Parameters
    ----------
    ra (float): (degrees) J2000 Right Ascension (BLESS UP)
    dec (float): (degrees) J2000 Declination
    radius (float): (degrees) Search radius (<= 0.5 degrees)
        ** Divide by 3600 to get arcseconds **
    table (string): mean, stack, or detection
    release (string): dr1 or dr2
    format: csv, votable, json
    columns: list of column names to include (None means use defaults)
    baseurl: base URL for the request
    verbose: print info about request
    **kw: other parameters (e.g., 'nDetections.min':2)
    """
    data = kw.copy()
    data['ra'] = ra
    data['dec'] = dec
    data['radius'] = radius
    return ps1search(table=table,release=release,format=format,columns=columns,
                    baseurl=baseurl, verbose=verbose, **data)

def ps1search(table="mean",release="dr1",format="csv",columns=None,
           baseurl="https://catalogs.mast.stsci.edu/api/v0.1/panstarrs",
           verbose=False,**kw):
    import requests
    """
    Do a general search of the PS1 catalog (possibly without ra/dec/radius)
    Parameters
    ----------
    table (string): mean, stack, or detection
    release (string): dr1 or dr2
    format: csv, votable, json
    columns: list of column names to include (None means use defaults)
    baseurl: base URL for the request
    verbose: print info about request
    **kw: other parameters (e.g., 'nDetections.min':2).  Note this is required!
    """
    data = kw.copy()
    if not data:
        raise ValueError("You must specify some parameters for search")
    checklegal(table,release)
    if format not in ("csv","votable","json"):
        raise ValueError("Bad value for format")
    url = "{baseurl}/{release}/{table}.{format}".format(**locals())
    if columns:
        # check that column values are legal
        # create a dictionary to speed this up
        dcols = {}
        for col in ps1metadata(table,release)['name']:
            dcols[col.lower()] = 1
        badcols = []
        for col in columns:
            if col.lower().strip() not in dcols:
                badcols.append(col)
        if badcols:
            raise ValueError('Some columns not found in table: {}'.format(
                ', '.join(badcols)))
        # two different ways to specify a list of column values in the API
        # data['columns'] = columns
        data['columns'] = '[{}]'.format(','.join(columns))
    # either get or post works
    # r = requests.post(url, data=data)
    r = requests.get(url, params=data)
    if verbose:
        print(r.url)
    r.raise_for_status()
    if format == "json":
        return r.json()
    else:
        return r.text

def checklegal(table,release):
    """
    Checks if this combination of table and release is acceptable
    Raises a VelueError exception if there is problem
    """
    releaselist = ("dr1", "dr2")
    if release not in ("dr1","dr2"):
        raise ValueError("Bad value for release (must be one of {})".format(
            ', '.join(releaselist)))
    if release=="dr1":
        tablelist = ("mean", "stack")
    else:
        tablelist = ("mean", "stack", "detection")
    if table not in tablelist:
        raise ValueError(
            "Bad value for table (for {} must be one of {})".format(
            release, ", ".join(tablelist)))


def ps1metadata(table="mean",release="dr1",
           baseurl="https://catalogs.mast.stsci.edu/api/v0.1/panstarrs"):
    from astropy.table import Table
    import json
    import requests
    """
    Return metadata for the specified catalog and table
    Parameters
    ----------
    table (string): mean, stack, or detection
    release (string): dr1 or dr2
    baseurl: base URL for the request
    Returns an astropy table with columns name, type, description
    """
    checklegal(table,release)
    url = "{baseurl}/{release}/{table}/metadata".format(**locals())
    r = requests.get(url)
    r.raise_for_status()
    v = r.json()
    # convert to astropy table
    tab = Table(rows=[(x['name'],x['type'],x['description']) for x in v],
               names=('name','type','description'))
    return tab


def mastQuery(request):
    """
    Perform a MAST query.
    Parameters
    ----------
    request (dictionary): The MAST request json object
    Returns head,content where head is the response HTTP headers,
    and content is the returned data
    """
    server='mast.stsci.edu'
    # Grab Python Version
    version = ".".join(map(str, sys.version_info[:3]))
    # Create Http Header Variables
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "User-agent":"python-requests/"+version}
    # Encoding the request as a json string
    requestString = json.dumps(request)
    requestString = urlencode(requestString)
    # opening the https connection
    conn = httplib.HTTPSConnection(server)
    # Making the query
    conn.request("POST", "/api/v0/invoke", "request="+requestString, headers)
    # Getting the response
    resp = conn.getresponse()
    head = resp.getheaders()
    content = resp.read().decode('utf-8')
    # Close the https connection
    conn.close()
    return head,content

def resolve(name):
    """
    Get the RA and Dec for an object using the MAST name resolver
    Parameters
    ----------
    name (str): Name of object
    Returns RA, Dec tuple with position"""
    resolverRequest = {'service':'Mast.Name.Lookup',
                       'params':{'input':name,
                                 'format':'json'
                                },
                      }
    headers,resolvedObjectString = mastQuery(resolverRequest)
    resolvedObject = json.loads(resolvedObjectString)
    # The resolver returns a variety of information about the resolved object,
    # however for our purposes all we need are the RA and Dec
    try:
        objRa = resolvedObject['resolvedCoordinate'][0]['ra']
        objDec = resolvedObject['resolvedCoordinate'][0]['decl']
    except IndexError as e:
        raise ValueError("Unknown object '{}'".format(name))
    return (objRa, objDec)

'''
This one was written by Noah
'''
def loadCSV(csvpath):
    import pandas as pd
    # csvpath includes the directory name 'FITS_CSV/''
    f = open(csvpath,'r')
    data = pd.read_csv(f)
    f.close()
    return data

# def removeStars(csvpath,mag=20):
#     # things greater than 20 on the red band can stay
#     import pandas as pd
#     from time import time
#     import multiprocessing
#     radius = 1/3600
#     data = loadCSV(csvpath)
#     # noStars = data.copy()
#     manager = multiprocessing.Manager()
#     ns = manager.Namespace()
#     ns.noStars = data.copy()
#     # ret_dict = manager.dict()
#     processes = []
#
#     st = time()
#     for i in __________:
#         process = multiprocessing.Process(target=worker,args=())
#         processes.append(process)
#     for j in processes:
#         j.start()
#     print('Working...')
#     for k in processes:
#         n.join()
#     # for index,row in data.iterrows():
#     #     ra = row['#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]']
#     #     dec = row['#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]']
#     #     stars = findStars(ra,dec,radius,{'nDetections.gt':1})
#     #     if isinstance(stars, pd.DataFrame):
#     #         for i in stars['rMeanPSFMag']:
#     #             if i < mag:
#     #                 noStars = noStars.drop(index)
#     #                 break
#
#     # noStars = noStars.reset_index(drop=True)
#     foo = type('foo',(),{'csvpath':csvpath,'radius':radius,
#                          'data':data,'noStars':ns.noStars})
#     print(time()-st,' seconds')
#     return foo
#
# # def worker(index,row,radius,ns):
# #     ra = row['#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]']
# #     dec = row['#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]']
# #     stars = findStars(ra,dec,radius,{'nDetections.gt':1})
# #     if isinstance(stars, pd.DataFrame):
# #         for i in stars['rMeanPSFMag']:
# #             if i < mag:
# #                 ns.noStars.drop(index,inplace=True)
# #                 break
#
# def shouldDelete(data,radius,save=False):
#     import pandas as pd
#     from io import StringIO
#     radec = data[['#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]',
#             '#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]']].copy()
#     radec['star'] = 0
#     result = radec.apply(lambda x: helpDelete(x,radius,{'nDetections.gt':1}),
#         axis=1)
#     return result
#
# def helpDelete(row,radius,constraints):
#     # this is a helper for shouldDelete (used by DataFrame.apply())
#     columns = ['objID', 'raMean', 'decMean', 'nDetections', 'ng', 'nr', 'ni',
#                'nz', 'ny', 'gMeanPSFMag', 'rMeanPSFMag', 'iMeanPSFMag',
#                'zMeanPSFMag', 'yMeanPSFMag']
#     return ps1cone(
#         row['#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]'],
#         row['#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]'],
#         radius,release='dr2',columns=columns,verbose=False,**constraints)
