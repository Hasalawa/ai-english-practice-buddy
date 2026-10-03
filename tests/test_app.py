import json
import os
import sys
from unittest import mock

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as buddy


@pytest.fixture
def client():
    return buddy.app.test_client()


def fake_ollama(payload):
    resp = mock.Mock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"message": {"content": json.dumps(payload)}}
    return resp


def test_index_served(client):
    assert client.get("/").status_code == 200


def test_empty_sentence_rejected(client):
    assert client.post("/check", json={"sentence": "  "}).status_code == 400


def test_too_long_rejected(client):
    r = client.post("/check", json={"sentence": "a" * 501})
    assert r.status_code == 400


def test_successful_check(client):
    answer = {
        "is_correct": False,
        "corrected": "I went to university yesterday.",
        "explanation": "Yesterday is past, so use went.",
        "example": "She went home.",
        "better": "I went to uni yesterday.",
    }
    with mock.patch("app.requests.post", return_value=fake_ollama(answer)):
        r = client.post("/check", json={"sentence": "I am go to university yesterday."})
    body = r.get_json()
    assert r.status_code == 200
    assert body["is_correct"] is False
    assert body["corrected"] == "I went to university yesterday."


def test_ollama_down_returns_503(client):
    with mock.patch("app.requests.post", side_effect=requests.ConnectionError):
        r = client.post("/check", json={"sentence": "hello"})
    assert r.status_code == 503


def test_bad_model_output_returns_502(client):
    resp = mock.Mock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"message": {"content": "not json"}}
    with mock.patch("app.requests.post", return_value=resp):
        r = client.post("/check", json={"sentence": "hello"})
    assert r.status_code == 502
