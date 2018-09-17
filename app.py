from flask import Flask, redirect, render_template, request, session, url_for
import os
import time
import pandas as pd
from pricing.standardize import validate
from pricing.computations import search_and_compute
from pricing.export import update_query, price_JSON, query_JSON
import boto3
# from pricing.config import S3_BUCKET, S3_KEY, S3_SECRET

s3_resource = boto3.resource(
   "s3",
   aws_access_key_id=process.env.S3_KEY,
   aws_secret_access_key=process.env.S3_SECRET
)

app = Flask(__name__)
app.secret_key = b'\tR\x81q\x91qP\x13\xb6\xfe\x1f}4\xb50Z\x04>\x8f\xb3Fw\x9d\x8f'

@app.route('/files', methods=['POST', 'GET'])
def files():
	
	s3_resource = boto3.resource('s3')
	my_bucket = s3_resource.Bucket(process.env.S3_BUCKET)
	summaries = my_bucket.objects.all()
	return render_template('test.html', my_bucket=my_bucket, files=summaries)


@app.route('/', methods=['POST', 'GET'])
def index():

	if request.method == 'GET':
	    return render_template('index.html')

	if request.method == 'POST':
		start_time = str(int(time.time()))
		session['start_time'] = start_time
            
		if not request.form['asset'] or not request.form['start'] or not request.form['end']:
			flags = ['Incomplete form data']
			return render_template('index.html', flags=flags)

		asset_name = request.form['asset']
		session['asset_name'] = asset_name

		if not request.files:
			flags = ['No file uploaded']
			return render_template('index.html', flags=flags)

		file = request.files['upload']
		extension = file.filename.rsplit('.')[-1]

		if extension != 'csv':
			flags = ['Incorrect file type']
			return render_template('index.html', flags=flags)

		S3_info = {'bucket': process.env.S3_BUCKET, 'key': process.env.S3_KEY, 'secret': process.env.S3_SECRET}
		session['S3_info'] = S3_info
		session['source'] = session['start_time'] + '-' + session['asset_name']

		df = pd.read_csv(file)

		user_parameters = {'start': request.form['start'], 
							'end': request.form['end'], 
							'trading_days': request.form['trading_days'], 
							'S3_info': session['S3_info'],
							'source': session['source']}
		session['trading_days'] = user_parameters['trading_days']
		flags = validate(user_parameters, df)
	
		if not flags:
			name = [asset_name]
			session['file_length'] = len(df)
			return render_template('/analysis.html', name=name)
		else:
			return render_template('index.html', flags=flags)

@app.route('/update.html', methods=['GET'])
def update():

	query = update_query(request.args.to_dict(), session)	

	if session['file_length'] < 2 * (int(query['option_length']) + 1):
		return 'bad_request'
	else:
		search_and_compute(query)
		query_data = query_JSON(query)
		return query_data


if __name__ == '__main__':
	app.run()
