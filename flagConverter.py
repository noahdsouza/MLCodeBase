'''
Last updated Monday June 24, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

def flagConverter(x):
    v = []
    flags = []
    # Converting the decimal number into its binary equivalent.
    # The index of each item in v corresponds to a power of two
        # ex: v[0]=1 means 2^1 adds into x, v[3]=0 means 2^3 does not
    while(int(x) > 0):
        v.append(int(int(x)%2))
        x = int(int(x)/2)
    # Saving output as a list of the flags
        # ex: if x=135, then v=[1,1,1,0,0,0,0,1], and flags=[1,2,4,128]
    for i in range(0, len(v)):
        if (v[i] == 1):
            flags.append(str(2**i))
    return flags
