#!/bin/bash
# Read username and password
read -r -p "Long URL: " long_url

# substitute into the curl command
curl -i -X POST -H "Content-Type: application/json" \
   -d '{"longURL": "'$long_url'"}' \
      -b cookie-jar \
         -k https://cs3103.cs.unb.ca:26345/shorten
