#!/bin/bash

#This program repeatedly steps forward through an elisp program (the first arg)
#Example usage:
#./run.sh elisp/factorial.el


fn=$1
tmp=/tmp/run_MEL_sh

#use the newest version of python
if which python3 >/dev/null; then
    p=python3
else
    p=python2
fi

#first just format the code nicely
$p python/MEL.py --nostep $fn 2>/dev/null | tee $tmp

#then repeatedly (waiting for user input) step forward through the program
while read line; do
    echo
    echo -e ----------------------------------------------
    echo
    $p python/MEL.py $tmp 2>/dev/null | tee "$tmp"2
    cp "$tmp"2 $tmp
done
