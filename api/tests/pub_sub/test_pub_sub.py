import os

from pub_sub import pub_sub
from unittest.mock import ANY, MagicMock, patch


@patch("pub_sub.pub_sub.send")
@patch.dict(os.environ, {"AXE_CORE_URLS_TOPIC": "topic"}, clear=True)
def test_dispatch_adds_an_id_and_calls_send(mock_send):
    pub_sub.dispatch({})
    mock_send.assert_called_once_with("topic", {"id": ANY})


@patch("pub_sub.pub_sub.log")
def test_send_logs_error_if_no_topic_arn_is_found(mock_logger):
    pub_sub.send(None, {})
    mock_logger.error.assert_called_once_with("Topic ARN is not defined")


@patch("pub_sub.pub_sub.boto3")
def test_send_publishes_to_a_sns_topic(mock_boto):
    mock_client = MagicMock()
    mock_boto.client.return_value = mock_client

    payload = {"id": "abcd"}
    pub_sub.send("topic", payload)
    mock_client.publish.assert_called_once_with(
        TargetArn="topic",
        Message='{"default": "{\\"id\\": \\"abcd\\"}"}',
        MessageStructure="json",
    )
