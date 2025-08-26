from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_customer():
    response = client.post("/customers/", json={
        "name": "Test", "username": "testuser", "first_name": "Test", "last_name": "User",
        "address_postal_code": "12345", "address_city": "City", "profile_first_name": "Prof",
        "profile_last_name": "User", "company_name": "Comp"
    }, headers={"x-api-key": "secret_key"})
    assert response.status_code == 200
    assert "id" in response.json()

def test_read_customers():
    response = client.get("/customers/", headers={"x-api-key": "secret_key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_customer():
    # Assume created from previous, but for isolation, create first
    create_resp = client.post("/customers/", json={
        "name": "Test2", "username": "test2", "first_name": "T", "last_name": "U",
        "address_postal_code": "123", "address_city": "C", "profile_first_name": "P",
        "profile_last_name": "U", "company_name": "C"
    }, headers={"x-api-key": "secret_key"})
    id = create_resp.json()["id"]
    response = client.get(f"/customers/{id}", headers={"x-api-key": "secret_key"})
    assert response.status_code == 200
    assert response.json()["id"] == id

def test_update_customer():
    create_resp = client.post("/customers/", json={
        "name": "Test3", "username": "test3", "first_name": "T", "last_name": "U",
        "address_postal_code": "123", "address_city": "C", "profile_first_name": "P",
        "profile_last_name": "U", "company_name": "C"
    }, headers={"x-api-key": "secret_key"})
    id = create_resp.json()["id"]
    response = client.put(f"/customers/{id}", json={
        "name": "Updated", "username": "updated", "first_name": "U", "last_name": "D",
        "address_postal_code": "456", "address_city": "T", "profile_first_name": "Up",
        "profile_last_name": "Da", "company_name": "UpC"
    }, headers={"x-api-key": "secret_key"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"

def test_delete_customer():
    create_resp = client.post("/customers/", json={
        "name": "Test4", "username": "test4", "first_name": "T", "last_name": "U",
        "address_postal_code": "123", "address_city": "C", "profile_first_name": "P",
        "profile_last_name": "U", "company_name": "C"
    }, headers={"x-api-key": "secret_key"})
    id = create_resp.json()["id"]
    response = client.delete(f"/customers/{id}", headers={"x-api-key": "secret_key"})
    assert response.status_code == 200
    get_resp = client.get(f"/customers/{id}", headers={"x-api-key": "secret_key"})
    assert get_resp.status_code == 404