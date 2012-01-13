#!/bin/bash
echo "Saving data in ../../../t4t-data/twitter/, debug output"
python uktwaffic.py -t 'traffic OR accident OR tailback OR gridlock OR m25 OR standstill OR road OR street OR stuck OR car OR bus OR train' ../../../tweets.sqlite -v 10
