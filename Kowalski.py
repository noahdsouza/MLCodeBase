'''
Last updated Friday July 12, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''
class Kowalski:

    def __init__(self,forest):
        from sklearn.metrics import confusion_matrix
        from collections import OrderedDict
        '''
        forest is a RunForest object
        How lucky of us to be using binary classification
        This is just a helper class for running metrics on a RandomForest
        prediction set. It import RunForest and RunForest imports it. Cute.
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

    def collect(self):
        import numpy as np
        self.positiveInd = np.where(self.__frst.y_pred_tree==1)
        self.negativeInd = np.where(self.__frst.y_pred_tree==0)
        self.truPosInd, self.falPosInd = [],[]
        self.truNegInd, self.falNegInd = [],[]
        # this finds the index of the result WITHIN the test set self.X_te
        for i in range(len(self.__frst.y_pred_tree)):
            pre = self.__frst.y_pred_tree[i]
            act = self.__frst.y_te[i]
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
