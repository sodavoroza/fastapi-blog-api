import pytest
from src.services.s3_service import upload_image_to_s3

@pytest.mark.asyncio
async def test_upload_image_to_s3(mocker):
    mock_boto = mocker.patch("src.services.s3_service.boto3.client", autospec=True)
    mock_client = mock_boto.return_value
    mock_client.put_object.return_value = {}
    result = upload_image_to_s3(b"fake_jpeg_data", "myphoto.jpg")
    mock_client.put_object.assert_called_once()
    assert "myphoto.jpg" in result
    assert "http" in result
