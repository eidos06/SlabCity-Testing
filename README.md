# SlabCity-Testing component

## Overview
This repo contains the testing component of SlabCity.

The main testing entry is ```testing/oracle.py```. It contains an Oracle class, which can test the equivalence of a candidate query and the ground truth query, by generating databases.


```synthesizerv2``` folder contains an old version of SlabCity synthesizer - it is no longer used anymore, but since the testing part replies on some of its analysis functionality, it is kept here.

Yuxuan Zhu (yxx404@illinois.edu) wrote this testing component, and please feel free to contact him if you have any specific questions.