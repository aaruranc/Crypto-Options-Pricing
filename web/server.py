from flask import Flask, request, render_template, session
import os
import sys 
import time
from pathlib import Path
# from pricing.module_1 import module_1_function
# from pricing.module_2 import module_2_function  
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parameters.html', methods=['POST', 'GET'])
def parameters():
    if request.method == 'POST':
        
        if session.get('dir') == None:
            start = int(time.time())
            session['dir'] = start

            # Initialize User Directory
            print('XXXXXXXXXXXXXXXXXXX')
            user_directory = Path('data') / str(start)
            print(user_directory)
            session['dir_path'] = user_directory
            os.mkdir(user_directory)
            print('XXXXXXXXXXXXXXXXXXX')

            csv = request.files['historical']
            dest = user_directory / 'historical.csv'
            print('XXXXXXXXXXXXXXXXXXX', file=sys.stderr)
            csv.save(dest)



    
    return render_template('parameters.html')


@app.route('/analysis.html', methods=['POST', 'GET'])
def analysis():
    return render_template('analysis.html')

 #    location = session['dir']
 #    if session['wraparound'] == False:
 #        # Generate Directory and perform initial file handling
 #    	user_parameters = {}
 #    	for header in request.form:
 #    		user_parameters.update({header: request.form[header]})     	
 #    	module_1_function(user_parameters, location)
 #    	session['wraparound'] = True
		

	# if session['wraparound'] == True:
	# 	viz_parameters = {}
 #    	for header in request.form:
 #    		user_parameters.update({header: request.form[header]})

 #    	# Modify csv's, Generate Graphs and push relevant info to dictionary
 #    	user_dict = module_2_function(viz_parameters, location)
 #    	return render_template('analysis.html', user_dict)


if __name__ == '__main__':
	app.run(debug=True)