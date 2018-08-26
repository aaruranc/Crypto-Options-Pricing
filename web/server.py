from flask import Flask, json, redirect, render_template, request, session
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import time
import pandas as pd
import json
from pricing.standardize import validate
from pricing.computations import search_and_compute
from pricing.export import update_query, price_JSON, query_JSON


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True


@app.route('/', methods=['POST', 'GET'])
# @cross_origin(origin='*', headers=['access-control-allow-origin','Content-Type'])
def index():

	if request.method == 'GET':
	    print('executed')
	    start_time = str(int(time.time()))
	    session['location'] = 'data' + '/' + start_time
	    return render_template('index.html')

	if request.method == 'POST':
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

		dest = session['location'] + '/' + file.filename
		session['source'] = dest
		
		if not os.path.isdir(session['location']):
	   		os.mkdir(session['location'])
		
		file.save(dest)
		file.close()
		
		user_parameters = {'start': request.form['start'], 
							'end': request.form['end'], 
							'trading_days': request.form['trading_days'], 
							'source': session['source']}

		session['trading_days'] = user_parameters['trading_days']
		flags = validate(user_parameters)

		if not flags:
			return render_template('/analysis.html')
		else:
			return render_template('index.html', flags=flags)

@app.route('/update.html', methods=['GET', 'POST'])
def update():

	if request.method == 'GET':
		
		# Check if there is enough datapoints to conduct analysis

		query = update_query(request.args.to_dict(), session)
		search_and_compute(query)
		query_data = query_JSON(query)
		return query_data

	else: 
		return render_template('/')

if __name__ == '__main__':
	app.run()
