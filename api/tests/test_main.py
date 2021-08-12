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


@patch("main.migrate_head")
def test_handler_migrate_event(mock_migrate_head):
    assert main.handler({"task": "migrate"}, {}) == "Success"
    mock_migrate_head.assert_called_once()


@patch("main.migrate_head")
def test_handler_migrate_event_failed(mock_migrate_head):
    mock_migrate_head.side_effect = Exception()
    assert main.handler({"task": "migrate"}, {}) == "Error"
    mock_migrate_head.assert_called_once()


@patch("main.storage")
def test_handler_record_event_no_s3(mock_storage):
    assert main.handler({"Records": []}, {}) == "Success"
    mock_storage.get_object.assert_not_called()


@patch("main.storage")
def test_handler_record_event_contains_s3(mock_storage):
    assert main.handler({"Records": [{"s3": {}}]}, {}) == "Success"
    mock_storage.get_object.assert_called_once_with({"s3": {}})
