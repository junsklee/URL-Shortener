#!/usr/bin/env python3

import sys
from flask import Flask, jsonify, abort, request, make_response, session
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
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { "status": "Bad request" } ), 400)

@app.errorhandler(403) # decorators to add to 403 response
def not_found(error):
	return make_response(jsonify( { "status": "Unauthorized - Not Signed In" } ), 403)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { "status": "Resource not found" } ), 404)

####################################################################################
#
# Static Endpoints for humans
#
class Root(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('index.html')

api.add_resource(Root,'/')

class RootGetURL(Resource):
	# GET: Return full URL data from short URL
	#
	# Example request:
	# curl -i -X GET -H "accept: application/json" -b cookie-jar
	# 	-k https://cs3103.cs.unb.ca:26345/{short_url}
	def get(self, short_url):
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
			sqlArgs = (short_url,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
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


api.add_resource(RootGetURL, '/<string:short_url>')

class Developer(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('developer.html')
	
api.add_resource(Developer,'/dev')

####################################################################################
#
# URL shorten routing: GET and POST, individual shorten access
#
class Shorten(Resource):
	def post(self):
        #
		# POST: Create a shortened URL from long URL
        # Sample command line usage:
        #
		# curl -i -X POST -H "Content-Type: application/json" 
		# 	-d '{"longURL": "https://www.verylongurl.com"}' 
		#		-b cookie-jar -k https://cs3103.cs.unb.ca:26345/shorten
		if not SignIn().isSignedIn():
			abort(403, description="Unauthorized - Not Signed In")

		if not request.json or not 'longURL' in request.json:
			abort(400) # bad request
		# Pull the results out of the json request
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
		uri = uri + '/'+str(row['short_url'])
		return make_response(jsonify( { "shortURL" : uri } ), 201) # successful resource creation

	'''
    # DELETE: Delete identified url resource
    #
    # Example request: curl -X DELETE https://cs3103.cs.unb.ca:xxxxx/user/2
	def delete(self, urlId):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'deleteURL'
			cursor = dbConnection.cursor()
			sqlArgs = (urlId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
			if row is None:
				make_response(jsonify({"longURL": row}), 204) # no data
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"longURL": row}), 202) # successful deletion
		return
		'''
####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Shorten, '/shorten')
#api.add_resource(Shorten, '/shorten/<String:short_url>')

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
			response = {'status': 'success'}
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
				response = {'status': 'success' }
				responseCode = 200
			except LDAPException:
				response = {'status': 'Invalid Credentials'}
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
		response = {'msg': 'Success - No Content'}
		responseCode = 204
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
