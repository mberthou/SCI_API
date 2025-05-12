# PACE_API

# for local testing
* install docker
* install dynamodb docker image
$ docker run -p 8000:8000 amazon/dynamodb-local
* initialize table
$ aws dynamodb create-table --cli-input-json file://configs/create_scidata_table.json --endpoint-url http://localhost:8000

* start api localy using sam (provided by aws toolkit), needs dockers installed and started locally
$ sam local start-api
for step by step debugging in vscode, use launch configurations defined in .vscode/launch.json


# for remote deployement
* for deploying
$ sam build
$ sam deploy --guided

* for deleting application from AWS
$ sam delete --stack-name ScientificDataRepository