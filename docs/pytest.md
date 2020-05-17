## Pytest
Run unit tests with `pipenv run pytest`.

Add tests to `src/tests` folder, following the pattern defined in `pytest.ini`.

### Run all tests
`pipenv run pytest`

### Run one test
`pipenv run pytest src/tests/test_dynamodb.py`

## Dynamodb
Some tests require running against a local dynamodb instance.
Download dynamodb from this link: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html

Extract the directory and copy it into the `/tests` directory. It must match the setting we've set in pytest.ini (`dynamodb_dir = ./src/tests/dynamodb_local_latest`) so that the pytest_dynamodb library can find it. https://pypi.org/project/pytest-dynamodb/.

<p align="left">
  <img src="/docs/images/dynamo_dir.png" width="200">
</p>

More notes about running dynamodb locally: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.UsageNotes.html

### Changing the Dynamodb port
I've set dynamodb to run on port 8008. You can change that by following these steps.

1. Set the "PUBLISHER_DYNAMODB_PORT" value in .env
2. Set the "dynamodb_port" value in pytest.ini
