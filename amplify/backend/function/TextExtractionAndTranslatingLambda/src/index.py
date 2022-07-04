import json
import os
import cv2
import numpy as np
from imutils.contours import sort_contours
import imutils
import boto3

import constants

def translation(translate_client, output_string, language):
  
  # Translation  
  translated_output = translate_client.translate_text(Text=output_string, 
            SourceLanguageCode="auto", TargetLanguageCode=language)        
  print(translated_output)
    
  translated_output_string = translated_output['TranslatedText']

  return translated_output_string
  
def filter_by_size(allBoundingBoxes):
  boundingBoxes = []
  for i in range(len(allBoundingBoxes)):
      x, y, w, h = allBoundingBoxes[i]
      if w > constants.WORD_BOUNDING_BOX_MIN_WIDTH and \
            constants.WORD_BOUNDING_BOX_MIN_HEIGHT < h < constants.WORD_BOUNDING_BOX_MAX_HEIGHT:
        boundingBoxes.append(allBoundingBoxes[i])

  return boundingBoxes

def sort_by_left_right_top_down(allBoundingBoxes):
  boundingBoxes = filter_by_size(allBoundingBoxes)

  line = 1
  by_line = []
  x, y, w, h = boundingBoxes[0]
  by_line.append((line, x, y, w, h))

  for i in range(1, len(boundingBoxes)):
      x, y, w, h = boundingBoxes[i]
      if boundingBoxes[i - 1][1] - constants.LINE_SPACE_THRESHOLD <= y <= boundingBoxes[i - 1][1] + constants.LINE_SPACE_THRESHOLD:
          by_line.append((line, x, y, w, h))
      else:
          line += 1
          by_line.append((line, x, y, w, h))

  contours_sorted = [(x, y, w, h) for line, x, y, w, h in sorted(by_line)]

  return contours_sorted

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
      if w * h > constants.CHAR_BOUNDING_BOX_MIN_AREA:
          height_arr.append(h)

  print('area_arr: ', area_arr)

  return get_lower_bound_from_array(height_arr)

def detectTextArea(file_path, s3, bucket, image_folder):
  # read image 
  file = s3.Object(bucket, file_path).get().get('Body').read()
  image = cv2.imdecode(np.asarray(bytearray(file)), cv2.IMREAD_COLOR)
  
  image = resize_with_aspect_ratio(image, width=constants.DEFAULT_IMAGE_RESIZE_WIDTH)
  image = cv2.pyrDown(image)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

  _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
  connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
  cv2.imwrite(f'/tmp/connected.jpg', connected)
  s3.meta.client.upload_file('/tmp/connected.jpg', bucket, image_folder + 'connected.jpg')

  contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  contours, bounding_boxes = sort_contours(contours, method='top-to-bottom')
  bounding_boxes = sort_by_left_right_top_down(bounding_boxes)

  textAreaPaths = []
  for idx in range(len(bounding_boxes)):
    x, y, w, h = bounding_boxes[idx]
    crop_img = image[y - 2:y + h + 2, x - 2:x + w + 2]
    path = f'/tmp/{idx}.jpg'

    try:
      cv2.imwrite(path, crop_img)
      s3.meta.client.upload_file(f'/tmp/{idx}.jpg', bucket, image_folder + f'{idx}.jpg')
      textAreaPaths.append(path)
    except:
      pass

    # draw text area bounding boxes
    cv2.rectangle(image, (x, y), (x + w - 1, y + h - 1), (0, 255, 0), 2)

  cv2.imwrite(f"/tmp/detected.jpg", image)

  return textAreaPaths

def detectAndClassifyCharsFromText(idx, path, s3, image_folder, sm):
  textArea = cv2.imread(path)
  gray = cv2.cvtColor(textArea, cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray, (5, 5), 0)
  edged = cv2.Canny(blurred, 30, 150)
  # some characters are not "edged" well: W, Z, Y. Dilating a bit after edging helps overall.
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
  edged = cv2.dilate(edged, kernel, iterations=1)
  cv2.imwrite(f'/tmp/{idx}-edged.jpg', edged)
  s3.meta.client.upload_file(f'/tmp/{idx}-edged.jpg', constants.CLIENTS_IMAGES_BUCKET, image_folder + f'{idx}-edged.jpg')

  cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
      cv2.rectangle(textArea, (int(x), int(y)), (int(x + w), int(y + h)), constants.RED_COLOR, 1)
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

      # uncomment for writing in s3 individual extracted chars images 32x32
      # cv2.imwrite(f"/tmp/{idx}-{x}-{y}-{w}-{h}.jpg", padded)
      # s3.meta.client.upload_file(f"/tmp/{idx}-{x}-{y}-{w}-{h}.jpg", constants.CLIENTS_IMAGES_BUCKET, image_folder + f"extracted_char/{idx}-{x}-{y}-{w}-{h}.jpg")

      # prepare the padded image for classification via our OCR model
      padded = padded.astype('float32') / 255.0
      padded = np.expand_dims(padded, axis=-1)

      # update our list of characters that will be OCR'd
      chars.append((padded, (x, y, w, h)))

  cv2.imwrite(f'/tmp/{idx}-chars_bounding_boxes.jpg', textArea)
  s3.meta.client.upload_file(f'/tmp/{idx}-chars_bounding_boxes.jpg', constants.CLIENTS_IMAGES_BUCKET, image_folder + f'{idx}-chars_bounding_boxes.jpg')

  boxes = [b[1] for b in chars]
  chars = np.array([c[0] for c in chars], dtype='float32')
  
  # OCR the characters using our model
  response = sm.invoke_endpoint(EndpointName=constants.ENDPOINT_NAME, 
              ContentType='application/json', 
              Body=json.dumps(chars.tolist()))

  result = json.loads(response['Body'].read())
  preds = result['predictions']
  print(f'path: {path}. preds: {preds}')

  extracted_word = ''
  for (pred, (x, y, w, h)) in zip(preds, boxes):
    i = np.argmax(pred)
    prob = pred[i]
    label = constants.LABEL_NAMES[i]
    print(f'label: {label}. probability: {prob}')
    extracted_word += label
    
  return extracted_word

def handler(event, context):
  print('received event body :')
  print(event['body'])

  try:
    # operation params
    obj_body = json.loads(event['body'])
    file_path = 'public/' + obj_body['filePath']
    operation = obj_body['operation']
    targetLanguage = obj_body['targetLanguage']
    text = obj_body['text']

    # aws services clients
    translate_client = boto3.client('translate')
    textract_client = boto3.client('textract')
    sm= boto3.client('runtime.sagemaker')
    s3 = boto3.resource('s3')
  
    # AWS Textract option
    if operation == 'AWSTextract':      
      # Process the file using the S3 object we just uploaded
      response = textract_client.detect_document_text(
        Document = {'S3Object': {'Bucket': constants.CLIENTS_IMAGES_BUCKET, 'Name': file_path}})
        
      # Get the text blocks
      blocks = response['Blocks']
      print(blocks)
            
      extracted_string = ''
      for block in blocks:
        if block['BlockType'] == 'LINE':
          extracted_string += block['Text'] + ' '    
      print(extracted_string)

      return constants.construct_handler_output(extracted_string)
     
    # My custom ocr  
    elif operation == 'MyOcr':
      image_folder = os.path.splitext(file_path)[0] + '/'
      
      textAreaPaths = detectTextArea(file_path, s3, constants.CLIENTS_IMAGES_BUCKET, image_folder)
      print(textAreaPaths)

      extracted_string = ''
      for idx, path in enumerate(textAreaPaths):
        print(path)
        try:
          extracted_word = detectAndClassifyCharsFromText(idx, path, s3, image_folder, sm)

          extracted_string += f'{extracted_word} '

          print('current extracted string: ', extracted_string)
        except Exception as e:
          print(str(e))
          pass

      extracted_string = extracted_string.upper()
      print('final output: ', extracted_string)

      return constants.construct_handler_output(extracted_string)

    # Translation
    elif operation == 'Translate':        
      translated_output_string = translation(translate_client, text, targetLanguage)
      print(translated_output_string)

      return constants.construct_handler_output(translated_output_string)
  
  except Exception as e:
    print(str(e))
    return constants.construct_handler_output(constants.DEFAULT_ERROR_MESSAGE)
