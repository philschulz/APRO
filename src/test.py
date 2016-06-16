import sys
from Moses_Wrapper import Moses_Wrapper

def main():
    fields = sys.argv[1:]
    print fields
    wrapper = Moses_Wrapper(fields[0])

    wrapper.merge_k_best_lists(fields[1], fields[2], "bla.txt")

if __name__ == "__main__":
    main()