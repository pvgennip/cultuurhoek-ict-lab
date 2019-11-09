#!/bin/bash

#fswebcam -r 1920x1080 -S 5 --jpeg 90 photo.jpg

raspistill -n -drc high -mm matrix -md 3 -q 80 -o photo.jpg

exit 0