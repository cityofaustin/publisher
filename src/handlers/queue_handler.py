

def handler(event, context):
    print("hi")
    for record in event['Records']:
        print(record['eventID'])
        print(record['eventName'])
        print(record['dynamodb'])
    print('Successfully processed %s records.' % str(len(event['Records'])))
