import boto3
from os import environ

environ['AWS_SHARED_CREDENTIALS_FILE'] = "~/HypeBid/.aws/credentials"
environ['AWS_CONFIG_FILE'] = "~/HypeBid/.aws/config"

s3 = boto3.resource('s3')

def uploadToS3(filename):
	data = open('itemUploads/{}'.format(filename), 'rb')
	s3.Bucket('hypebid-uploads').put_object(Key=filename, Body=data)
	url = 'https://s3.us-east-2.amazonaws.com/hypebid-uploads/{}'.format(filename)
	return url
