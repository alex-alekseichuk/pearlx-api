"""Unit tests for Organizations API."""
import os

import pytest


@pytest.fixture(scope="function")
def organization_record(client):
    organization_record = {}
    yield organization_record
    if "organization_id" in organization_record:
        client.delete(f"/api/v1/organizations/{organization_record['organization_id']}")


def test_organizations(client, organization_record):
    # Login test user
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": os.environ["ADMIN_EMAIL"],
            "password": os.environ["ADMIN_PASSWORD"],
        },
    )
    assert response.status_code == 200

    token = response.json["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test GET many
    response = client.get("/api/v1/organizations", headers=headers)
    assert response.status_code == 200
    records_num = len(response.json)

    # Test POST
    response = client.post(
        "/api/v1/organizations",
        json={"name": "Cisforce", "address": "Ireland", "phone": "+79049264772"},
        headers=headers,
    )
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["name"] == "Cisforce"
    assert response.json["address"] == "Ireland"
    assert response.json["phone"] == "+79049264772"

    organization_id = response.json["id"]
    organization_record["organization_id"] = organization_id

    # Test GET many after creating
    response = client.get("/api/v1/organizations", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == records_num + 1

    # Test PUT
    response = client.put(
        f"/api/v1/organizations/{organization_id}",
        json={"name": "Cisforce Inc."},
        headers=headers,
    )
    assert response.status_code == 200

    # Test GET one after updating
    response = client.get(f"/api/v1/organizations/{organization_id}", headers=headers)
    assert response.status_code == 200
    assert response.json["id"] == organization_id
    assert response.json["name"] == "Cisforce Inc."
    assert response.json["address"] == "Ireland"
    assert response.json["phone"] == "+79049264772"

    # Test DELETE
    response = client.delete(f"/api/v1/organizations/{organization_id}", headers=headers)
    assert response.status_code == 204

    # Test GET many after deletion
    response = client.get("/api/v1/organizations", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == records_num

    # Logout test user
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 204
