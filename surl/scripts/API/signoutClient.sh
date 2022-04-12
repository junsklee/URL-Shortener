#!/bin/bash
# curl command signout
curl -i -H "Content-Type: application/json" -X DELETE \
   -c cookie-jar -k https://cs3103.cs.unb.ca:26345/signin
