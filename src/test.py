import sys
from Moses_Wrapper import Moses_Wrapper

fields = sys.argv[1:]
print fields
wrapper = Moses_Wrapper(fields[0])

wrapper.merge_k_best_lists(fields[1], fields[2])