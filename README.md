# snapshotalyzer-30000
Python demo project for EC2 snapshot

# About
Demo project for ACG course, with python3 and boto3

# Configure
`aws configure --profile acg-python`

# Run
Run some EC2 activities, WIP
`pipenv run python shotty/shotty.py <resource> <command> <--project=PROJECT>`

*resource* is instances, volumes, snapshots
*command* is list, start, stop or snapshot (as appropriate)
*PROJECT* is optional, or match your tag key project value.
