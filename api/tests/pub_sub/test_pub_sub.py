import os

from pub_sub import pub_sub
from unittest.mock import ANY, MagicMock, patch


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
@patch.dict(os.environ, {"AXE_CORE_URLS_TOPIC": "topic"}, clear=True)
def test_dispatch_adds_an_id_and_calls_send(mock_send, _mock_session, mock_a11y_report_class):
    mock_a11y_report_class().id = "a11y_report"
    pub_sub.dispatch({"scan_id": "scan_id", "url": "url"})
    mock_send.assert_called_once_with("topic", {"id": "a11y_report", "scan_id": "scan_id", 'url': 'url'})


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.log")
def test_send_logs_error_if_no_topic_arn_is_found(mock_logger, _mock_session, mock_a11y_report_class):
    pub_sub.send(None, {"scan_id": "scan_id", "url": "url"})
    mock_logger.error.assert_called_once_with("Topic ARN is not defined")


@patch("pub_sub.pub_sub.get_session")
def test_send_publishes_to_a_sns_topic(mock_get_session):
    mock_client = MagicMock()
    mock_get_session.return_value.client.return_value = mock_client

    payload = {"id": "abcd"}
    pub_sub.send("topic", payload)
    mock_client.publish.assert_called_once_with(
        TargetArn="topic",
        Message='{"default": "{\\"id\\": \\"abcd\\"}"}',
        MessageStructure="json",
    )
