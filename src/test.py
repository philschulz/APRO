import sys
from Moses_Wrapper import Moses_Wrapper

wrapper = Moses_Wrapper()
files = sys.argv[1:]

wrapper.merge_k_best_lists(files[0], files[1])