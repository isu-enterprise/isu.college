#!/bin/bash

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for f in *.xls
do
    # echo $f
    echo libreoffice --headless --convert-to xlsx $f
    libreoffice --headless --convert-to xlsx $f
done
IFS=$SAVEIFS
