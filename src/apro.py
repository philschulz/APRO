'''
Created on May 26, 2016

@author: Philip Schulz
'''

import argparse, os
from SVM_Query_Constructor import SVM_Query_Constructor
from Moses_Wrapper import Moses_Wrapper
from LibSVM_Wrapper import LibSVM_Wrapper
from shutil import copyfile
from datetime import datetime

k_best_name="_best_list"
query_name="query_list"
weight_name="weights"
acc_k_best_name="accumluated_k_best_list"

def main():
    
    global k_best_name
    global query_name
    
    command_line_parser = argparse.ArgumentParser("BLa")
    
    command_line_parser.add_argument("--moses", help="Path into the mosesdecoder. The moses bin diretory should be a child of this path.", required=True)
    command_line_parser.add_argument("--moses-ini", help="Path to the moses ini that shall be used to produce the k-best list.", required=True)
    command_line_parser.add_argument("-s", "--dev-source", help="Path to the source side of the dev data set.", required=True)
    command_line_parser.add_argument("-t", "--dev-target", help="Path to the target side of the dev data set.", required=True)
    command_line_parser.add_argument("--rank-SVM", help="Path to the RankSVM directory", required=True)
    command_line_parser.add_argument("-k", help=("The size of the k-best list produced at each iteration. (Note that the actual k-best lists will"
                                     "usually be longer because they are merged across iterations. The k-best list is reset after the 10th iteration. "
                                     "Changing this parameter from its default value of 500 is strongly discouraged. Changes of this "
                                     "parameter should always be reported, especially if subsequent significance testing is performed."), type=int, default=500)
    command_line_parser.add_argument("--k-best-list", help="Path to a already computed k-best-list. This option is only here for development purposes.")
    command_line_parser.add_argument("--threads", help="Set number of threads to use during decoding. There is no support for LIBSVM multithreading at the moment.", type=int, default=1)
    command_line_parser.add_argument("-C", help="Set the regularization strength for the L2-regulariser of RankSVM. The set value will be divided by the number "
                                     "of candidates in each k-best list. The value of this parameter is applied to the hinge loss objective. Thus, higher values lead "
                                     "to less regularization. Changing this parameter from its default value of 0.01 is strongly discouraged. Changes of this "
                                     "parameter should always be reported, especially if subsequent significance testing is performed.", type=float, default=0.01)
    command_line_parser.add_argument("-i","--iterations", help="Set the maximum number of tuning iterations. Tuning is stopped automatically whenever the candidate k-best list "
                                     "does not change across consecutive optimisation runs. Changing this parameter from its default value of 30 is strongly discouraged. Changes of this "
                                     "parameter should always be reported, especially if subsequent significance testing is performed.", type=int, default=30)
    
    args = vars(command_line_parser.parse_args())
    
    moses = args["moses"]
    moses_ini = args["moses_ini"]
    k = args["k"]
    k_best_name = str(k) + k_best_name
    k_best = args["k_best_list"]
    source = args["dev_source"]
    refs = args["dev_target"]
    threads = args["threads"]
    rankSVM = args["rank_SVM"]
    regularisation_strength = args["C"]
    iterations = args["iterations"]
    
    moses_wrapper = Moses_Wrapper(moses)
    query_constructor = SVM_Query_Constructor(moses_ini)
    libsvm_wrapper = LibSVM_Wrapper(rankSVM)

    #TODO plug iterations in here
    for i in xrange(1):
        print "Starting APRO iteration {0} at {1}\n".format(str(i + 1), datetime.now())

        suffix = "." + str(i + 1)
        current_k_best = k_best_name + suffix
        #moses_wrapper.create_k_best_list(moses_ini, source, current_k_best, k, threads=threads)
        if os.path.isfile(acc_k_best_name):
            k_best_size, changed = moses_wrapper.merge_k_best_lists(acc_k_best_name, current_k_best, acc_k_best_name)
            if not changed:
                print 'Tuning stopped early after iteration {09 because accumulated k_best_list did not change.\n'.format(i)
        else:
            k_best_size = moses_wrapper.compute_k_best_length(current_k_best)
            copyfile(current_k_best, acc_k_best_name)

        bleu_list = moses_wrapper.compute_sentence_bleu(acc_k_best_name, refs)
        query_constructor.write_query_file(bleu_list, acc_k_best_name, query_name + suffix)
        libsvm_wrapper.optimise(query_name, str(regularisation_strength / k_best_size), weight_name)
        query_constructor.create_moses_ini(weight_name)

        print "Finished APRO iteration {0} at {1}\n".format(str(i + 1), datetime.now())

        if (i == 9):
            print 'Removing accumulated k-best list after iteration 10\n'
            os.remove(acc_k_best_name)
    
if __name__ == '__main__':
    main()
    
