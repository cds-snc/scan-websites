import pytest

from pub_sub import pub_sub
from unittest.mock import MagicMock, patch


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
def test_dispatch_adds_an_id_and_calls_send(
    mock_send, _mock_session, mock_a11y_report_class
):
    mock_a11y_report_class().id = "a11y_report"
    pub_sub.dispatch(
        {
            "type": pub_sub.AvailableScans.AXE_CORE.value,
            "product": "foo",
            "revision": "bar",
            "template_id": "123",
            "scan_id": "scan_id",
            "url": "url",
            "event": "sns",
            "queue": "AXE_CORE_URLS_TOPIC",
        }
    )
    mock_send.assert_called_once_with(
        "AXE_CORE_URLS_TOPIC",
        {
            "type": pub_sub.AvailableScans.AXE_CORE.value,
            "product": "foo",
            "revision": "bar",
            "template_id": "123",
            "scan_id": "scan_id",
            "url": "url",
            "event": "sns",
            "queue": "AXE_CORE_URLS_TOPIC",
            "id": "a11y_report",
        },
    )


@patch("pub_sub.pub_sub.SecurityReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
def test_security_dispatch_adds_an_id_and_calls_send(
    mock_send, _mock_session, mock_security_report_class
):
    mock_security_report_class().id = "security_report"
    pub_sub.dispatch(
        {
            "type": pub_sub.AvailableScans.OWASP_ZAP.value,
            "product": "foo",
            "revision": "bar",
            "template_id": "123",
            "scan_id": "scan_id",
            "url": "url",
            "event": "sns",
            "queue": "OWASP_ZAP_URLS_TOPIC",
        }
    )
    mock_send.assert_called_once_with(
        "OWASP_ZAP_URLS_TOPIC",
        {
            "type": pub_sub.AvailableScans.OWASP_ZAP.value,
            "product": "foo",
            "revision": "bar",
            "template_id": "123",
            "scan_id": "scan_id",
            "url": "url",
            "event": "sns",
            "queue": "OWASP_ZAP_URLS_TOPIC",
            "id": "security_report",
        },
    )


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
def test_dispatch_logs_error_if_no_type_is_defined(
    mock_send, _mock_session, mock_a11y_report_class
):
    mock_a11y_report_class().id = "a11y_report"
    with pytest.raises(ValueError):
        pub_sub.dispatch(
            {
                "product": "foo",
                "revision": "bar",
                "template_id": "123",
                "scan_id": "scan_id",
                "url": "url",
                "event": "sns",
                "queue": "AXE_CORE_URLS_TOPIC",
            }
        )


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
def test_dispatch_logs_error_if_mandatory_key_is_missing(
    mock_send, _mock_session, mock_a11y_report_class
):
    mock_a11y_report_class().id = "a11y_report"
    with pytest.raises(ValueError):
        pub_sub.dispatch(
            {
                "type": pub_sub.AvailableScans.AXE_CORE.value,
                "revision": "bar",
                "template_id": "123",
                "scan_id": "scan_id",
                "url": "url",
                "event": "sns",
                "queue": "AXE_CORE_URLS_TOPIC",
            }
        )


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
def test_dispatch_logs_error_if_unknown_type_is_specified(
    mock_send, _mock_session, mock_a11y_report_class
):
    mock_a11y_report_class().id = "a11y_report"
    with pytest.raises(ValueError):
        pub_sub.dispatch(
            {
                "type": "baz",
                "revision": "bar",
                "template_id": "123",
                "scan_id": "scan_id",
                "url": "url",
                "event": "sns",
                "queue": "AXE_CORE_URLS_TOPIC",
            }
        )


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.send")
def test_dispatch_logs_error_if_queue_is_undefined(
    mock_send, _mock_session, mock_a11y_report_class
):
    mock_a11y_report_class().id = "a11y_report"
    with pytest.raises(ValueError):
        pub_sub.dispatch(
            {"type": "axe-core", "scan_id": "scan_id", "url": "url", "event": "sns"}
        )


@patch("pub_sub.pub_sub.A11yReport")
@patch("pub_sub.pub_sub.db_session")
@patch("pub_sub.pub_sub.log")
def test_send_logs_error_if_no_topic_arn_is_found(
    mock_logger, _mock_session, mock_a11y_report_class
):
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
