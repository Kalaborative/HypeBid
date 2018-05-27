import boto3
from credentials import ACCESS_KEY, SECRET_KEY

s3 = boto3.resource('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

def uploadToS3(filename):
	data = open('itemUploads/{}'.format(filename), 'rb')
	s3.Bucket('hypebid-uploads').put_object(Key=filename, Body=data)
	url = 'https://s3.us-east-2.amazonaws.com/hypebid-uploads/{}'.format(filename)
	return url
