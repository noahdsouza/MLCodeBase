'''
Last updated Monday July 29, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''
class Kowalski:

    def __init__(self,forest):
        from sklearn.metrics import confusion_matrix
        from sklearn.metrics import recall_score,precision_score,accuracy_score
        from sklearn.metrics import make_scorer
        from collections import OrderedDict
        '''
        forest is a RunForest object, and becomes the __frst private attribute
        How lucky of us to be using binary classification
        This is just a helper class for running metrics on a RandomForest
        prediction set. It imports RunForest and RunForest imports it. Cute.
        If only my parents' marriage worked that well.
        '''
        self.__frst = forest
            # making this private to avoid confusion in RunForest
        if not (hasattr(self.__frst, 'X_tr') and
                hasattr(self.__frst, 'X_te') and
                hasattr(self.__frst, 'y_tr') and
                hasattr(self.__frst, 'y_te') and
                hasattr(self.__frst, 'y_pred_tree')):
                self.__frst.runRFC()
        self.tn, self.fp, self.fn, self.tp = confusion_matrix(
            self.__frst.y_te, self.__frst.y_pred_tree).ravel()
        fi = dict(zip(self.__frst.X_tr.columns,
            self.__frst.f.feature_importances_))
        self.ftImp = OrderedDict()
        # I would use a regular dictionary, but order is so hard to keep track
        # of with this data that I'm using an OrderedDict just to be safe.
        for k,v in sorted(fi.items(), reverse=True, key=lambda item: item[1]):
            self.ftImp[k] = v
        self.recall = recall_score(self.__frst.y_te, self.__frst.y_pred_tree)
        # "The recall is intuitively the ability of the classifier to find all
        # the positive samples."
        self.precision = precision_score(self.__frst.y_te,
            self.__frst.y_pred_tree)
        self.param_grid = {
            'min_samples_split' : [3,5,10],
            'n_estimators' : [100,300],
            'max_depth' : [3,5,15,25],
            'max_features' : [3,5,10,20]
        }
        self.scorers = {
            'precision_score' : make_scorer(precision_score),
            'recall_score' : make_scorer(recall_score),
            'accuracy_score' : make_scorer(accuracy_score)
        }
        # "The precision is intuitively the ability of the classifier not to
        # label as positive a sample that is negative."

    def collect(self):
        import numpy as np
        '''
        Essentially the main function of this class. It extracts the
        true-positives, false-positives, true-negatives, and false-negatives
        from the data (and confusion matrix) and puts them in little piles.
        Conveniently, the data that needed to be dropped to make the training
        set is plopped back in. You're welcome, me.
        '''
        self.positiveInd = np.where(self.__frst.y_pred_tree==1)
        self.negativeInd = np.where(self.__frst.y_pred_tree==0)
        self.truPosInd, self.falPosInd = [],[]
        self.truNegInd, self.falNegInd = [],[]
        # this finds the index of the result WITHIN the test set self.X_te
        for i in range(len(self.__frst.y_pred_tree)):
            pre = self.__frst.y_pred_tree[i]
            act = self.__frst.y_te.iloc[i]
            if pre == 1 and pre == act:
                self.truPosInd.append(i)
            if pre == 1 and pre != act:
                self.falPosInd.append(i)
            if pre == 0 and pre == act:
                self.truNegInd.append(i)
            if pre == 0 and pre != act:
                self.falNegInd.append(i)
        self.truPos, self.falPos, self.truNeg, self.falNeg = [],[],[],[]
        for i in self.truPosInd:
            self.truPos.append(self.__frst.X_te.iloc[i,:])
        for i in self.falPosInd:
            self.falPos.append(self.__frst.X_te.iloc[i,:])
        for i in self.truNegInd:
            self.truNeg.append(self.__frst.X_te.iloc[i,:])
        for i in self.falNegInd:
            self.falNeg.append(self.__frst.X_te.iloc[i,:])
        self.attachTags()

    def attachTags(self):
        # remember that truPos/falPos/truNeg/falNeg are LISTS
        '''
        This facilitates reattaching the dropped data
        (see: RunForest.makeTrainSet()) so you can see which files are messing
        everything up.
        '''
        for i in [self.truPos, self.falPos, self.truNeg, self.falNeg]:
            for row in i: # row is a pandas Series
                testname = row.name
                # NOTE: This converts #_46_AST_STATUS from encoded to unencoded
                row['#_46_AST_STATUS'] = 'YES' if (
                    self.__frst.targets[testname]==1) else 'NO'
                row['#_47_THUMB_PATH'] = self.__frst.fnames[testname]

    def optimize(self, refit_score='recall_score'):
        from sklearn.ensemble import RandomForestClassifier
        from time import time
        '''
        You might want to run this one on a fast computer. It tests every
        combination of RandomForestClassifier parameters you give it (see:
        param_grid in __init__) and pumps out the best one (and its confusion
        matrix). Sorry for using a brute-force strategy, @NickSteelman
        '''
        st = time()
        # NB: remember that __clf is NOT a RunForest object
            # It's a fresh and clean new RandomForestClassifier object
        self.__clf = RandomForestClassifier(n_jobs=-1)
        # the code this is based on returns 'grid_search' (GridSearchCV object)
        # here it is stored in the 'grid_search' attribute instead because
        # returning objects is for classless (haha, get it?) chumps
        self.__grid_search_wrapper(refit_score)
        print('RUNTIME: ',time()-st)

    def __grid_search_wrapper(self, refit_score='recall_score'):
        from sklearn.model_selection import GridSearchCV, StratifiedKFold
        from sklearn.metrics import roc_curve, precision_recall_curve, auc
        from sklearn.metrics import make_scorer, recall_score, accuracy_score
        from sklearn.metrics import precision_score, confusion_matrix
        import pandas as pd
        """
        Taken from:
        https://towardsdatascience.com/
        fine-tuning-a-classifier-in-scikit-learn-66e048c21e65
        (and then edited, of course)
        fits a GridSearchCV classifier using refit_score for optimization
        Helper method for optimize(), does a lot of the heavy lifting
        """
        skf = StratifiedKFold(n_splits=10)
        self.grid_search = GridSearchCV(self.__clf, self.param_grid,
            scoring=self.scorers, refit=refit_score, cv=skf,verbose=100,
            return_train_score=True, n_jobs=-1)
        self.grid_search.fit(self.__frst.X_tr.values, self.__frst.y_tr.values)
        # Use .best_params_ attribute of grid_pred
        self.grid_pred = self.grid_search.predict(self.__frst.X_te.values)
        self.optConfMatrix = pd.DataFrame(
            confusion_matrix(self.__frst.y_te,self.grid_pred),
            columns=['pred_neg','pred_pos'],index=['neg','pos'])

    # Pay no attention to this incredibly important static method
    @staticmethod
    def kowalskiAnalysis():
        print(
        """
                                                   ...'',,,''.........';::;'.
                                               ..,:llolcc:;;'....',:codxkkdc,.
                                             .:okkkxddoccc:;,;;clodxddddxxxc,'.
                                           .ckxdolc:;;,,,;:ccclodddddddddddl;;'
                                           ,Ok:,,''....';:dO0xooxxdddoodddddddl
                                          .lK0x:;;,'',:::;;xKkooxxdoooooooddodo
                                          .kXK0koclolc::clloolclolccccllooooooo
                                          ;0XK00Odolccc:;:c:::cc:;;,,''',;:clll
                                          :KK0Okxdolloocccccc:;,'..'',,,,;;:cco
                                          :kxdddoodxocc::cc;,..',;:ccccccccccdO
                                          ,dddoooddoc::::;'..';:clllooollolokkl
                                          .o0K0Oxxxoc:;,'.',;;:cloooddddddkOd:,
                                          .;xKXK0xo:'....'',,;codxxxxxxxkOkl;,,
                                         ..,,dKXXKOxl;;,,,,,;lxOOkkkkkkOOd:;,,,
                                         ....'oKXXKKkl:;;;;;lx00OOOkkkOkl;,,;,,
                                     ....,,''.,dXXKXKkl::c:lk0K00OOkOOd:;,,,,,,
     Kowalski, analysis...          .:dxooooo;:xXXKKKKOxkxdO00K00OOOkl:;;,,,,,,
                                   ,lododdcloodOKKKKXX0O0K0K0O00OOkdc;;;,,,,,,,
                                   .';cllc;',;lOKKKKKXK0KK00OOOOOxl:;;;;,,,,,;;
                                   ..,clc;,..:xKKKKKKKKK0000OOkko:;;;;;,,,,,;;;
....................................';::;,,,,oO00000OOkkdooodxdc;;;;;,,,,,,;;;:
...................................'';;,,,;:cclooollc::;,'.',,;;;,;;,,,,,,;;;::
        """)




if __name__ == '__main__':
    print('''
        Kowalski, analysis...
    ''')
