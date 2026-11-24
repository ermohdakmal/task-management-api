def create_task(client, headers, title="First task", status="todo", priority="high"):
    return client.post(
        "/tasks",
        headers=headers,
        json={"title": title, "status": status, "priority": priority},
    )


def test_create_task(client, auth_headers):
    response = create_task(client, auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "First task"
    assert body["status"] == "todo"
    assert body["priority"] == "high"


def test_list_tasks(client, auth_headers):
    create_task(client, auth_headers, "Alpha")
    create_task(client, auth_headers, "Beta", "done", "low")

    response = client.get("/tasks?limit=10&offset=0", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tasks_filters_status_priority_and_search(client, auth_headers):
    create_task(client, auth_headers, "Pay bills", "todo", "high")
    create_task(client, auth_headers, "Pay taxes", "done", "low")

    response = client.get(
        "/tasks",
        params={"status": "todo", "priority": "high", "search": "bills"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Pay bills"


def test_get_update_and_delete_task(client, auth_headers):
    created = create_task(client, auth_headers)
    task_id = created.json()["id"]

    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 200

    update_response = client.patch(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated task", "status": "in_progress", "description": None},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated task"
    assert update_response.json()["status"] == "in_progress"
    assert update_response.json()["description"] is None

    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404


def test_user_cannot_read_another_users_task(client):
    register_user(client, "owner@example.com")
    owner_login = login_user(client, "owner@example.com")
    owner_headers = {"Authorization": f"Bearer {owner_login['access_token']}"}
    created = create_task(client, owner_headers)

    register_user(client, "other@example.com")
    other_login = login_user(client, "other@example.com")
    other_headers = {"Authorization": f"Bearer {other_login['access_token']}"}
    task_id = created.json()["id"]

    assert client.get(f"/tasks/{task_id}", headers=other_headers).status_code == 404


def test_user_cannot_update_or_delete_another_users_task(client):
    register_user(client, "owner2@example.com")
    owner_headers = bearer_headers(login_user(client, "owner2@example.com"))
    created = create_task(client, owner_headers)
    task_id = created.json()["id"]

    register_user(client, "other2@example.com")
    other_headers = bearer_headers(login_user(client, "other2@example.com"))

    assert client.patch(
        f"/tasks/{task_id}",
        headers=other_headers,
        json={"title": "Unauthorized"},
    ).status_code == 404
    assert client.delete(f"/tasks/{task_id}", headers=other_headers).status_code == 404


def register_user(client, email):
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "strong-password"},
    )
    assert response.status_code == 201


def login_user(client, email):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "strong-password"},
    )
    assert response.status_code == 200
    return response.json()


def bearer_headers(token_response):
    return {"Authorization": f"Bearer {token_response['access_token']}"}
