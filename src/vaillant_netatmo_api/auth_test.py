import pytest

from .auth import auth_client

valid_token = {
    "access_token": "12345",
    "refresh_token": "abcde",
    "expires_at": "",
    "expires_in": ""
}

@pytest.fixture
async def mocked_valid_http_client(mocker):
    return None

@pytest.fixture
async def mocked_invalid_http_client(mocker):
    return None

@pytest.mark.asyncio
class TestAuth:
    async def test_async_get_token__wrong_client_id__raises_error(self, mocked_invalid_http_client):
        client_id = ""
        client_secret = ""
        scope = ""
        username = ""
        password = ""
        user_prefix = ""
        app_version = ""

        with auth_client(client_id, client_secret, scope, mocked_invalid_http_client) as client:
            with pytest.raises(Exception, match=r"client_id"):
                await client.async_get_token(username, password, user_prefix, app_version)
    
    # async def test_wrong_client_secret_raises_error(self, auth_client):
    #     with pytest.raises(Exception, match=r"client_secret"):
    #         await auth_client.async_get_token(username, password, user_prefix, app_version)

    # async def test_nonsupported_scope_raises_error(self, auth_client):
    #     with pytest.raises(Exception, match=r"scope"):
    #         await auth_client.async_get_token(username, password, user_prefix, app_version)

    # async def test_missing_username_raises_error(self, auth_client):
    #     with pytest.raises(Exception, match=r"username"):
    #         await auth_client.async_get_token(username, password, user_prefix, app_version)

    # async def test_missing_password_raises_error(self, auth_client):
    #     with pytest.raises(Exception, match=r"password"):
    #         await auth_client.async_get_token(username, password, user_prefix, app_version)

    # async def test_missing_user_prefix_raises_error(self, auth_client):
    #     with pytest.raises(Exception, match=r"user_prefix"):
    #         await auth_client.async_get_token(username, password, user_prefix, app_version)

    # async def test_missing_app_version_raises_error(self, auth_client):
    #     with pytest.raises(Exception, match=r"app_version"):
    #         await auth_client.async_get_token(username, password, user_prefix, app_version)

    async def test_valid_request_params_return_valid_access_token(self, mocked_valid_http_client):
        client_id = ""
        client_secret = ""
        scope = ""
        username = ""
        password = ""
        user_prefix = ""
        app_version = ""

        with auth_client(client_id, client_secret, scope, mocked_valid_http_client) as client:
            token = await client.async_get_token(username, password, user_prefix, app_version)

            assert hasattr(token, "access_token")
            assert token["access_token"] == valid_token.access_token

    async def test_valid_request_params_return_valid_refresh_token(self, auth_client):
        assert True == True

    async def test_valid_request_params_return_valid_token_expiry(self, auth_client):
        assert True == True
