import os


# Make sure our environment variables match what's in pytest.ini
def test_deploy_env():
    assert os.getenv("DEPLOY_ENV") == "pytest"
    assert os.getenv("AWS_REGION") == "us-east-1"


# Test that mocker allows us to mock an imported function, with static return_value
def test_patching(mocker):
    mocker.patch('handlers.helpers.utils.is_staging', return_value=True)
    mocker.patch('handlers.helpers.utils.is_production', return_value=True)
    from handlers.helpers.utils import is_staging, is_production
    assert os.getenv("DEPLOY_ENV") == "pytest"
    assert is_staging() is True
    assert is_production() is True


# Test that mocker allows us to mock an imported function, with dynamic return value
def test_patching_as_function(mocker):
    def identity(data):
        return data
    mocker.patch('handlers.helpers.utils.is_staging', side_effect=identity)
    from handlers.helpers.utils import is_staging
    assert is_staging("banana") == "banana"


# Baseline test to show that mocker works in our following test
def test_nested_baseline(mocker):
    from tests.helpers.testing_tools_helper import nested_is_staging
    assert nested_is_staging() is False


# Test that mocker allows us to mock a function that's nested inside an external file.
# This is subtle. We are replacing the "is_staging" instance used within "tests.helpers.testing_tools_helper".
# That way, when "nested_is_staging" calls "is_staging", its using our mocked version.
# This will be useful for replacing nested functions in our handlers.
# Read through this section a couple of times: https://docs.python.org/3/library/unittest.mock.html#where-to-patch
def test_patching_nested(mocker):
    mocker.patch('tests.helpers.testing_tools_helper.is_staging', return_value=True)
    from tests.helpers.testing_tools_helper import nested_is_staging
    assert nested_is_staging() is True


# Test that patching can work with a re-import
def test_patching_nested_after_import(mocker):
    from tests.helpers.testing_tools_helper import nested_is_staging
    mocker.patch('tests.helpers.testing_tools_helper.is_staging', return_value=True)
    from tests.helpers.testing_tools_helper import nested_is_staging
    assert nested_is_staging() is True
