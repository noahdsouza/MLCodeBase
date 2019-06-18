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
