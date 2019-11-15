def read_text(data):
    from gtts import gTTS    
    tts = gTTS(text=data, lang='nl')
    tts.save("good.mp3")
    os.system("mpg321 good.mp3")
    path = 'good.mp3'
    playsound(path)

def detect_labels(path):
    """Detects labels in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations
    print('Labels:')

    labelList = [translate_label(label.description) for label in labels]
    return ' '.join(labelList)


def translate_label(label):
    from googletrans import Translator
    translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.nl',
    ])
    translation = translator.translate(label, dest='nl')
    print(translation.text)
    return translation.text

import os 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/haiku/gvision-key.json"
#print(os.environ['GOOGLE_APPLICATION_CREDENTIALS']) 

read_text(detect_labels('photo.jpg'))

