'''
Created on May 27, 2016

@author: Philip Schulz
'''

import sys, os
from subprocess import Popen, PIPE

word_penalty = "UnknownWordPenalty0"

def _is_numeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False   

class SVM_Query_Constructor(object):
    '''
    Constructs queries in the format needed by RankSVM
    '''

    def __init__(self, moses_ini):
        '''
        Constructor
        '''
        self.num_features = 0
        # a map from feature names to lists of weights indices
        self.feature_map = dict()
        self.moses_ini = moses_ini
        self._read_weights_from_moses_ini(moses_ini)

    def _read_weights_from_moses_ini(self, moses_ini):
        """
        Reads a moses.ini file to determine the number of weights used by the decoder

        :param moses_ini: Path to the relevant moses.ini
        :return: A list storing the weights
        """

        with open(moses_ini) as ini:
            for line in ini:
                if "[weight]" in line:
                    break;
            
            for line in ini:
                mapping = line.split("=")
                if len(mapping) > 0 and not word_penalty in mapping[0]:
                    key = mapping[0]
                    current_weights = [item for item in mapping[1].strip(" \n").split(" ")]
                    value = range(self.num_features, self.num_features + len(current_weights))
                    self.num_features = self.num_features + len(current_weights)
                    self.feature_map[key] = value
                
    def _construct_sentence_query(self, qid, bleu, features_string):
        """
        Constuct a query suitable for RankSVM from a string containing the feature
        values for this query in Moses k-best format.

        :param qid: The id of the query
        :param bleu: The Bleu score for this query
        :param features_string: A string containing features from a Moses k-best list
        :return: The query in string format
        """
        query = [bleu + " qid:"+ str(qid)]
        feature_values = dict()
        features = features_string.strip().split()

        i = 0
        while i < len(features):
            field = features[i]
            if not _is_numeric(field):
                field = field.strip("=")
                feature_idx = self.feature_map[field]
                for idx in feature_idx:
                    i += 1
                    feature_values[idx] = features[i]
                i += 1
        
        query += [str(idx + 1) + ":" + feature_values[idx] for idx in xrange( self.num_features)]
        return " ".join(query)
    
    def write_query_file(self, bleu_list, k_best_list, name="query_list"):
        """
        Write a RankSVM data file in which all sentences from the k-best list belong to the
        same query.

        :param moses_wrapper: A Moses_Wrapper object
        :param k_best_list: Path to the k-best list for which to construct the
        :param references:
        :param name:
        """

        i = 0
        sys.stderr.write("Creating query list\n")
        with open(k_best_list) as k_best, open(name, "w") as out:
            for line in k_best:
                fields = line.split(" ||| ")
                sent_num = fields[0].strip()
                features = fields[2].strip()
                out.write(self._construct_sentence_query(sent_num, bleu_list[i], features) + "\n")
                i += 1
