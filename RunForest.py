'''
Last updated Monday July 29, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

# def timer(func):
#     # I may not work, don't worry about me
#     def timed(*args, **kw):
#         ts = time.time()
#         result = func(*args, **kw)
#         te = time.time()
#         print(func.__name__, ' time: ', te-ts)

class RunForest:

    # These are generally good parameters. Use them if you want.
    # FIXME: I'm not sure if this is super necessary/pythonic
    testsize = 0.5
    randomstate = 23

    def __init__(self):
        import pandas as pd
        # import sys
        '''
        This is a class structure for running SciKit Learn's Random Forest
        Classifier module on data that has been user-classified and preprocessed
        in Astaroth.py (and previous pipeline steps)
        Have fun with the RunForest.runforrest() static method lol  :)
        '''
        # self.verbose = None
        self.prepDictList() # defines the dictlist
        self.df = pd.DataFrame(self.dictlist).dropna()
        self.groups = self.df.groupby('#_46_AST_STATUS')
        self.ts = RunForest.testsize
        self.rs = RunForest.randomstate

    def __str__(self):
        # print('RunForest object')
        if not (hasattr(self, 'X_tr') and hasattr(self, 'X_te') and
                hasattr(self, 'y_tr') and hasattr(self, 'y_te')):
            return 'RunForest Object \nNo training set made yet'
        if hasattr(self, 'analysis'):
            return '''
            RunForest object
            True Positives:  %s
            False Positives: %s
            True Negatives:  %s
            False Negatives: %s
            ''' % (self.analysis.tp, self.analysis.fp,
                   self.analysis.tn, self.analysis.fn)
        elif hasattr(self, 'y_pred_tree'):
            return 'RunForest object \nFit has been run'

    def prepDictList(self):
        import os
        '''
        Scrapes (properly constructed) directories for data and turns turns it
        into a giant list of dictionaries
        '''
        self.dictlist = []
        # self.foldernames = []
        for fname in os.listdir('NO/'):
            self.dictlist.append(RunForest.prepDict('NO',fname))
            # self.foldernames.append(fname+'.png')
        for fname in os.listdir('YES/'):
            self.dictlist.append(RunForest.prepDict('YES',fname))
            # self.foldernames.append(fname+'.png')
        # for fname in os.listdir('MAYBE/'):
        #     # only use this one if you're using 'MAYBE' objects
        #     self.dictlist.append(RunForest.prepDict('MAYBE',fname))

    def plotGroups(self):
        '''
        Fairly obsolete method for visualizing which data points have been
        classified as asteroid/not-asteroid by a user
        '''
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        for name, group in self.groups:
            ax.plot(group[
                '#_5_XWIN_IMAGE_Windowed_position_estimate_along_x_[pixel]'],
                    group[
                '#_6_YWIN_IMAGE_Windowed_position_estimate_along_y_[pixel]'],
                    marker='o', linestyle='')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height*0.8])
        ax.legend(['YES','NO'],title='Status',loc='center left',
                  bbox_to_anchor=(1,0.5))
        plt.show()

    def makeTrainSet(self,ts=testsize,rs=randomstate):
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelBinarizer
        '''
        Splits the prepared set into training and test sets, dropping all
        features that are shitty or just can't be encoded. The targets and
        filenames are saved into attributes before being dropped, so don't trip.
        '''
        # ts is a float portion of the data put into the test set
        # rs is an int seed for the random state
        if ts != RunForest.testsize:
            self.ts = ts
        if rs != RunForest.randomstate:
            self.rs = rs
        if '#_46_AST_STATUS' in self.df:
            le = LabelBinarizer()
            # le.fit(['NO','YES'])
            self.df['#_46_AST_STATUS'] = le.fit_transform(
                self.df['#_46_AST_STATUS'].values)
            # self.df['#_47_THUMB_PATH'] = le.fit_transform(
            #     self.df['#_47_THUMB_PATH'].values)
            self.targets = self.df['#_46_AST_STATUS']
            self.fnames = self.df['#_47_THUMB_PATH']
            # self.encoded = le.transform(self.df['#_46_AST_STATUS'])
            self.df.drop(['#_46_AST_STATUS',
        '#_47_THUMB_PATH',
        # '#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]',
        # '#_17_X_IMAGE_DBL_Object_position_along_x_(double_precision)_[pixel]',
        # '#_18_Y_IMAGE_DBL_Object_position_along_y_(double_precision)_[pixel]',
        # '#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]',
        '#_2_FLAGS_Extraction_flags_'],
        axis=1, inplace=True)
        # self.df.drop([
        # '#_46_AST_STATUS',
        # '#_47_THUMB_PATH',
        # # '#_11_XMIN_IMAGE_Minimum_x-coordinate_among_detected_pixels_[pixel]',
        # # '#_15_X_IMAGE_Object_position_along_x_[pixel]',
        # # '#_3_ALPHAWIN_J2000_Windowed_right_ascension_(J2000)_[deg]',
        # # '#_17_X_IMAGE_DBL_Object_position_along_x_(double_precision)_[pixel]',
        # # '#_13_XMAX_IMAGE_Maximum_x-coordinate_among_detected_pixels_[pixel]',
        # # '#_5_XWIN_IMAGE_Windowed_position_estimate_along_x_[pixel]',
        # # '#_18_Y_IMAGE_DBL_Object_position_along_y_(double_precision)_[pixel]',
        # # '#_6_YWIN_IMAGE_Windowed_position_estimate_along_y_[pixel]',
        # # '#_14_YMAX_IMAGE_Maximum_y-coordinate_among_detected_pixels_[pixel]',
        # # '#_12_YMIN_IMAGE_Minimum_y-coordinate_among_detected_pixels_[pixel]',
        # # '#_4_DELTAWIN_J2000_windowed_declination_(J2000)_[deg]',
        # # '#_16_Y_IMAGE_Object_position_along_y_[pixel]',
        # # '#_1_NUMBER_Running_object_number_',
        # '#_2_FLAGS_Extraction_flags_']
        # X_tr is a DataFrame of the training set's features
        # X_te is a DataFrame of the test set's features
        # y_tr is a numpy array of the training set's labels (binary encoded)
        # y_te is a numpy array of the test set's labels (binary encoded)
        self.X_tr, self.X_te, self.y_tr, self.y_te = train_test_split(self.df,
            self.targets, stratify=self.targets,
            test_size=self.ts,
            random_state=self.rs)

    def runRFC(self, tsR=testsize, rsR=randomstate):
        from sklearn.ensemble import RandomForestClassifier as RFC
        '''
        Runs a RandomForestClassifier on the training set and fits it to the
        test set. Compare y_pred_tree to y_te to get analytics
        '''
        # from sklearn.ensemble import ExtraTreesClassifier as ETC
        if not (hasattr(self, 'X_tr') and hasattr(self, 'X_te') and
                hasattr(self, 'y_tr') and hasattr(self, 'y_te')):
            # print("NO TRAINING SET FOUND. MAKING TRAINING SET NOW...")
            self.makeTrainSet(ts=tsR,rs=rsR)
        elif ((self.ts != tsR or RunForest.testsize != tsR) or
              (self.rs != rsR or RunForest.randomstate != rsR)):
            self.ts = tsR
            self.rs = rsR
            self.makeTrainSet(ts=tsR,rs=rsR)
        else:
            if tsR == self.ts:
                print('tsR INPUT IS SAME AS CURRENT VALUE. IGNORING.')
            if rsR == self.rs:
                print('rsR INPUT IS SAME AS CURRENT VALUE. IGNORING.')
            print("USING PRE-EXISTING TRAINING SET. IGNORING KEYWORD ARGUMENTS.")
            print("RE-RUN RunForest.makeTrainSet() IF YOU WANT NEW KWARGS.")
        # NB:   These RFC parameters can be changed!! Please do!!
            # NOTE: They have been optimized with Kowalski.optimize() though
        # NOTE: increasing n_jobs sometimes makes this slower, so consider that
        self.f = RFC(n_estimators=100,
                     max_features=3,
                     # oob_score=True,
                     max_depth=3,
                     min_samples_split=10,
                     verbose=1)
        self.f.fit(self.X_tr, self.y_tr)
        self.y_pred_tree = self.f.predict(self.X_te)

    def plotRFC(self):
        import matplotlib.pyplot as plt
        '''
        Plots color-coordinated test set (stars, yellow=predicted positive,
        purple=predicted negative) on the training set (dots, red=actual
        positive, blue=actual negative) in a position (actual locations)
        '''
        fig, ax = plt.subplots()
        sc = ax.scatter(
            self.X_te[
                '#_5_XWIN_IMAGE_Windowed_position_estimate_along_x_[pixel]'
            ],
            self.X_te[
                '#_6_YWIN_IMAGE_Windowed_position_estimate_along_y_[pixel]'
            ],
            c = self.y_pred_tree,
            cmap = plt.cm.viridis,
            marker = '*',
            s = 300,
            alpha = 0.5)
        plt.colorbar(sc)
        for name, group in self.groups:
            ax.scatter(
                group[
                '#_5_XWIN_IMAGE_Windowed_position_estimate_along_x_[pixel]'
                ],
                group[
                '#_6_YWIN_IMAGE_Windowed_position_estimate_along_y_[pixel]'
                ],
                marker='o')
        plt.show()


    def analytics(self):
        from Kowalski import Kowalski
        '''
        Makes a Kowalski object for analysis purposes. See Kowalski.py for more
        details. There will likely be more to this at some point. I think.
        '''
        self.analysis = Kowalski(self)
        self.analysis.collect()

# -------------------------- ENTER: STATIC METHODS -------------------------- #

    @staticmethod
    def typeFix(d):
        '''
        Static helper method for prepDict()
        Turns numbers stored as strings (in a dictionary) into ints or floats
        '''
        for key in list(d):
            if key == d[key]:
                d.pop(key)
            elif '.' not in d[key] and d[key]!='YES' and d[key]!='NO':
                d[key] = int(d[key])
            elif '.' in d[key] and d[key]!='YES' and d[key]!='NO':
                d[key] = float(d[key])

    @staticmethod
    def prepDict(dec, fn):
        import pickle
        '''
        Static helper method for prepDictList(). Does initial loading and
        converting (with help from other helpers, of course)
        dec is 'YES', 'NO', or 'MAYBE'
        fn is a filename, not a path
        '''
        # dec is 'YES', 'NO', or 'MAYBE'
        # fn is a filename
        tempdict = pickle.load(open((dec+'/'+fn+'/'+fn+'.dict'),'rb'))
        thumbpath = tempdict['thumbpath']
        tempdict = tempdict['SoExData']
        RunForest.typeFix(tempdict)
        if dec == 'NO':
            tempdict['#_46_AST_STATUS'] = dec
        # else: # this one throws all 'MAYBE' objects into the 'YES' pile
        #     tempdict['#_46_AST_STATUS'] = 'YES'
        elif dec == 'YES':
            tempdict['#_46_AST_STATUS'] = dec
        tempdict['#_47_THUMB_PATH'] = thumbpath
        return tempdict

    @staticmethod
    def repeatOffenders(num):
        # import random
        import multiprocessing
        '''
        Runs through runRFC() a bunch of times, recording which objects appear
        as false-negatives most often (so that no asteroids can kill us)
        num is just how many loops you want to run
        '''
        manager = multiprocessing.Manager()
        ret_dict = manager.dict()
        processes = []
        for i in range(num):
            process = multiprocessing.Process(target=RunForest.workerRO,
                args=(i,ret_dict))
            processes.append(process)
        for m in processes:
            m.start()
            # print('Starting:',m)
        print('Working...')
        for n in processes:
            n.join()
            # print('Ending:  ',n)
        return ret_dict

    @staticmethod
    def thickLoop():
        # It's called thickLoop cause the loop is DUMMY thick.
        # Like, it takes a while to run (x/xr and y dependent)
        import matplotlib.pyplot as plt
        import numpy as np
        from time import time
        import multiprocessing
        '''
        Self-explanatory name: this function has a DUMMY-thicc loop that runs
        runRFC() with different test sizes and random states and then graphs
        the elements of a confusion matrix on one monstrous graph
        Made it a static method so it isn't too reliant on the class
        '''
        tpt, fpt, tnt, fnt = [],[],[],[]
        x = np.linspace(0.95,0.05,20)
        xr = np.linspace(0.05,0.95,20)
        # y = [21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43]
        y = [23,37,43]
        # y = [23,25,27,29,31,33,35,37,39,41,43]
        # y = [42]
        fig, ax = plt.subplots()
        # let's do some multiprocessing, bitch
        st = time() # just for getting the runtime
        manager = multiprocessing.Manager()
        ret_dict = manager.dict()
        processes = []
        for i in y:
            process = multiprocessing.Process(target=RunForest.workerTL,
                args=(x,i,ret_dict))
            processes.append(process)
        for m in processes:
            m.start()
            print('Starting:',m)
        print('Working...')
        for n in processes:
            n.join()
            print('Ending:  ',n)
        # RunForest.print_ret_dict(ret_dict) # uncomment to print ret_dict
        for k,v in ret_dict.items():
            ax.plot(xr,v['tpt'],'ro-', xr,v['fpt'],'bs-' ,
                    xr,v['tnt'],'g^-' ,xr,v['fnt'],'y*-')
        print(time()-st)
        ax.set_xlabel('Training Set Percentage (decimal)')
        ax.set_ylabel('Rate')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.set_facecolor('black')
        fig.set_facecolor('black')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='x',colors='white')
        ax.tick_params(axis='y',colors='white')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height*0.8])
        ax.legend(['TruPos','FalPos','TruNeg','FalNeg'],title='Rates',
                  loc='center left', bbox_to_anchor=(1,0.5))
        plt.show()

    # I'm a helper function for the mainloop
    @staticmethod
    def workerTL(x,i,ret_dict):
        tpt, fpt, tnt, fnt = [],[],[],[]
        '''
        Static helper method for thickLoop(). It's basically just a worker for
        multiprocessing purposes
        '''
        rf = RunForest()
        for j in x:
            rf.runRFC(tsR=j, rsR=i)
            rf.analytics()
            tpt.append(rf.analysis.tp/(rf.analysis.tp+rf.analysis.fn))
            fpt.append(rf.analysis.fp/(rf.analysis.fp+rf.analysis.tn))
            tnt.append(rf.analysis.tn/(rf.analysis.tn+rf.analysis.fp))
            fnt.append(rf.analysis.fn/(rf.analysis.fn+rf.analysis.tp))
        ret_dict[i] = {'tpt':tpt, 'fpt':fpt, 'tnt':tnt, 'fnt':fnt}

    @staticmethod
    def workerRO(i,ret_dict):
        import random
        '''
        Static helper method for repeatOffenders(). Again, just a worker method
        to facilitate multiprocessing
        '''
        rf = RunForest()
        # repeats = {}
        # for i in range(num):
        rf.runRFC(rsR=random.randint(20,57))
        rf.analytics()
        rf.analysis.collect()
        pics = []
        for i in rf.analysis.falNeg:
            pics.append(i['#_47_THUMB_PATH'][:-4])
        for j in pics:
            if j not in ret_dict:
                ret_dict[j] = 0
            elif j in ret_dict:
                ret_dict[j] = ret_dict[j] + 1

    @staticmethod
    def print_ret_dict(ret):
        # use this for pretty-printing the ret_dict from thickLoop()
        for k,v in ret.items():
            print(k,'{')
            for k1,v1 in v.items():
                print('    ',k1,'{')
                for v2 in v1:
                    print('        ',v2)
                print('        }')
            print('     }')

    # NOTE: VERY IMPORTANT STATIC METHOD. DO NOT DELETE!!!!
    @staticmethod
    def runforrest():
        import random
        '''
        Arguably the most important method in this class. Do not delete or I
        WILL track you down and cry uncontrollably until you put it back.
        '''
        x = random.randint(1,11)
        if x==1:
            print("""
            I don't know if we each have a destiny,
            or if we're all just floatin' around accidental-like on a breeze,
            but I, I think maybe it's both.
            Maybe both is happenin' at the same time
            """)
        if x==2:
            print("""
            Life is like a box a chocolate,
            you never know what your going to get.
            """)
        if x==3:
            print("""
            My mama says that stupid is as stupid does.
            """)
        if x==4:
            print("""
            What's normal anyways?
            """)
        if x==5:
            print(r"""
             ___   _   _ _   _
            |  _ \| | | | \ | |
            | |_) | | | |  \| |
            |  _ <| |_| | |\  |
            |_| \_\\___/|_| \_|
             _____ ___  ____  ____  _____ ____ _____
            |  ___/ _ \|  _ \|  _ \| ____/ ___|_   _|
            | |_ | | | | |_) | |_) |  _| \___ \ | |
            |  _|| |_| |  _ <|  _ <| |___ ___) || |
            |_|   \___/|_| \_\_| \_\_____|____/ |_|
             ____  _   _ _   _ _
            |  _ \| | | | \ | | |
            | |_) | | | |  \| | |
            |  _ <| |_| | |\  |_|
            |_| \_\\___/|_| \_(_)
            """)
        if x==6:
            print('''
            "Have you found Jesus yet, Gump?"
            "I didn't know we were supposed to be lookin' for him, sir"
            ''')
        if x==7:
            print("""
            YES DRILL SERGEANT
            """)
        if x==8:
            print("""
            I'm not a smart man, but I know what love is.
            """)
        if x==9:
            print("""
            And we was looking for a guy named Charlie.
            Never did find that Charlie.
            """)
        if x==10:
            print("""
            (talking to John F. Kennedy) I gotta pee
            """)
        if x==11:
            print("""
            There's shrimp stew, shrimp salad, shrimp and potatoes...
            There's pineapple shrimp, lemon shrimp, coconut shrimp,
            pepper shrimp, shrimp soup, shrimp stew, shrimp salad,
            shrimp and potatoes, shrimp burger...
            """)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # # print('yeet')
    # from time import time
    # recalls = 0
    # runs = 20
    # st = time()
    # rfc = RunForest()
    # for i in range(runs):
    #     rfc.runRFC()
    #     rfc.analytics()
    #     recalls = recalls + rfc.analysis.recall
    # # print(rfc.analysis.recall)
    # print('RUNTIME: ',time()-st)
    # print(recalls/runs)
    # # print(rfc.analysis.ftImp)

    # rf = RunForest()
    # rf.runRFC()
    # rf.analytics()
    # rf.analysis.optimize()
    # print(rf.analysis.grid_search.best_params_)
    # print(rf.analysis.optConfMatrix)

    rf = RunForest()
    inds = []
    pnts = []
    for i in range(27,50):
        rf.makeTrainSet(ts=0.5,rs=i)
        rf.runRFC()
        rf.analytics()
        inds.append(i)
        pnts.append(rf.analysis.recall)
    fig, ax = plt.subplots()
    ax.plot(inds,pnts,'b.')
    ax.set_xlabel('Random State')
    ax.set_ylabel('Recall %')
    plt.show()

#           max_depth = 3
#        max_features = 10
#   min_samples_split = 5
#        n_estimators = 100















# oof
