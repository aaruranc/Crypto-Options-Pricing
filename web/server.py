from flask import Flask, json, redirect, render_template, request, session
from flask_cors import CORS, cross_origin
from pathlib import Path
import os
import time
import pandas as pd
import json
from pricing.standardize import validate
from pricing.computations import search_and_compute
from pricing.export import price_JSON, query_JSON


app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.debug = True


@app.route('/', methods=['POST', 'GET'])
@cross_origin(origin='*', headers=['access-control-allow-origin','Content-Type'])
def index():

	if request.method == 'GET':
	    start_time = str(int(time.time()))
	    session['location'] = 'data' + '/' + start_time
	    return render_template('index.html')

	if request.method == 'POST':
		asset_name = request.form['asset']
		session['asset_name'] = asset_name

		# Need to handle the case when no file is uploaded

		file = request.files['upload']
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

		flags = validate(user_parameters)

		if not flags:
			return render_template('/analysis.html')
		else:
			print(flags)
			return render_template('index.html', flags=flags)


@app.route('/prices.html', methods=['GET', 'POST'])
def prices():
	asset_time_series = price_JSON(session['source'])
	return asset_time_series


@app.route('/update.html', methods=['GET', 'POST'])
@cross_origin(origin='*', headers=['access-control-allow-origin','Content-Type'])
def update():

	if request.method == 'GET':
		query = request.args.to_dict()
		query.update({'current_directory': session['location'], 'source': session['source']})
		print(query)
		search_and_compute(query)
		print('MADE IT')
		query_data = query_JSON(query)
		print('MADE IT 2')
		return query_data

	else: 
		return render_template('/')

if __name__ == '__main__':
	app.run()
