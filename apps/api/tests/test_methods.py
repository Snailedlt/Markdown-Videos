from fastapi.testclient import TestClient
import pytest
import requests

from . import data_for_testing
from src import util
from main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "url, expected_video_id",
    data_for_testing.active_youtube_array_url_formats,
)
def test_get_youtube_video_id_by_valid_url(url, expected_video_id):
    assert util.get_video_id_by_url(url, util.URL_Regex.YOUTUBE) == expected_video_id

    # Test if the urls are valid with the expected video id
    url_input_response = requests.get(f"https://youtu.be/{expected_video_id}")
    assert url_input_response.status_code == 200


@pytest.mark.parametrize(
    "url, expected_video_id",
    data_for_testing.active_vimeo_array_url_formats,
)
def test_get_vimeo_video_id_by_valid_url(url, expected_video_id):
    assert util.get_video_id_by_url(url, util.URL_Regex.VIMEO) == expected_video_id

    # -- NOT WORKING AS OF 2024.08.22 with status_code 429 (Too Many Requests) -- #
    # Test if the urls are valid with the expected video id
    # url_input_response = requests.get(f"https://vimeo.com/{expected_video_id}")
    # assert url_input_response.status_code == 200
