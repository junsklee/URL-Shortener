# URL-Shortener
A URL shortener in the web, bulit with Python, MySQL and Flask. This program runs on top of an LDAP server with existing credentials.

# API Scripts

Instructions:

1. run surl/app/app.py  
2. run ./signinClient.sh and enter your FCS LDAP credentials to sign in.
3. run any script below: ./<script_name.sh>

Script Files:

signinClient.sh - Client used to sign in. This creates a cookie that should keep you signed in througout your session. Uses FCS LDAP credentials, there is no need to register.
	- API: POST /signin

signoutClient.sh - Client used to sign out.
	- API: DELETE /signin

shortenURL.sh - Shortens Long URL
	- API: POST /shorten

URLRedirectPage.sh - Gets the redirect page of the short URL in html.
	- API: GET /{url_id}

getURL.sh - Gets URL information by the short url
 	- API: GET /{url_id}/info

getURLById.sh - Gets URL information by url_id
 	- API: GET /{url_id}/info

getAllUserURLs.sh - Gets a list of all user URLs, only for the signed in user.
	- API: GET /user/{username}/urls

getUserURL.sh - Gets a specific URL (user-provided url_id) only for the signed in user.
	- API: GET /user/{username}/urls/{url_id}

deleteUserURL.sh - Deletes the user's URL at specified url_id (only for the signed in user)
	- API: DELETE /user/{username}/urls/{url_id}

## Examples:

signinClient.sh 
	[user_name@surl API]$ ./signinClient.sh
	username (FCS LDAP): user_name
	password: ********
	
	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:05:32 GMT; HttpOnly; Path=/
	Content-Length: 64
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:05:32 GMT

	{
	  "message": "Success - Signed In", 
	  "username": "user_name"
	}


signoutClient.sh 
	[user_name@surl API]$ ./signoutClient.sh
	  
	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=9e9ff5b4-84b2-4f62-9941-e1d31dac9b50; Domain=surl.ca; Expires=Fri, 13-May-2022 23:04:17 GMT; HttpOnly; Path=/
	Content-Length: 40
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:04:17 GMT

{
  "message": "Success - Signed Out"
}


shortenURL.sh 
	[user_name@surl API]$ ./shortenURL.sh
	Long URL: www.articlegeek.com

	Response:
	HTTP/1.0 201 CREATED
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:05:37 GMT; HttpOnly; Path=/
	Content-Length: 57
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:05:37 GMT

	{
	  "shortURL": "https://surl.cs.unb.ca:26345/267e2"
	}

URLRedirectPage.sh 
	[user_name@surl API]$ ./URLRedirectPage.sh 
	Short URL: https://surl.ca:26345/267e2 

	Response:
	HTTP/1.0 303 SEE OTHER
	Content-Type: text/html; charset=utf-8
	Content-Length: 261
	Location: https://www.articlegeek.com
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:09:01 GMT; HttpOnly; Path=/
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:09:01 GMT

	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
	<title>Redirecting...</title>
	<h1>Redirecting...</h1>
	<p>You should be redirected automatically to target URL: <a href="https://www.articlegeek.com">https://www.articlegeek.com</a>.  If not click the link.[user_name@surl API]$ 


getURL.sh 
 	[user_name@surl API]$ ./getURL.sh
	Short URL: https://surl.ca:26345/267e2

	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:10:17 GMT; HttpOnly; Path=/
	Content-Length: 96
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:10:17 GMT

	{
	  "long_url": "www.articlegeek.com", 
	  "short_url": "https://surl.ca:26345/267e2"
	}


getURLById.sh 
 	[user_name@surl API]$ ./getURLById.sh 
	URL ID: 267e2

	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:11:01 GMT; HttpOnly; Path=/
	Content-Length: 96
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:11:01 GMT

	{
	  "long_url": "www.articlegeek.com", 
	  "short_url": "https://surl.ca:26345/267e2"
	}


getAllUserURLs.sh 
	[user_name@surl API]$ ./getAllUserURLs.sh
	Username: user_name

	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:11:43 GMT; HttpOnly; Path=/
	Content-Length: 3331
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:11:43 GMT

	[
	  {
	    "long_url": "lensdump.com", 
	    "short_url": "https://surl.ca:26345/9de20", 
	    "url_id": "9de20"
	  }, 
	  {
	    "long_url": "www.articlegeek.com", 
	    "short_url": "https://surl.ca:26345/267e2", 
	    "url_id": "267e2"
	  }
	]



getUserURL.sh 
	[user_name@surl API]$ ./getUserURL.sh 
	Username: user_name
	URL ID: 267e2

	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:12:59 GMT; HttpOnly; Path=/
	Content-Length: 118
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:12:59 GMT

	{
	  "long_url": "www.articlegeek.com", 
	  "short_url": "https://surl.ca:26345/267e2", 
	  "url_id": "267e2"
	}


deleteUserURL.sh
	[user_name@surl API]$ ./deleteUserURL.sh
	Username: user_name
	URL ID: 267e2

	Response:
	HTTP/1.0 200 OK
	Content-Type: application/json
	Set-Cookie: peanutButter=3ff66698-31ba-4164-b571-02d4cc04ddd2; Domain=surl.ca; Expires=Fri, 13-May-2022 23:13:24 GMT; HttpOnly; Path=/
	Content-Length: 49
	Server: Werkzeug/0.12.2 Python/3.6.8
	Date: Tue, 12 Apr 2022 23:13:24 GMT

	{
	  "message": "Success: URL Resource Deleted"
	}





