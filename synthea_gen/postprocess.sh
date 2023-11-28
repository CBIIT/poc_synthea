#!/bin/bash

for F in `\ls output/fhir/*.json`
do
#    egrep -li -e 162573006 -e 254637007 -e 424132000 $F > /dev/null
    egrep -li -e 254837009 -e HER2 $F > /dev/null
    if [ $? -eq 0 ]
    then
        ls -lah $F
        cp $F selected
    fi
done
