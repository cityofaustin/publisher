from os import path
import sys, pytest

# Set handlers as root import for tests
sys.path.append(path.join(path.dirname(__file__), '../handlers'))
sys.path.append(path.join(path.dirname(__file__), '..'))

# imports "dynamodb" fixture
from pytest_dynamodb import factories


@pytest.fixture()
def dynamodb_table(dynamodb):
    # Create a coa_publisher_test dynamodb table.
    # Follows the same schema defined in src/templates/dynamodb.yml
    table = dynamodb.create_table(
        TableName='coa_publisher_pytest',
        KeySchema=[
            {
                'AttributeName': 'pk',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'sk',
                'KeyType': 'Range'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'pk',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'sk',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'build_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'status',
                'AttributeType': 'S'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'build_id.janis',
                'KeySchema': [
                    {
                        'AttributeName': 'build_id',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'pk',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                },
                # Required, but ignored locally
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 123,
                    'WriteCapacityUnits': 123
                }
            },
        ],
        LocalSecondaryIndexes=[
            {
                'IndexName': 'janis.status',
                'KeySchema': [
                    {
                        'AttributeName': 'pk',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'status',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                },
            },
        ],
        # Required, but ignored locally
        ProvisionedThroughput={
            'ReadCapacityUnits': 123,
            'WriteCapacityUnits': 123
        },
    )
    table.meta.client.get_waiter('table_exists').wait(TableName='coa_publisher_pytest')
    return table


@pytest.fixture()
def dynamodb_client(dynamodb_table):
    return dynamodb_table.meta.client


# Patches publish_request_handler's get_dynamodb_table() function to use our local dynamodb_client fixture.
# Most tests are excepted to fail before there is an interaction with dynamodb. But we'll run this patch for each of them just in case of a false negative.
@pytest.fixture
def patch_demo_table(mocker, dynamodb_table):
    mocker.patch('handlers.publish_request_handler.get_dynamodb_table', return_value=dynamodb_table)
