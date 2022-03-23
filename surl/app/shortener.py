#!/usr/bin/env python3

import sys
from flask import Flask, jsonify, abort, request, make_response, session, redirect
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import pymysql.cursors
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import ssl

import cgitb
import cgi
import sys
cgitb.enable()

import settings # Our server and db settings, stored in settings.py

app = Flask(__name__, static_url_path='/static')
api = Api(app)

app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

####################################################################################
# Error handlers

@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { "status": "Bad request" } ), 400)

@app.errorhandler(403) # decorators to add to 403 response
def not_found(error):
	return make_response(jsonify( { "status": "Unauthorized - Not Signed In" } ), 403)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { "status": "Resource not found" } ), 404)

#Redirects the page to the corresponding long url
class RedirectPage(Resource):
	def get(self, url_id):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getURL'
			cursor = dbConnection.cursor()
			sqlArgs = (url_id,)
			cursor.callproc(sql,sqlArgs)
			row = cursor.fetchone()
			if row is None:
				abort(404)
			else:
				short_uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT)
				short_uri = short_uri + '/'+str(row['short_url'])
				return redirect(row['long_url'], code=303)
		except:
			abort(404)
		finally:
			cursor.close()
			dbConnection.close()

api.add_resource(RedirectPage,'/<string:url_id>')

class Root(Resource):
	def get(self):
		return app.send_static_file('index.html')

api.add_resource(Root, '/index.html')

class RootGetURL(Resource):
	# GET: Return full URL data from short URL
	#
	# Example request:
	# curl -i -X GET -H "accept: application/json" -b cookie-jar
	# 	-k https://cs3103.cs.unb.ca:26345/{url_id}
	def get(self, url_id):
		if not SignIn().isSignedIn():
			abort(403, description="Not Signed In")
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getURL'
			cursor = dbConnection.cursor()
			sqlArgs = (url_id,)
			cursor.callproc(sql,sqlArgs)
			row = cursor.fetchone()
			if row is None:
				abort(404)
			else:
				short_uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT)
				short_uri = short_uri + '/'+str(row['short_url'])
				return make_response(jsonify({"long_url": row['long_url'], "short_url": short_uri}), 200) # successful
		except:
			abort(404)
		finally:
			cursor.close()
			dbConnection.close()

api.add_resource(RootGetURL, '/api/<string:url_id>')



# URL shorten routing: GET and POST, individual shorten access
class Shorten(Resource):
	def post(self):
		# POST: Create a shortened URL from long URL
        # Sample command line usage:
        #
		# curl -i -X POST -H "Content-Type: application/json" 
		# 	-d '{"longURL": "https://www.verylongurl.com"}' 
		#		-b cookie-jar -k https://cs3103.cs.unb.ca:26345/shorten
		if not SignIn().isSignedIn():
			abort(403, description="Unauthorized - Not Signed In")

		if not request.json or not 'longURL' in request.json:
			abort(400)

		longURL = request.json['longURL']
		user = SignIn().getUsername()

		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addURL'
			cursor = dbConnection.cursor()
			sqlArgs = (longURL,user) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			if row is None:
				abort(500)
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		# Look closely, Grasshopper: we just created a new resource, so we're
		# returning the uri to it, based on the return value from the stored procedure.
		# Yes, now would be a good time check out the procedure.
		uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT)
		uri = uri + '/'+ str(row['short_url'])
		return make_response(jsonify( { "shortURL" : uri } ), 201) # successful resource creation


####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Shorten, '/shorten')
#api.add_resource(Shorten, '/shorten/<string:short_url>')

####################################################################################
#
# User-related functions
#
class UserList(Resource):
	# GET: Display User Info
	#
	# Example request:
	# curl -i -X GET -H "accept: application/json" -b cookie-jar
	# 	-k https://cs3103.cs.unb.ca:26345/user/{username}/urls
	def get(self, username):
		if not SignIn().isSignedIn():
			abort(403, description="Not Signed In")
		elif username != SignIn().getUsername():
			abort(403, description="Unauthorized Access")
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserURLs'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			results = cursor.fetchall() # get the list result
			if results is None:
				abort(500)
			else:
				output = []
				for row in results:
					short_uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT) + '/'+str(row['short_url'])
					output.append({"long_url": row['long_url'], "short_url": short_uri, "url_id": row['short_url']})								
				return make_response(jsonify(output), 200) # successful
		except Exception as e:
			abort(500, description=getattr(e, 'message', repr(e)))
		finally:
			cursor.close()
			dbConnection.close()			

api.add_resource(UserList, '/user/<string:username>/urls')

class UserURL(Resource):
	# GET: Display data for a specified URL owned by a specified user
	#
	# Example request:
	# curl -i -X GET -H "accept: application/json" -b cookie-jar
	# 	-k https://cs3103.cs.unb.ca:26345/user/{username}/urls/{url_id}
	def get(self, username, url_id):
		if not SignIn().isSignedIn():
			abort(403, description="Not Signed In")
		elif username != SignIn().getUsername():
			abort(403, description="Unauthorized Access")
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getURL'
			cursor = dbConnection.cursor()
			sqlArgs = (url_id,)
			cursor.callproc(sql,sqlArgs) 
			row = cursor.fetchone() 
			if row is None:
				abort(404, description="URL Resource not found")
			else:
				short_uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT)
				short_uri = short_uri + '/'+str(row['short_url'])
				return make_response(jsonify({"long_url": row['long_url'], "short_url": short_uri, "url_id": row['short_url']}), 200) # successful
		except:
			abort(404, description="URL Resource not found")
		finally:
			cursor.close()
			dbConnection.close()

	# DELETE: Deletes a user's url resource
    #
    # Example request: 
	# curl -i -X DELETE -H "accept: application/json" -b cookie-jar
	# 	-k https://cs3103.cs.unb.ca:26345/user/{username}/urls/{url_id}
	def delete(self, username, url_id):
		if not SignIn().isSignedIn():
			abort(403, description="Not Signed In")
		elif username != SignIn().getUsername():
			abort(403, description="Unauthorized Access")
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'deleteShortURL'
			cursor = dbConnection.cursor()
			sqlArgs = (url_id, username)
			cursor.callproc(sql,sqlArgs) 
			row = cursor.fetchone() 
			dbConnection.commit() 
		except:
			abort(404, description="URL Resource not found")
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"message": "Success: URL Resource Deleted"}), 200) # successful deletion

api.add_resource(UserURL, '/user/<string:username>/urls/<string:url_id>')

####################################################################################
# SIGN IN
####################################################################################

####################################################################################
#
# Routing: GET and POST using Flask-Session
#
class SignIn(Resource):
	#
	# Set Session and return Cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "User123", "password": "password123"}'
	#  	-c cookie-jar -k https://cs3103.cs.unb.ca:26345/signin
	#
	def post(self):

		if not request.json:
			abort(400) # bad request

		# Parse the json
		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request

		if request_params['username'] in session:
			response = {'message': 'Success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
				response = {'message': 'Success - Signed In' }
				responseCode = 200
			except LDAPException:
				response = {'message': 'Invalid Credentials'}
				responseCode = 401
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	# GET: Check Cookie data with Session data
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar
	#	-k https://cs3103.cs.unb.ca:26345/signin
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'Success - Signed In'}
			responseCode = 200
		else:
			response = {'status': 'Not Found - No Login Session'}
			responseCode = 404
		return make_response(jsonify(response), responseCode)

	# DELETE: Logout: remove session
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE 
	# 	-c cookie-jar -k https://cs3103.cs.unb.ca:26345/signin

	def delete(self):
		session.pop('username', None)
		response = {'message': 'Success - Signed Out'}
		responseCode = 200
		return make_response(jsonify(response), responseCode)

	def isSignedIn(self):
		return True if 'username' in session else False

	def getUsername(self):
		return session['username']
####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(SignIn, '/signin')

#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
	#
	# You need to generate your own certificates. To do this:
	#	1. cd to the directory of this app
	#	2. run the makeCert.sh script and answer the questions.
	#	   It will by default generate the files with the same names specified below.
	#
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)
