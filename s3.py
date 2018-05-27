import boto3
from credentials import access_key, secret_key, region
from os import environ


def uploadToS3(filename):
	print(environ['AWS_ACCESS_KEY_ID'])
	print(environ['AWS_SECRET_ACCESS_KEY'])
	session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

	s3 = session.resource('s3')
	data = open('itemUploads/{}'.format(filename), 'rb')
	s3.Bucket('hypebid-uploads').put_object(Key=filename, Body=data)
	url = 'https://s3.us-east-2.amazonaws.com/hypebid-uploads/{}'.format(filename)
	return url
