'''
Created on May 27, 2016

@author: philip
'''

from subprocess import Popen
import os

class LibSVM_Wrapper(object):
    '''
    A wrapper class for the LIBSVM command line. Currently only useable for RankSVM.
    '''


    def __init__(self, libsvm_dir):
        '''
        Constructor
        '''
        self.libsvm_dir = libsvm_dir
        self.train = os.path.join(self.libsvm_dir, "train")
    
    def optimise(self, query_list, regularisation_strength, output_file="weights.txt"):
        process = Popen([self.train, "-s 8", "-C " + str(regularisation_strength), query_list, output_file])
        process.communicate()