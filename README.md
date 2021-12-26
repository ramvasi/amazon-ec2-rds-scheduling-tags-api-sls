# EC2/RDS Instance Schedule Tags API

    This project contains a centralized API to add/delete/get the schedule tags for RDS and EC2 instances in a multi-account AWS Organizations implementation.
    The scheduling tags(on-hours, off-hours) can be used by AWS Config policies or Cloud Custodian policies to automate starting and stopping RDS/EC2 instances for cost saving measures.
    
    API features: 
    * API adds, deletes, and gets the 'on-hours' and 'off-hours' tags on a particular RDS/EC2 instance
    * Create schedule tag request when tag exists will have tag updated if there are changes
    * Delete schedule tag request on instance without tag will return 200 OK
    * Date/Time will be stored in UTC format
        Incoming request payload will have the local time zone (tz database name) of the request. The API translates the time zone to the UTC time.
    * Invoke POST call and verify the schedule tag gets added
        Tag will be Key-Value Pair with Key=on-hours or off-hours and Value indicating Days (M-F) and Time in 24h format
        Example on-hours tag is as follows 
            For RDS, "Key": "on-hours", "Value": "M-F/5:tz=utc:"
            For EC2, "Key": "on-hours", "Value": "(M-F,5);tz=utc;"
        Example off-hours tag is as follows 
            For RDS, "Key": "off-hours", "Value": "M-F/20:tz=utc:"
            For EC2, "Key": "off-hours", "Value": "(M-F,20);tz=utc;"
    * Invoke DELETE call and verify the schedule tag gets removed
    * Invoke GET call and verify the schedule tag is retrieved
    

## Architecture
![Architecture2](docs/arch.png)

```
.
├── README.md                     <-- This documentation file
├── add_schedule_tags             <-- Lambda function that adds schedule tags for a resource
├── delete_schedule_tags          <-- Lambda function that deletes schedule tags for a resource
├── get_schedule_tags             <-- Lambda function that lists schedule tags for a resource
├── schedule-tags-api.yaml        <-- Swagger doc 
└── serverless.yml                <-- Serverless application definition file
```
## Pre-requisites
```shell script
Install NodeJS
Install Serverless framework
Install Python 3.6, Pip3
```


## Test
```shell script
#Install Python requirements
pip3 install -r requirements.txt

pytest ./
```

## Deployment
```shell script
# Install serverless framework dependencies from package.json
npm i

#Deploy API
serverless deploy -s dev
```

## Integration Test
```
behave sls/schedule_tags_api/get_schedule_tags/tests/bdd/
behave sls/schedule_tags_api/delete_schedule_tags/tests/bdd/
behave sls/schedule_tags_api/put_schedule_tags/tests/bdd/
```

## OpenAPI Spec
The OpenAPI spec for the API is located at [docs/openapi.yml](docs/openapi.yml)

## Example Usage

```bash
# Get schedule tags from account-id=itx-000, in region=us-west-2 and for ec2 instance with id = i-instance-000

curl -X GET 
     -H 'Content-Type: application/json' 
     -H 'authorization: Bearer AMvcMSfZoAHnlXX0cAIhAKsJx8Pp' 
     https://vpce-01227fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev/v1/accounts/itx-000/regions/us-west-2/ec2/i-instance00/schedule

# Delete on-hours, off-hours schedule tags from account-id=itx-000, in region=us-west-2 and for ec2 instance with id = i-instance-000

curl -X DELETE 
     -H 'Content-Type: application/json' 
     -H 'authorization: Bearer AMvcMSfZoAHnlXX0cAIhAKsJx8Pp' 
     https://vpce-01271027fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev/v1/accounts/itx-000/regions/us-west-2/ec2/i-instance00/schedule

# Put on-hours schedule tag for account-id=itx-000, in region=us-west-2 and for ec2 instance with id = i-instance-000

curl -X PUT 
     -H 'Content-Type: application/json' 
     -H 'authorization: Bearer AMvcMSfZoAHnlXX0cAIhAKsJx8Pp' 
    -d  {'timezone': 'America/Chicago','type': 'on-hours','frequency': 'M-F','time': 20}
     https://vpce-012427fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev/v1/accounts/itx-000/regions/us-west-2/ec2/i-instance00/schedule

```

## License
This library is licensed under the MIT-0 License. See the LICENSE file.