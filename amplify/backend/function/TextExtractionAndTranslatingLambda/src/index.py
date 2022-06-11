import json
import cv2
import boto3

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

  output_string = ''
  
  # AWS Textract option
  if ocr_option == 'Textract':
    print(bucket)
    print(file_path)
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
  elif ocr_option == 'MyCustomOcr1':
    # opencv + sagemaker model
    # In progress ...
    pass

  # Translation  
  translated_output = translate_client.translate_text(Text=output_string, 
            SourceLanguageCode="auto", TargetLanguageCode=language)        
  print(translated_output)
    
  translated_output_string = translated_output['TranslatedText']
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
