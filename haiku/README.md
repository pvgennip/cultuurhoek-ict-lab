# Haiku generator 

## This Haiku generator generates a haiku from objects in a photo.

It works as follows:

1. Wait for PIR sensor movement (on GPIO 2)
2. Take a photo
3. Send photo to Google Vision API
4. Get objects in English text
5. Translate text to Dutch
6. Search on-line Speadsheet for object word
7. Define Haiku template and season
8. Fill in other matching words in Haiku template
9. Pass created Haiku to Google text to speech API
10. Downlaod and play spoken Haiku


# Installation

Requirements: 

* Python
* Google API account
* Image Magick

## Image Magick
```sudo apt-get install imagemagick```


## Save GOOGLE API key

Add API key to file ```gvision-key.json```

## Additional Python libraries 

* gpio: ```pip install gpiozero```
* pandas: ```sudo apt-get install python-pandas```
* Google: 
 * ```pip install google-cloud-vision```
 * ```pip install google-cloud-translate```

 # Run
```cd haiku```
```python haiku.py```

## Check log at
```tail -f log/rclocal.log```