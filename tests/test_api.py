def register_and_login(client, username="tester"):
    client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "strong-pass-123",
    })
    response = client.post("/auth/login", data={
        "username": username,
        "password": "strong-pass-123",
    })
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_register_login_and_create_task(client):
    headers = register_and_login(client)
    response = client.post("/tasks", headers=headers, json={
        "title": "Prepare EPAM application",
        "description": "Finish a Python portfolio project",
        "priority": "high",
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Prepare EPAM application"
    assert response.json()["status"] == "todo"


def test_filter_tasks_by_status(client):
    headers = register_and_login(client)
    client.post("/tasks", headers=headers, json={"title": "First task"})
    client.post("/tasks", headers=headers, json={"title": "Second task", "status": "done"})
    response = client.get("/tasks?status=done", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Second task"


def test_users_cannot_see_each_others_tasks(client):
    headers_one = register_and_login(client, "alice")
    headers_two = register_and_login(client, "bob")
    created = client.post("/tasks", headers=headers_one, json={"title": "Private task"})
    task_id = created.json()["id"]
    response = client.get(f"/tasks/{task_id}", headers=headers_two)
    assert response.status_code == 404


def test_update_and_delete_task(client):
    headers = register_and_login(client)
    created = client.post("/tasks", headers=headers, json={"title": "Draft"})
    task_id = created.json()["id"]

    updated = client.patch(f"/tasks/{task_id}", headers=headers, json={"status": "done"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    deleted = client.delete(f"/tasks/{task_id}", headers=headers)
    assert deleted.status_code == 204
