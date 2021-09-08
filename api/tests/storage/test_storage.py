from storage import storage
from unittest.mock import MagicMock, patch


def load_fixture(name):
    fixture = open(f"tests/storage/fixtures/{name}", "r")
    return fixture.read()


def mock_record():
    mock_record = MagicMock()
    mock_record.s3.bucket.name = "bucket_name"
    mock_record.s3.object.key = "key"
    return mock_record


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
    mock_log.error.assert_called_once_with("Error downloading key from bucket_name")


@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_store_with_not_json(mock_get_object, mock_log):
    mock_get_object.return_value = load_fixture("not_json.txt")
    assert storage.store(mock_record()) is False
    mock_log.error.assert_called_once_with("Error decoding key from bucket_name")


@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_store_with_empty_json(mock_get_object, mock_log):
    mock_get_object.return_value = load_fixture("empty.json")
    assert storage.store(mock_record()) is False
    mock_log.error.assert_called_once_with("Error decoding key from bucket_name")


@patch("storage.storage.db_session")
@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_store_with_scan_missing(mock_get_object, mock_log, mock_session):
    mock_session().query().options().get.return_value = None
    mock_get_object.return_value = load_fixture("axe_core_report.json")
    assert storage.store(mock_record()) is False
    mock_log.error.assert_called_once_with("Scan ID: scan_id could not be found")


@patch("storage.storage.db_session")
@patch("storage.storage.log")
@patch("storage.storage.get_object")
def test_store_with_scan_type_missing(mock_get_object, mock_log, mock_session):
    mock_scan = MagicMock()
    mock_scan.id = "scan_id"
    mock_scan.scan_type.name = "unknown_type_name"
    mock_session().query().options().get.return_value = mock_scan
    mock_get_object.return_value = load_fixture("axe_core_report.json")
    assert storage.store(mock_record()) is False
    mock_log.error.assert_called_once_with("Error storing scan_id with type unknown_type_name")


@patch("storage.storage.db_session")
@patch("storage.storage.log")
@patch("storage.storage.get_object")
@patch("storage.storage.store_axe_core_record")
def test_store_with_scan_type_as_axe_core(mock_store_axe_core, mock_get_object, mock_log, mock_session):
    mock_scan = MagicMock()
    mock_scan.id = "scan_id"
    mock_scan.scan_type.name = "axe_core"
    mock_store_axe_core.return_value = True
    mock_session().query().options().get.return_value = mock_scan
    mock_get_object.return_value = load_fixture("axe_core_report.json")
    assert storage.store(mock_record()) is True
    mock_store_axe_core.assert_called_once()
