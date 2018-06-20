import boto3
from os import remove
from retrieveCreds import getCredentials


def uploadToS3(filename):
	user = getCredentials()
	session = boto3.Session(aws_access_key_id=user['access_key'], aws_secret_access_key=user['secret_key'], region_name='us-east-2')

	s3 = session.resource('s3')
	with open('itemUploads/{}'.format(filename), 'rb') as data:
		s3.Bucket('hypebid-upload').put_object(Key=filename, Body=data)
		url = 'https://s3.us-east-2.amazonaws.com/hypebid-upload/{}'.format(filename)
	remove("itemUploads/{}".format(filename))
	return url