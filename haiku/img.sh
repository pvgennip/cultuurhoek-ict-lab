curl -X POST \
-H "Authorization: Bearer "$(gcloud auth application-default 283fe349a7651abb8186fc10d63cbffb1cf29fbe) \
-H "Content-Type: application/json; charset=utf-8" \
https://vision.googleapis.com/v1/images:annotate -d "{
  'requests': [
    {
      'image': {
        'source': {
          'gcsImageUri': 'photo.jpg'
        }
      },
      'features': [
        {
          'maxResults': 5,
          'type': 'LABEL_DETECTION'
        },
      ]
    }
  ]
}"

