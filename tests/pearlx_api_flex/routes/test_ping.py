"""Unit tests for Ping API."""


def test_ping(client):
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert "datetime" in response.json
    assert "method" in response.json
    assert "url" in response.json
