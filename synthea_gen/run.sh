#!/bin/bash

rm -rf output
rand_seed=`shuf --random-source='/dev/urandom' -n 1 -i 2000-2000000;`
time java -jar synthea-with-dependencies.jar -c synthea.properties \
    -s $rand_seed \
    -a 40-80  \
    California "Los Angeles"
