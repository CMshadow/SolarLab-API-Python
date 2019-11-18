# SolarLab-API-Python
SolarLab APIs on AWS Lambda, Python codes

## Build Application
```shell
$ sam build
```

## Test Application Locally
- `event.json` : Test event JSON file
```shell
$ sam local invoke --event ./events/event.json
```

## Package SAM template

- `template.yaml` : Lambda function settings
- `packaged.yaml` : deploy settings
  
```shell
$ sam package --template-file template.yaml --s3-bucket solarlab-sam-lambda --output-template-file packaged.yaml
```

## Deploy packaged SAM template

- `packaged.yaml` : deploy settings
- `solarlab-api-python` : the name of the stack on CloudFormation after deployment
  
```shell
$ sam deploy --template-file ./packaged.yaml --stack-name solarlab-api-python --capabilities CAPABILITY_IAM
```
