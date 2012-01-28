#!/bin/bash
#Valid queries to mock server

#ENDPOINT /t4t/0.1/disruptions

curl -X GET "localhost:55004/t4t/0.1/disruptions?topleftlat=2.3&topleftlong=10&bottomrightlat=2.1&bottomrightlong=10"

curl -X GET "localhost:55004/t4t/0.1/disruptions?latitude=2.3&longitude=2.1&radius=10"

curl -H "Content-Type:application/json" -X POST "localhost:55004/t4t/0.1/disruptions/route/" -d "{}"

curl -H "Content-Type:application/json" -X POST "localhost:55004/t4t/0.1/report" -d "{}"

