# MLCodeBase

#### This is the second of three steps in the [Nugent Lab's](https://github.com/nugent-lab) research into the NEAT Dataset.
#### The contents of this repository (in its current form) build a framework to run a Random Forest classifier on extracted data. This code included does the following:
 
* ```Astaroth.py``` Is a GUI comparable to "Tinder for Asteroids" where a user inputs "left" for "not an asteroid" and "right" for "asteroid" as a classification tool
* ```AsteroidProfile.py``` Is a class which stores information extracted from a single object in a FITS image
* ```ImageProfile.py``` Is a class which store information extracted from a FITS image that has been analyzed by Source Extractor
* ```makeThumbnail.py``` Contains a series of helper functions which clip a found object out of a parent FITS image
* ```TXTtoCSV.py``` Contains two helper functions which take raw Source Extractor output and convert it into a more parsable CSV format
* ```flagConverter.py``` Is a helper function which decodes, identifies, and returns all flags on an object found by Source Extractor
* ```ClearFiles.py``` Is a utility cleanup function used to remove the output of tests of ```Astaroth.py```
