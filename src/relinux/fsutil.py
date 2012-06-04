'''
General filesystem utilities
@author: Anonymous Meerkat
'''

import os

def makedir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def maketree(arr):
    for i in arr:
        makedir(i)