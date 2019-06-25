'''
Last updated Thursday June 20, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

# This is just a utility script to make my life easier when testing AsTroid.py
# Pay no attention to this script unless you also want to get rid of all the
# AsTroid output periodically

import os, shutil

yea = 'YES/'
nah = 'NO/'
may = 'MAYBE/'

filelistY = [ f for f in os.listdir(yea)]
for f in filelistY:
    shutil.rmtree(yea + f)

filelistN = [ g for g in os.listdir(nah)]
for g in filelistN:
    shutil.rmtree(nah + g)

filelistM = [ h for h in os.listdir(may)]
for h in filelistM:
    shutil.rmtree(may + h)

if os.path.isfile('txtpath.txt'):
    os.remove('txtpath.txt')
