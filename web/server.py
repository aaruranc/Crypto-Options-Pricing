from flask import Flask, redirect, request, render_template, session
import os
import time
# from pricing.module_1 import module_1_function
from pricing.module_2 import search_and_compute
from pricing.module_3 import price_JSON
from pricing.module_3 import query_to_JSON

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():

	# Check if first post
    # Create Session Variables
    session['wraparound'] = False
    # Handle csv 
    # Check if csv is valid (route to /invalid and throw error if not)
    	# 'Date' and 'Price' columns are labeled
    	# Start and End Dates Match
    	# Date format works
    	# Longer than 2 weeks
    	# Price is just numbers 
    	# Nonnegative price data
    	# Contiguous Data
    	# return redirect(url_for('/invalid/<x>'))
    start = str(int(time.time()))
    print(start)
    print(type(start))
    session['location'] = 'data' + '/' + start
    print(session['location'])
    # rename csv and place in user directory
    return render_template('index.html')


@app.route('/invalid/<x>')
def throw_error():
	# Check error method
	error = ''
	return render_template('/', data=error)

@app.route('/analysis.html', methods=['POST', 'GET'])
def analysis():
	return render_template('analysis.html')

	if session['wraparound'] == False:
		session['wraparound'] = True
		initial_data = price_JSON(session['location'])
		# Create json of historical price
		# Inject JSON into analysis template / Render
		return render_template('analysis.html')
	
	elif session['wraparound'] == True:
		query = {'trading_strategy': request.form['trading_strategy'], 
				'option_length': request.form['option_length'],
				'strike': request.form['strike'],
				'user_directory': session['dir'] 
				}
		
		# search_and_compute(query)
		# injection = query_to_JSON(query)
		render_template('analysis.html', data=injection)


if __name__ == '__main__':
	app.run(debug=True)
