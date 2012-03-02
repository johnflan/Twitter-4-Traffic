#!/bin/bash
#Valid queries to mock server

#ENDPOINT /t4t/0.1/disruptions

#V0.1
curl -X GET "localhost:55005/t4t/0.1/disruptions?topleftlat=2.3&topleftlong=10&bottomrightlat=2.1&bottomrightlong=10"

curl -X GET "localhost:55005/t4t/0.1/disruptions?latitude=2.3&longitude=2.1&radius=10"

curl -H "Content-Type:application/json" -X POST "localhost:55005/t4t/0.1/disruptions/route/" -d "{}"

curl -H "Content-Type:application/json" -X POST "localhost:55005/t4t/0.1/report" -d "{}"

#V0.2
curl -X GET "localhost:55005/t4t/0.2/disruptions?topleftlat=51.50&topleftlong=-0.15&bottomrightlat=51.51&bottomrightlong=-0.16"

curl -X GET "localhost:55005/t4t/0.2/disruptions?latitude=51.50&longitude=-0.18&radius=1000"

curl -H "Content-Type:application/json" -X POST "localhost:55005/t4t/0.2/disruptions/route/" -d '{"points":[{"lon":"-0.18","lat":"51.51"},{"lon":"-0.10","lat":"51.47"}]}'