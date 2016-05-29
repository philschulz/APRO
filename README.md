# APRO
Python implementation of APRO ([Dreyer and Dong, 2015](http://www.aclweb.org/anthology/N15-1106)).

This is a program for tuning the weights of a log-linear machine translation decoder. If you are using this
program, please provide a link to this repository in your report and cite the above paper.

At the moment, it can only be used with [Moses](http://www.statmt.org/moses/). Also, it only supports sentence-level BLEU
scoring function.

## Why APRO?

APRO has a couple of important advantages over other SMT tuners. First and foremost, the weights it returns are
determined by the input, i.e. by the parameters settings, the initial decoder weights used to generate the first
k-best list, the number k of candidate translations in that list, the reference translations and the scoring function used.
Also, because it uses LibLinear, APRO is comparatively fast (at least it' s faster than MERT -- 
I have not yet compared it to any other tuners). For the same reason, APRO can handle massive features sets, enabling
research in non-neural feature-rich machine translation.

The advantages that result from APROs determinism are the following:
* Only one tuning run is needed. Translation results do not need to be averaged over multiple runs. This allows for
faster experimentation where tuning is usually a bottle neck.
* Changes that you make to your SMT system are directly reflected in the BLEU score. In my own experience with MERT, changes
in BLEU of up to 1 point are essentially random outcomes due to MERTs search procedure. APRO makes experimentation easier
since changes in BLEU are now only due to changes in the system.
* In case you are testing for statistical significance, your test procedure is invalidated if your give your data different
treatments. For SMT this means, that if your baseline system is tuned in a different way that the system you experiment with,
any statistical significance test you do is essentially meaningless (read: the test is not defined for such a situation!). 
This is clearly the case when your tuner is
non-deterministic. As far as I know, APRO is currently the only deterministic tuner. IMPORTANT: There are so many conceptual 
problems with significance tests that I would actually discourage people from using them. However,
if you have to use those tests, please use APRO for tuning to at least reduce the influence that the tuner has on your test.

## Changing Parameters

APROs default parameters should ideally not be changed to ensure comparability (recall that changing the parameters does
affect the weights output by APRO). If you do change the parameters, you should in any case report this and justify your
decision. The initial weights of newly introduced features are tricky. While for the standard Moses features APRO simply
used the initial features provided by Moses, the initial weights of custom-made features have to be set by hand. I suggest
using an initial value of 0 for new features. Notice that the value 0 could in principle be replaced by any constant C,
but I do believe that it is crucial that there be a consensus on that value. Most importantly, it needs to be the same 
constant C for *ALL* newly introduced features. 

## Required Libraries

The implementation is largely based on RankSVM. You will need to install this extension of LibLinear in order
to use APRO. The most current release can be found [here](https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/#large_scale_ranksvm).

## TODO

1. Include functionality for mutliple reference files
2. Make APRO available for other decoders
3. Allow for scoring functions other than sentence-level BLEU
