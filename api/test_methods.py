from fastapi.testclient import TestClient
import pytest

from . import data_for_testing, util
from .main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "url, expected_video_id",
    data_for_testing.active_youtube_array_url_formats,
)
def test_get_youtube_video_id_by_valid_url(url, expected_video_id):
    assert util.get_video_id_by_url(url, util.URL_Regex.YOUTUBE) == expected_video_id


@pytest.mark.parametrize(
    "url, expected_video_id",
    data_for_testing.active_vimeo_array_url_formats,
)
def test_get_vimeo_video_id_by_valid_url(url, expected_video_id):
    assert util.get_video_id_by_url(url, util.URL_Regex.VIMEO) == expected_video_id
