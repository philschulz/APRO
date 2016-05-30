'''
Created on May 27, 2016

@author: philip
'''

from subprocess import Popen, PIPE
import os

candidate_txt = "k_best_candidates.txt"
ref_txt = "k_best_references.txt"

class Moses_Wrapper(object):
    '''
    A wrapper class for the Moses MT system.
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
        """
        Create a list of the k-best translations for each sentence in the data and write
        this list to disk. The format of the list is the one used by Moses.

        :param moses_ini: Path to the moses.ini file storing the weights and features used for translation
        :param data: Path to a source language text file with one sentence per line
        :param list_name: Name of the resulting k-best list file. If a file by that name already exists, it will be overwritten
        :param k: The number of k-best translations per sentence
        :param threads: Number of threads to be used by the decoder
        """
        with open(data) as k_best:
            process = Popen([self.moses, "-threads", str(threads), "-f", moses_ini, "-n-best-list", list_name, str(k)], stdin=k_best)
            process.communicate()

    def _score_sentence_Bleu(self, candidate_file, reference_file, output_file=None):
        """
        Score a list of candidate translations with sentence bleu. The candidate and reference files need to
        store the candidates and their respective reference translations in the same order. The resulting
        Bleu scores will be written to disk in the same order if an output file path is provided.

        :param candidate_file: Path to the file containing the candidate translations
        :param reference_file: Path to the file containing the reference translations
        :param output_file: Path to an optional output file to which the Bleu scores are written
        :return: The output Bleu scores as a string, one score per line, if output_file is None. Return nothing otherwise.
        """
        if output_file:
            with open(candidate_file) as candidates, open(output_file, "w") as output:
                process = Popen([self.sentence_bleu, reference_file], stdin=candidates, stdout=output)
                process.communicate(input)
        
        else:
            with open(candidate_file) as candidates:
                process = Popen([self.sentence_bleu, reference_file], stdin=candidates, stdout=PIPE)
                return process.communicate()[0]

    def compute_sentence_bleu(self, k_best_list, references):
        """
        Compute the sentence Bleu score for each item in a k-best list and a reference file that contains
        one reference translation for each source sentence from which the k-best list was generated.

        :param k_best_list: Path to the Moses-style k-best list
        :param references: Path to a file containing reference translations
        :return: A list of string representing Bleu scores in the order of candidates in the k-best list
        """
        ref = list()

        with open(references) as refs:
            for line in refs:
                ref.append(line)

        with open(k_best_list) as k_best, open(candidate_txt, "w") as candidates, open(ref_txt, "w") as references:
            for line in k_best:
                fields = line.split(" ||| ")
                sent_num = int(fields[0])
                text = fields[1].strip()
                candidates.write(text + "\n")
                references.write(ref[sent_num])

        bleu = self._score_sentence_Bleu(candidate_txt, ref_txt)
        bleu_list = bleu.split("\n")

        return bleu_list

    def merge_k_best_lists(self, list1, list2, out_file):
        """
        Merge two k-best-lists in Moses format and write the merged list to disk. Return a tuple containing
        the size of the merged list and an indicator for whether this size is different from the first arguments
        size.

        :param list1: A k-best list that serves as reference
        :param list2: A k-best list to be merged with list1
        :param out_file: Path to which the merged list will be written
        :return: size of the merged list, boolean indicator of whether the merged list is longer than list1
        """
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
        k_best_sorted = sorted(k_best_1, key = lambda x : int(x.split()[0]))
         
        with open(out_file, "w") as out:
            for line in k_best_sorted:
                out.write(line)

        return updated_size, changed

    def compute_k_best_length(self, k_best_list):
        """
        Compute the length of a k-best list in terms of its lines

        :param k_best_list: Path to the k-best list
        :return: The length of the k-best list
        """
        length = 0
        with open(k_best_list) as k_best:
            for _ in k_best:
                length += 1

        return length