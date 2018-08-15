from flask import Flask, json, redirect, render_template, request, session
from werkzeug.utils import secure_filename
from pathlib import Path
import jinja2
import os
import time
import pandas as pd 
# from pricing.standardize import convert_datetime, error_labels, validate
# from pricing.computations import search_and_compute
from pricing.export import price_JSON, query_JSON


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True


@app.route('/', methods=['POST', 'GET'])
def index():

	if request.method == 'GET':
	    start_time = str(int(time.time()))
	    session['location'] = 'data' + '/' + start_time
	    return render_template('index.html')

	if request.method == 'POST':
		file = request.files['upload']
		dest = session['location'] + '/' + file.filename
		session['file'] = dest
		
		if not os.path.isdir(session['location']):
	   		os.mkdir(session['location'])
		
		file.save(dest)
		file.close()
		user_df = pd.read_csv(session['file'])

		error = []
		# error = validate(user_df)

		if not error:
			input_data = price_JSON(session['file'])
			return render_template('/analysis.html', input_data=input_data)
		else:
			flags = error_labels(error)
			return render_template('index.html', flags=flags)

@app.route('/analysis.html', methods=['POST', 'GET'])
def analysis():
	
	if request.method == 'POST':	
		
		query = {'trading_strategy': request.form['trading_strategy'], 
				'option_length': request.form['option_length'],
				'strike': request.form['strike'],
				'current_directory': session['location'], 
				'source': session['file']
				}
		
		search_and_compute(query)
		query_data = query_JSON(query)
		return render_template('/analysis.html', query_data=query_data)
	
	elif request.method == 'GET':
		return render_template('/')


if __name__ == '__main__':
	app.run()
