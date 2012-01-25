#!/bin/bash
echo "Saving data in /srv/t4t/tfl, debug output"
python tfltrafficfeedreader.py -d /srv/t4t/tfl/ -v 10
