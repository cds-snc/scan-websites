import json
import os

from models.A11yReport import A11yReport
from models.A11yViolation import A11yViolation
from models.SecurityReport import SecurityReport
from models.SecurityViolation import SecurityViolation

from storage import storage
from unittest.mock import MagicMock, patch, call


def load_fixture(name):
    fixture = open(f"tests/storage/fixtures/{name}", "r")
    return fixture.read()


def mock_record(name="bucket_name"):
    return {"s3": {"bucket": {"name": name}, "object": {"key": "key"}}}


@patch("storage.storage.log")
@patch("storage.storage.get_session")
def test_get_object(mock_get_session, mock_log):
    mock_client = MagicMock()
    mock_client.Object.return_value.get.return_value.__getitem__.return_value.read.return_value = (
        "body"
    )

    mock_get_session.return_value.resource.return_value = mock_client

    assert storage.get_object(mock_record()) == "body"
    mock_client.Object.assert_called_once_with("bucket_name", "key")
    mock_client.Object().get().__getitem__.assert_called_once_with("Body")
    mock_log.info.assert_called_once_with(
        "Downloaded key from bucket_name with length 4"
    )


@patch("storage.storage.log")
@patch("storage.storage.get_session")
def test_get_object_catch_exception(mock_get_session, mock_log):
    mock_object = MagicMock()
    mock_object.get.side_effect = Exception

    mock_client = MagicMock()
    mock_client.Object.return_value = mock_object

    mock_get_session.return_value.resource.return_value = mock_client

    assert storage.get_object(mock_record()) is False
    mock_log.error.assert_has_calls([call("Error downloading key from bucket_name")])


@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_retrieve_and_route_with_not_json(mock_get_object, mock_log):
    mock_get_object.return_value = load_fixture("not_json.txt")
    assert storage.retrieve_and_route(mock_record()) is False
    mock_log.error.assert_called_once_with(
        "Error decoding key from bucket_name: Expecting value: line 1 column 1 (char 0)"
    )


@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_retrieve_and_route_with_empty_json(mock_get_object, mock_log):
    mock_get_object.return_value = load_fixture("empty.json")
    assert storage.retrieve_and_route(mock_record()) is False
    mock_log.error.assert_called_once_with("Unknown bucket bucket_name")


@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_retrieve_and_route_with_unknown_bucket(mock_get_object, mock_log):
    mock_get_object.return_value = load_fixture("axe_core_report.json")
    assert storage.retrieve_and_route(mock_record("unknown")) is False
    mock_log.error.assert_called_once_with("Unknown bucket unknown")


@patch("storage.storage.get_object")
@patch("storage.storage.store_axe_core_record")
@patch.dict(os.environ, {"AXE_CORE_REPORT_DATA_BUCKET": "axe_core"}, clear=True)
def test_retrieve_and_route_with_bucket_type_as_axe_core(
    mock_store_axe_core, mock_get_object
):
    mock_store_axe_core.return_value = True
    mock_get_object.return_value = load_fixture("axe_core_report.json")
    assert storage.retrieve_and_route(mock_record("axe_core")) is True
    mock_store_axe_core.assert_called_once()


@patch("storage.storage.db_session")
@patch.dict(os.environ, {"AXE_CORE_REPORT_DATA_BUCKET": "axe_core"}, clear=True)
def test_store_axe_core_record_returns_false_on_missing_record(mock_session):
    mock_session.query().get.return_value = None

    payload = json.loads(load_fixture("axe_core_report.json"))
    assert storage.store_axe_core_record(mock_session, payload) is False


def test_store_axe_core_record_updates_record(session, a11y_report_fixture):
    payload = json.loads(load_fixture("axe_core_report.json"))
    payload["id"] = a11y_report_fixture.id
    assert storage.store_axe_core_record(session, payload) is True
    session.refresh(a11y_report_fixture)
    assert a11y_report_fixture.summary == {
        "inapplicable": 72,
        "incomplete": 0,
        "passes": 12,
        "status": "completed",
        "violations": {"moderate": 2, "serious": 1, "total": 3},
    }


def test_store_axe_core_record_creates_violations(session, scan_fixture):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(a11y_report)
    session.commit()

    payload = json.loads(load_fixture("axe_core_report.json"))
    payload["id"] = a11y_report.id
    assert storage.store_axe_core_record(session, payload) is True
    violations = (
        session.query(A11yViolation)
        .filter(A11yViolation.a11y_report_id == a11y_report.id)
        .all()
    )
    assert len(violations) == 3


def test_sum_impact_empty():
    assert storage.sum_impact([]) == {}


def test_sum_impact_missing_impact():
    assert storage.sum_impact([{"foo": "bar"}]) == {}


def test_sum_impact_correct_impact():
    assert storage.sum_impact([{"impact": "impact_value"}]) == {"impact_value": 1}


@patch("storage.storage.get_object")
@patch("storage.storage.store_owasp_zap_record")
@patch.dict(os.environ, {"OWASP_ZAP_REPORT_DATA_BUCKET": "owasp_zap"}, clear=True)
def test_retrieve_and_route_with_bucket_type_as_owasp_zap(
    mock_store_owasp_zap, mock_get_object
):
    mock_store_owasp_zap.return_value = True
    mock_get_object.return_value = load_fixture("owasp_zap_report.json")
    assert storage.retrieve_and_route(mock_record("owasp_zap")) is True
    mock_store_owasp_zap.assert_called_once()


@patch("storage.storage.db_session")
@patch.dict(os.environ, {"OWASP_ZAP_REPORT_DATA_BUCKET": "owasp_zap"}, clear=True)
def test_store_owasp_zap_record_returns_false_on_missing_record(mock_session):
    mock_session.query().get.return_value = None
    payload = json.loads(load_fixture("owasp_zap_report.json"))
    assert storage.store_owasp_zap_record(mock_session, payload) is False


def test_store_owasp_zap_record_updates_record(session, security_report_fixture):
    payload = json.loads(load_fixture("owasp_zap_report.json"))
    payload["id"] = security_report_fixture.id
    assert storage.store_owasp_zap_record(session, payload) is True
    session.refresh(security_report_fixture)
    assert security_report_fixture.summary == {
        "status": "completed",
        "total": 116,
        "Low (Medium)": 76,
        "Informational (Low)": 40,
    }


def test_store_owasp_zap_record_creates_violations(session, scan_fixture):
    security_report = SecurityReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(security_report)
    session.commit()

    payload = json.loads(load_fixture("owasp_zap_report.json"))
    payload["id"] = security_report.id
    assert storage.store_owasp_zap_record(session, payload) is True
    violations = (
        session.query(SecurityViolation)
        .filter(SecurityViolation.security_report_id == security_report.id)
        .all()
    )
    assert len(violations) == 4
