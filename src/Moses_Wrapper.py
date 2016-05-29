'''
Created on May 27, 2016

@author: philip
'''

from subprocess import Popen, PIPE
import os

class Moses_Wrapper(object):
    '''
    classdocs
    '''


    def __init__(self, moses_dir):
        '''
        Constructor
        '''
        self.moses_dir = moses_dir
        self.moses = os.path.join(moses_dir, "bin/moses")
        if not os.path.isfile(self.moses):
            raise Exception("Moses binary not found at " + self.moses)
        
        self.sentence_bleu = os.path.join(moses_dir, "bin/sentence-bleu")
        if not os.path.isfile(self.sentence_bleu):
            raise Exception("sentence-bleu not found at " + self.sentence_bleu)
        
    def create_k_best_list(self, moses_ini, data, list_name, k=100, threads=1):
        with open(data) as k_best:
            process = Popen([self.moses, "threads " + str(threads), "-f", moses_ini, "-n-best-list", list_name, str(k)], stdin=k_best)
            process.communicate()

    def score_sentence_Bleu(self, candidate_file, reference_file, output_file=None):
        if output_file:
            with open(candidate_file) as candidates, open(output_file, "w") as output:
                process = Popen([self.sentence_bleu, reference_file], stdin=candidates, stdout=output)
                process.communicate(input)
        
        else:
            with open(candidate_file) as candidates:
                process = Popen([self.sentence_bleu, reference_file], stdin=candidates, stdout=PIPE)
                return process.communicate()[0]
            
    def merge_k_best_lists(self, list1, list2, out_file):
        k_best_1 = set()
        k_best_2 = set()
         
        with open(list1) as k_best:
            for line in k_best:
                k_best_1.add(line)

        k1_size = len(k_best_1)
                 
        with open(list2) as k_best:
            for line in k_best:
                k_best_2.add(line)
                 
        k_best_1.update(k_best_2)
        updated_size = len(k_best_1)
        changed = k1_size != updated_size

        if changed:
            k_best_sorted = k_best_1
        else:
            k_best_sorted = sorted(k_best_1, key = lambda x : int(x.split()[0]))
         
        with open(out_file, "w") as out:
            for line in k_best_sorted:
                out.write(line)

        return updated_size, changed

    def compute_k_best_length(self, k_best_list):
        length = 0
        with open(k_best_list) as k_best:
            for _ in k_best:
                length += 1