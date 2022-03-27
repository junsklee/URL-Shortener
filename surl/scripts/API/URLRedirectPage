#!/bin/bash
# Read username and password
read -r -p "Short URL: " url

# substitute into the curl command
curl -i -X GET -H "accept: application/json" -b cookie-jar \
   -k "$url"
