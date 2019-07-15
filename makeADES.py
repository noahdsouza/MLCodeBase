'''
Last Updated Tuesday July 2, 2019
Author: Noah D'Souza
Designed and Tested in Python 3.6.3
'''

# Three telescopes, make a dictionary of dictionaries with data:
    # {'Palomar' : {design: '', 'aperture': '1.2', detector: 'CCD'}}
    # {'GEODSS'  : {design: '', 'aperture': , detector: 'CCD'}}

# REQUIRED TAGS:
    # obsContext:
        # observatory (mpcCode) {IN REF}
        # submitter (name) {IN REF}
        # observers (name) {IN REF}
        # measurers (name) {IN REF}
        # telescope (design, aperture, detector)
    # obsData
        # identification group (optical)
        # mode                                                  {done}
        # stn
        # obsTime                                               {done}
        # astCat
        # something with permID, provID, artSat, and trkSub
        # ra
        # dec
        # mag
        # band

def convertRow(row):
    return (
            '''

            ''' % ()
            )

def makeADES(dictIn, adesOut, reftxt):
    from dicttoxml import dicttoxml
    import xml.dom.minidom
    from collections import OrderedDict
    # dictIn is the filepath of the AsteroidProfile savefile being converted
    # adesOut is the output filepath
    # reftxt is the filepath of a comma-separated text table with the following:
        # 'Observatory:mpcCode' ('Observatory:name' optional as separate field)
        # 'Submitter:name' ("Name1, Name2, Name3, etc")
        # 'Observer:name' ("Name1, Name2, Name3, etc")'
        # 'Measurer:name' ("Name1, Name2, Name3, etc")
        # 'FundingAgency'
        # 'Comments' ("Comment1, Comment2, Comment3, etc")
    import pickle
    savefile = pickle.load(open(dictIn, 'rb'))
    header = HeaderToDict(savefile['thumbheader'])
    soex = savefile['SoExData'] # this is a dictionary

    # time to actually write the XML
    class Node(object):
        def __init__(self, name):
            self._name = name

        def __str__(self):
            return self._name
    e = OrderedDict([('obsBlock',
            # start obsContext and obsData
            OrderedDict([
            ('obsContext',
                OrderedDict([
                ('observatory',
                    OrderedDict([
                    ('mpcCode','568')
                    ])
                ),
                ('submitter',
                    OrderedDict([
                    ('name','I. M. Submit')
                    ])
                ),
                ('observers',
                    OrderedDict([
                    (Node('name'),'I. M. Observit'),
                    (Node('name'),'A. N. Astronomer')
                    ])
                ),
                ('measurers',
                    OrderedDict([
                    (Node('name'),'I. M. Measurit'),
                    (Node('name'),'A. N. Skywatcher')
                    ])
                ),
                ('telescope',
                    OrderedDict([
                    ('design','reflector'),
                    ('aperture','2.2'),
                    ('detector','CCD'),
                    ])
                ),
                ('fundingSource','Name of Funding Agency'),
                ('comment',
                    OrderedDict([
                    (Node('line'),'This is the first comment'),
                    (Node('line'),'This is the second comment')
                    ])
                )
                ])
            ),
            ('obsData',
                # start optical
                OrderedDict([
                    ('optical',
                        # start all the data
                        OrderedDict([
                        ('permID','1234567'),
                        ('provID','2018 AA1234'),
                        ('trkSub','alb2c3d4'),
                        ('mode','CCD'),
                        ('stn','568a'),
                        ('prog','31'),
                        ('obsTime','2016-08-27T12:32:34.12Z'),
                        ('ra','215.6560501'),
                        ('dec','-13.5478723'),
                        ('rmsRA','0.015'),
                        ('rmsDec','0.013'),
                        ('rmsCorr','0.215'),
                        ('astCat','2MASS'),
                        ('mag','21.91'),
                        ('band','w'),
                        ('photCat','PPMXL'),
                        ('photAp','13.3'),
                        ('logSNR','0.78'),
                        ('seeing','0.8'),
                        ('exp','1200'),
                        ('notes','klmnp'),
                        ('remark','High winds affected tracking')
                        ])
                    )
                ])
            )])
        )])
    x = dicttoxml(e, custom_root='ades', attr_type=False)
    d = xml.dom.minidom.parseString(x).toprettyxml
    d = d.replace('<ades>','<ades version="2017">',1)
    with open(adesOut, 'w') as f:
        f.write(d)


def HeaderToDict(header):
    head = {'mode':'CCD'}
    for line in header.split('\n'):
        if line[0:4] == 'DATE-OBS':
            head.append({'obsTime' : line[line.find('=')+3:line.find('=')+22]})

    return head


# TODO add reference text file that includes:
    # Observatory mpcCode (and optional name)
    # Submitter
    # Measurers
    # Name of funding agency
    # Comments
