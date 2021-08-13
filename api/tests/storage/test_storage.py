from storage import storage
from unittest.mock import MagicMock, patch


@patch("storage.storage.log")
@patch("storage.storage.boto3")
def test_get_object(mock_boto, mock_log):
    mock_record = MagicMock()
    mock_record.s3.bucket.name = "bucket_name"
    mock_record.s3.object.key = "key"

    mock_client = MagicMock()
    mock_client.Object.return_value.get.return_value.__getitem__.return_value.read.return_value = (
        "body"
    )

    mock_boto.resource.return_value = mock_client

    assert storage.get_object(mock_record) == "body"
    mock_client.Object.assert_called_once_with("bucket_name", "key")
    mock_client.Object().get().__getitem__.assert_called_once_with("Body")
    mock_log.info.assert_called_once_with(
        "Downloaded key from bucket_name with length 4"
    )


@patch("storage.storage.log")
@patch("storage.storage.boto3")
def test_get_object_catch_exception(mock_boto, mock_log):
    mock_record = MagicMock()
    mock_record.s3.bucket.name = "bucket_name"
    mock_record.s3.object.key = "key"

    mock_object = MagicMock()
    mock_object.get.side_effect = Exception

    mock_client = MagicMock()
    mock_client.Object.return_value = mock_object

    mock_boto.resource.return_value = mock_client

    assert storage.get_object(mock_record) is False
    mock_log.error.assert_called_once_with("Error downloading key from bucket_name")
