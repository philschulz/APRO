'''
Created on May 27, 2016

@author: Philip Schulz
'''

import sys, os
from subprocess import Popen, PIPE

candidate_txt = "k_best_candidates.txt"
ref_txt = "k_best_references.txt"
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
        weights = list()
        
        with open(moses_ini) as ini:
            for line in ini:
                if "[weight]" in line:
                    break;
            
            for line in ini:
                mapping = line.split("=")
                if len(mapping) > 0 and not word_penalty in mapping[0]:
                    key = mapping[0]
                    current_weights = [item for item in mapping[1].strip(" \n").split(" ")]
                    weights += current_weights
                    value = range(self.num_features, self.num_features + len(current_weights))
                    self.num_features = self.num_features + len(current_weights)
                    self.feature_map[key] = value
                
    
        return weights
        
    def _construct_sentence_query(self, qid, bleu, features_string):
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
    
    def write_query_file(self, moses_wrapper, k_best_list, references, name="query_list"):
        bleu_list = self.compute_sentence_bleu(moses_wrapper, k_best_list, references)
        
        i = 0
        sys.stderr.write("Creating query list")
        with open(k_best_list) as k_best, open(name, "w") as out:
            for line in k_best:
                fields = line.split(" ||| ")
                sent_num = fields[0].strip()
                features = fields[2].strip()
                out.write(self._construct_sentence_query(sent_num, bleu_list[i], features) + "\n")
                i += 1
                
    
    def compute_sentence_bleu(self, moses_wrapper, k_best_list,references):
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

        bleu = moses_wrapper.score_sentence_Bleu(candidate_txt, ref_txt)
        bleu_list = bleu.split("\n")
            
        return bleu_list
    
    def _extract_weights(self, model_file):
        weights = list()
        with open(model_file) as model:
            for line in model:
                if _is_numeric(line):
                    weights.append(line.strip())
                    
        return weights
                    
    def create_moses_ini(self, model_file, file_name="moses.ini"):
        weights = self._extract_weights(model_file)
        features = self.feature_map.keys()
        
        with open(self.moses_ini) as ini, open(file_name, "w") as out:
            for line in ini:
                out.write(line)
                if "[weight]" in line:
                    out.write(word_penalty + "= 1\n")
                    break;
                    
            for line in ini:
                print self.feature_map
                print line
                for feature in features:
                    if line.startswith(feature):
                        values = [str(weights[idx]) for idx in self.feature_map[feature]]
                        print values
                        out.write(feature + "= " + " ".join(values) + "\n")
    