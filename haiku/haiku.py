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

def detect_labels(path):
    """Detects labels in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open('photo.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.object_localization(image=image)
    objects = response.localized_object_annotations

    print('Objects:')

    labelList = [translate_label(object_info.name).lower() for object_info in objects]
    return labelList


def translate_label(label):
    from googletrans import Translator
    translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.nl',
    ])
    translation = translator.translate(label, dest='nl')
    print(translation.text)
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
                list_of_objects = detect_labels('photo.jpg')
                haiku = handle_object_list(list_of_objects)
                print haiku
                read_text(haiku)
        else:
                print("No movement")
        sleep(1)



