#!/bin/bash

python2 pyrdfa3/scripts/localRDFa.py -s -b https://irnok.net/pages/standard-09.03.01-bachelor-2016.html ./standard-09.03.01-bachelor-2016.html > standard-09.03.01-bachelor-2016.ttl
python2 pyrdfa3/scripts/localRDFa.py -s -b http://irnok.net/pages/Work-Program-AIIS-Academic-Bachelor.html ./Work-Program-AIIS-Academic-Bachelor.html > Work-Program-AIIS-Academic-Bachelor.ttl
