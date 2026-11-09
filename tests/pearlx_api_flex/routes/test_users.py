"""Unit tests for Users API."""
import os


def test_users(app, client, smtpd):
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

    # get initial number of users
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    init_users_num = len(response.json)

    # Get any organization
    response = client.get("/api/v1/organizations", headers=headers)
    assert response.status_code == 200

    # Register test user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "firstname": "test_user",
            "lastname": "test_user",
            "email": "test_user@gmail.com",
            "password": "Test_password1",
            "organization_id": response.json[0]["id"],
        },
    )
    assert response.status_code == 201

    # Test GET many
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    records_num = len(response.json)
    assert records_num == init_users_num + 1

    for user in response.json:
        user_id = user["id"]
        user_email = user["email"]

        if user_email == "test_user@gmail.com":
            break

    # Test PATCH
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"firstname": "Ilya"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["firstname"] == "Ilya"
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"lastname": "Test user"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["lastname"] == "Test user"
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"firstname": "Ilya Valerevich", "lastname": "Zhukov"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["firstname"] == "Ilya Valerevich"
    assert response.json["lastname"] == "Zhukov"
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"firstname": "Test", "lastname": "Test", "enabled": True},
        headers=headers,
    )
    assert response.status_code == 409

    # Test GET one after updating
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json["id"] == user_id
    assert response.json["firstname"] == "Ilya Valerevich"
    assert response.json["lastname"] == "Zhukov"
    assert response.json["email"] == user_email

    # Test Enable
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.json["enabled"] is True
    response = client.post(
        f"/api/v1/users/{user_id}/enable",
        json={"enabled": False},
        headers=headers,
    )
    assert response.status_code == 200
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.json["enabled"] is False
    response = client.post(
        f"/api/v1/users/{user_id}/enable",
        json={"enabled": True},
        headers=headers,
    )
    assert response.status_code == 200
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.json["enabled"] is True
    response = client.post(
        f"/api/v1/users/{user_id}/enable",
        json={"enabled": True, "firstname": "Test name"},
        headers=headers,
    )
    assert response.status_code == 409
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.json["enabled"] is True

    # Test DELETE
    response = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 204

    # Test GET many after deletion
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    records_num = len(response.json)
    assert records_num == init_users_num

    # Logout test user
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 204
