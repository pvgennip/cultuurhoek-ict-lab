from haiku_text_classes import InputHandler, HaikuTextGenerator
from gpiozero import Button
from time import sleep
import subprocess
import requests

def read_text(data):
    reqMp3AudioUrl = requests.post("https://ttsmp3.com/makemp3.php",
                   data={'msg': data, 'lang': 'Ruben', 'source': 'ttsmp3'})
    mp3AudioUrl = reqMp3AudioUrl.json()['URL']
    ttsmp3req = requests.get(mp3AudioUrl)
    with open('haiku.mp3', 'wb') as f:
        f.write(ttsmp3req.content)
    os.system("mpg321 haiku.mp3")

def detect_objects(path):
    """Detects labels in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open('photo.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image()
    image.source.image_uri = path

    response = client.object_localization(image=image)
    objects = response.localized_object_annotations

    objectList = [translate_label(object_info.name).lower() for object_info in objects]
    return objectList

def detect_labels(path):
    """Detects labels in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open('photo.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.label_detection(image=image)
    objects = response.label_annotations

    labelList = [translate_label(object_info.description).lower() for object_info in objects]
    return labelList


def translate_label(label):
    from googletrans import Translator
    translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.nl',
    ])
    translation = translator.translate(label, dest='nl')
    return translation.text


def handle_object_list(object_list):
    handled_input = InputHandler(object_list)
    haiku_template = handled_input.pick_injected_template()
    haiku_generator = HaikuTextGenerator(handled_input.word_df, haiku_template, handled_input.category_dict)
    haiku = haiku_generator.compose_haiku()
    return haiku

import os 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/haiku/gvision-key.json"
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/happy/Downloads/service_account.json"
print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

pir = Button(2)

while True:
    if pir.is_pressed:
        print "taking photo..."
        subprocess.call("./photo.sh")
        print "analyzing..."
        list_of_text = detect_labels('photo.jpg')
        if (len(list_of_text) > 0):
            print "objects detected: "
            print ' '.join(list_of_text)
            haiku = handle_object_list(list_of_text)
            print "a new moment has been captured:"
            print ""
            print haiku
            print ""
            read_text(haiku)
            print "waiting 20 sec before checking motion again..."
            sleep(20)
        else:
            print "no objects detected, checking motion again..."
    else:
        print("No movement")
        sleep(1)

