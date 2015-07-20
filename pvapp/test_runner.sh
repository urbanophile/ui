#!/bin/bash
fswatch -e 'pyc' . |
while read;
    do python test/test_load_save.py;
    echo "++++++++++++++++++++++"
    echo "Finished running tests"
    echo "++++++++++++++++++++++"
done

