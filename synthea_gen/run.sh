#!/bin/bash
#
# Runs the Synthea tool, with some options specified.
#
# See synthea.properties for additional options.

#rm -rf output
rand_seed=`shuf --random-source='/dev/urandom' -n 1 -i 2000-2000000;`
time java -jar synthea-with-dependencies.jar -c synthea.properties \
    -s $rand_seed \
    -a 40-80  \  # patient population aged 40-80
    'New York'
