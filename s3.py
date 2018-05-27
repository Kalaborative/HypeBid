import boto3
from credentials import access_key, secret_key, region

def uploadToS3(filename):
	sts = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
	res = sts.get_session_token()
	temp_access = res['Credentials']['AccessKeyId']
	temp_key = res['Credentials']['SecretAccessKey']
	temp_token = res['Credentials']["SessionToken"]
	session = boto3.Session(aws_access_key_id=temp_access, aws_secret_access_key=temp_key, region_name=region, aws_session_token=temp_token)

	s3 = session.resource('s3')
	data = open('itemUploads/{}'.format(filename), 'rb')
	s3.Bucket('hypebid-uploads').put_object(Key=filename, Body=data)
	url = 'https://s3.us-east-2.amazonaws.com/hypebid-uploads/{}'.format(filename)
	return url
