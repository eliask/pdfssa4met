""" Utility functions and classes for pdfssa4met.

Created on Mar 1, 2010
@author: John Harrison
"""

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def mean(mylist):
    """ Calculate the mean average of the numbers in a list """
    return sum([float(x) for x in mylist]) / len(mylist)

def median(mylist):
    """ Calculate the median average of the numbers in a list """
    mylist = [float(x) for x in mylist]
    mylist.sort()
    return mylist[int(len(mylist)/2)]
