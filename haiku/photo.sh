#!/bin/bash

#fswebcam -r 1920x1080 -S 5 --jpeg 90 photo.jpg
#raspistill -n -drc high -mm matrix -md 3 -q 80 -o photo.jpg

raspistill --nopreview --exposure sports --timeout 1 -q 50 -o photo_raw.jpg
sudo convert photo_raw.jpg -resize 30% photo.jpg

exit 0
