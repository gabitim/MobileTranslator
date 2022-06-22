import json
import os
import cv2
import numpy as np
from imutils.contours import sort_contours
import imutils
import boto3

def translation(translate_client, output_string, language):
  # Translation  
  # translated_output = translate_client.translate_text(Text=output_string, 
  #           SourceLanguageCode="auto", TargetLanguageCode=language)        
  # print(translated_output)
    
  # translated_output_string = translated_output['TranslatedText']

  # return translated_output_string
  return 'ResNet in progress...'

def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
  (h, w) = image.shape[:2]

  if width is None and height is None:
      return image
  if width is None:
      r = height / float(h)
      dim = (int(w * r), height)
  else:
      r = width / float(w)
      dim = (width, int(h * r))

  return cv2.resize(image, dim, interpolation=inter)

def get_lower_bound_from_array(array):
  # https://builtin.com/data-science/how-to-find-outliers-with-iqr

  array.sort()
  print('height array: ', array)
  np_arr = np.array(array)

  q1, q3 = np.percentile(np_arr, [25, 75])
  print(f'q1: {q1}, q3: {q3}')

  IQR = q3 - q1

  lower_bound = (q1 - 1.5 * IQR) - 2
  print(f'lower_bound: {lower_bound}')

  return lower_bound

def get_height_lower_bound(cnts):
  height_arr = []
  area_arr = []

  for c in cnts:
      # compute the bounding box of the contour
      (x, y, w, h) = cv2.boundingRect(c)
      area_arr.append(w * h)
      if w * h > 100:
          height_arr.append(h)

  print('area_arr: ', area_arr)

  return get_lower_bound_from_array(height_arr)

def handler(event, context):
  print('received event body :')
  print(event['body'])
  
  obj_body = json.loads(event['body'])
  file_path = 'public/' + obj_body['filePath']
  ocr_option = obj_body['ocrOption']
  language = obj_body['language']
  
  bucket = "clients-images161213-dev"

  translate_client = boto3.client('translate')
  textract_client = boto3.client('textract')
  sm= boto3.client('runtime.sagemaker')
  s3 = boto3.resource('s3')

  print(bucket)
  print(file_path)
  output_string = ''
  
  # AWS Textract option
  if ocr_option == 'Textract':
   
    # Process the file using the S3 object we just uploaded
    response = textract_client.detect_document_text(
      Document = {'S3Object': {'Bucket': bucket, 'Name': file_path}})
      
    # Get the text blocks
    blocks = response['Blocks']
    print(blocks)
          
    for block in blocks:
      if block['BlockType'] == 'LINE':
        output_string += block['Text'] + ' '    
    print(output_string)
    
  elif ocr_option == 'ResNet':
    red_color = (0, 0, 255)
    image_folder = os.path.splitext(file_path)[0] + '/'
    
    # read image 
    file = s3.Object(bucket, file_path).get().get('Body').read()
    image = cv2.imdecode(np.asarray(bytearray(file)), cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
    dilate_edged = cv2.dilate(edged, kernel, iterations=1)

    cv2.imwrite("/tmp/dilate_edged.jpg", dilate_edged)
    s3.meta.client.upload_file("/tmp/dilate_edged.jpg", bucket, image_folder + 'dilate_edged.jpg')

    cnts = cv2.findContours(dilate_edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sort_contours(cnts, method="left-to-right")[0]
    chars = []

    h_lower_bound = get_height_lower_bound(cnts)

    for c in cnts:
      # compute the bounding box of the contour
      (x, y, w, h) = cv2.boundingRect(c)

      # filter out bounding boxes
      if h_lower_bound <= h:
        # extract the character and threshold it to make the character
        # appear as *white* (foreground) on a *black* background, then
        # grab the width and height of the thresholded image
        cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), red_color, 1)
        roi = gray[y:y + h, x:x + w]
        thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        (tH, tW) = thresh.shape

        # if the width is greater than the height, resize along the
        # width dimension
        if tW > tH:
            thresh = imutils.resize(thresh, width=32)
        # otherwise, resize along the height
        else:
            thresh = imutils.resize(thresh, height=32)

        (tH, tW) = thresh.shape
        dX = int(max(0, 32 - tW) / 2.0)
        dY = int(max(0, 32 - tH) / 2.0)
        # pad the image and force 32x32 dimensions
        padded = cv2.copyMakeBorder(thresh, top=dY, bottom=dY,
                                    left=dX, right=dX, borderType=cv2.BORDER_CONSTANT,
                                    value=(0, 0, 0))
        padded = cv2.resize(padded, (32, 32))

        cv2.imwrite(f"/tmp/{x}-{y}-{w}-{h}.jpg", padded)
        s3.meta.client.upload_file(f"/tmp/{x}-{y}-{w}-{h}.jpg", bucket, image_folder + f"extracted_char/{x}-{y}-{w}-{h}.jpg")

        # prepare the padded image for classification via our
        # handwriting OCR model
        padded = padded.astype("float32") / 255.0
        padded = np.expand_dims(padded, axis=-1)

        # update our list of characters that will be OCR'd
        chars.append((padded, (x, y, w, h)))
  
    cv2.imwrite("/tmp/char_bounding_boxes.jpg", image)
    s3.meta.client.upload_file("/tmp/char_bounding_boxes.jpg", bucket, image_folder + 'char_bounding_boxes.jpg')

    boxes = [b[1] for b in chars]
    chars = np.array([c[0] for c in chars], dtype="float32")
    
    # OCR the characters using our model
    response = sm.invoke_endpoint(EndpointName=os.environ['RESNET_ENDPOINT_NAME'], 
                ContentType='application/json', 
                Body=json.dumps(chars.tolist()))

    result = json.loads(response['Body'].read())
    print(result)
    preds = result['predictions']
    print(preds)

    # define the list of label names
    labelNames = "0123456789"
    labelNames += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    labelNames = [l for l in labelNames]

    for (pred, (x, y, w, h)) in zip(preds, boxes):
      i = np.argmax(pred)
      prob = pred[i]
      label = labelNames[i]
      output_string += label

    print('output_string', output_string)

  # Translation  
  translated_output_string = translation(translate_client, 
              output_string, language)
  print(translated_output_string)
    
  return {
      'statusCode': 200,
      'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps(translated_output_string)
  }
