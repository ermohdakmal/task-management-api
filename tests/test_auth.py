def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "strong-password"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert "hashed_password" not in response.json()


def test_register_duplicate_email(client):
    payload = {"email": "duplicate@example.com", "password": "strong-password"}
    assert client.post("/auth/register", json=payload).status_code == 201

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert "detail" in response.json()


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "strong-password"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "strong-password"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "strong-password"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_me_returns_current_user(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
