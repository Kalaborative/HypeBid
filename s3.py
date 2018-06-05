import boto3
from retrieveCreds import getCredentials


def uploadToS3(filename):
	user = getCredentials()
	session = boto3.Session(aws_access_key_id=user['access_key'], aws_secret_access_key=user['secret_key'], region_name='us-east-2')

	s3 = session.resource('s3')
	data = open('itemUploads/{}'.format(filename), 'rb')
	s3.Bucket('hypebid-upload').put_object(Key=filename, Body=data)
	url = 'https://s3.us-east-2.amazonaws.com/hypebid-upload/{}'.format(filename)
	return url