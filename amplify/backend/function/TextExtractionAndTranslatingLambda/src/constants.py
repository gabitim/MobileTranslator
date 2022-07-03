import json
import os

LINE_SPACE_THRESHOLD = 10
WORD_BOUNDING_BOX_MIN_WIDTH = 8
WORD_BOUNDING_BOX_MIN_HEIGHT = 20
WORD_BOUNDING_BOX_MAX_HEIGHT = 100
CHAR_BOUNDING_BOX_MIN_AREA = 100

DEFAULT_IMAGE_RESIZE_WIDTH = 1300

RED_COLOR = (0, 0, 255)

 # define the list of label names. 47 classes. C, I, J, K, L, M, O, P, S, U,V, W, X, Y and Z are merged
LABEL_NAMES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LABEL_NAMES += "abdefghnqrt"
LABEL_NAMES += "0123456789"
LABEL_NAMES = [l for l in LABEL_NAMES]

ENDPOINT_NAME = os.environ['OCR_ENDPOINT_NAME']
CLIENTS_IMAGES_BUCKET = 'clients-images161213-dev'

DEFAULT_ERROR_MESSAGE = ' An error occurred while processing your request. \
  This might be an issue on our side. Please retry, and if the issue persists contact us.'

def construct_handler_output(message):
  return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(message)
    }

