from os import path
import sys, pytest

# Set handlers as root import for tests
sys.path.append(path.join(path.dirname(__file__), '../handlers'))

# imports "dynamodb" fixture
from pytest_dynamodb import factories


@pytest.fixture()
def table(dynamodb):
    # Create a coa_publisher_test dynamodb table.
    # Follows the same schema defined in src/templates/dynamodb.yml
    return dynamodb.create_table(
        TableName='coa_publisher_test',
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
