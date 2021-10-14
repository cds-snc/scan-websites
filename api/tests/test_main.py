import main
import json
from unittest.mock import MagicMock, patch


@patch("main.Mangum")
def test_handler_api_gateway_event(mock_mangum, context_fixture, capsys):
    mock_asgi_handler = MagicMock()
    mock_asgi_handler.return_value = True
    mock_mangum.return_value = mock_asgi_handler
    assert main.handler({"httpMethod": "GET"}, context_fixture) is True
    mock_asgi_handler.assert_called_once_with({"httpMethod": "GET"}, context_fixture)

    log = capsys.readouterr().out.strip()
    metrics_output = json.loads(log)

    assert "ScanWebsites" in log
    assert (
        "ColdStart"
        in metrics_output["_aws"]["CloudWatchMetrics"][0]["Metrics"][0]["Name"]
    )
    assert metrics_output["function_name"] == "api"


@patch("main.log")
def test_handler_unmatched_event(mock_logger, context_fixture):
    assert main.handler({}, context_fixture) is False
    mock_logger.warning.assert_called_once_with("Handler received unrecognised event")


@patch("main.migrate_head")
def test_handler_migrate_event(mock_migrate_head, context_fixture):
    assert main.handler({"task": "migrate"}, context_fixture) == "Success"
    mock_migrate_head.assert_called_once()


@patch("main.migrate_head")
def test_handler_migrate_event_failed(mock_migrate_head, context_fixture):
    mock_migrate_head.side_effect = Exception()
    assert main.handler({"task": "migrate"}, context_fixture) == "Error: "
    mock_migrate_head.assert_called_once()


@patch("main.storage")
def test_handler_record_event_no_records(mock_storage, context_fixture):
    assert main.handler({"Records": []}, context_fixture) == "Success"
    mock_storage.get_object.assert_not_called()


@patch("main.storage")
def test_handler_record_event_contains_s3(mock_storage):
    assert main.handler({"Records": [{"s3": {}}]}, {}) == "Success"
    mock_storage.retrieve_and_route.assert_called_once_with({"s3": {}})


@patch("main.log")
@patch("main.storage")
def test_handler_record_event_contains_unrecognised_event(mock_storage, mock_logger):
    assert main.handler({"Records": [{"sns": {}}]}, {}) == "Success"
    mock_storage.get_object.assert_not_called()
    mock_logger.warning.assert_called_once_with(
        "Handler received unrecognised record: {'sns': {}}"
    )
