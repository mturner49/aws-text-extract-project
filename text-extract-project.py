import boto3
import botocore
import logging
import re
import os, os.path
import glob
import datefinder
from datetime import date
from botocore.exceptions import ClientError
from pdf2image import convert_from_path
from os import path


def convert_to_jpg(file_name):
    images = convert_from_path(file_name)

    for i in range(len(images)):
        images[i].save(file_name + 'page' + str(i) + '.jpg', 'JPEG')


def find_jpgs(file_name):
    jpgs = []
    for file in glob.glob(file_name + '*' + '.jpg'):
        jpgs.append(file)
    return jpgs


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    print('File uploaded to s3 ....')


def textract(bucket, document):
    text = ''

    # Amazon Textract client
    textract = boto3.client('textract')

    # Call Amazon Textract
    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': document
            }
        })

    # Print detected text
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text += '\033[94m' +  item["Text"] + '\033[0m \n'

    return text


def get_dates(text):
    current_date = date.today()
    matches = datefinder.find_dates(text)
    for match in matches:
        if match.year == current_date.year:
            print(match)
    


def remove_words(text):
    clean_text = ''
    keywords = ['hw', 'homework', 'due', 'exam', 'test', 'quiz', 'final']
    lines = text.lower().split('\n')

    for line in lines:
        if any(word in line for word in keywords):
            print(line)

if __name__ == '__main__':



    s3BucketName = "text-extract-project-mturner0627"
    documentName = "Course Syllabus_MSA_8050_Scalable-Data-Analytics.pdf"
    s3 = boto3.resource('s3')

    output = ''

    # check if pdfs have already been converted to jpgs
    # to avoid duplicate files
    if os.path.isfile(documentName + '*' + '.jpg') == False:
        convert_to_jpg(documentName)

    imgs = find_jpgs(documentName)

    for img in imgs:
        output += textract(s3BucketName, img)

        # TODO: check whether images exist in s3, if not, upload files
        # before running textract method
        # try:
        #     s3.Object(s3BucketName, img).load()
        # except botocore.exceptions.ClientError as e:
        #     if e.response['Error']['Code'] == '404':
        #         upload_file(img, s3BucketName)
        #         output += textract(s3BucketName, img)
        #     else:
        #         raise
        # else:
        #     output += textract(s3BucketName, img)

    remove_words(output)



    
    


