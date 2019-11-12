#!/bin/bash

#fswebcam -r 1920x1080 -S 5 --jpeg 90 photo.jpg

raspistill --nopreview --exposure sports --timeout 1 -q 50 -o photo_raw.jpg
convert photo_raw.jpg -resize 30% photo.jpg 
# auto levels
#convert photo.jpg -colorspace Lab -channel 0 -auto-level +channel -colorspace sRGB photo.jpg

exit 0