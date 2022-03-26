#!/bin/bash
# Read username and password
read -r -p "Username: " username

# substitute into the curl command
curl -i -X GET -H "accept: application/json" -b cookie-jar \
   -k https://cs3103.cs.unb.ca:26345/user/"$username"/urls
