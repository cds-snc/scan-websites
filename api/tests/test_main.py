import main
from unittest.mock import MagicMock, patch


@patch("main.Mangum")
def test_handler_api_gateway_event(mock_mangum):
    mock_asgi_handler = MagicMock()
    mock_asgi_handler.return_value = True
    mock_mangum.return_value = mock_asgi_handler
    assert main.handler({"httpMethod": "GET"}, {}) is True
    mock_asgi_handler.assert_called_once_with({"httpMethod": "GET"}, {})


@patch("main.log")
def test_handler_unmatched_event(mock_logger):
    assert main.handler({}, {}) is False
    mock_logger.warning.assert_called_once_with("Handler recieved unrecognised event")
