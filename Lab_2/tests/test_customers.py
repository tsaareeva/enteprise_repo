class TestCustomers:
    def test_create(self, client, admin_token):
        r = client.post("/api/v1/customers", json={
            "first_name": "J", "last_name": "D", "email": "j@e.com"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert r.json()["first_name"] == "J"

    def test_get_one(self, client, user_token, customer):
        r = client.get(f"/api/v1/customers/{customer['id']}", headers={"Authorization": f"Bearer {user_token}"})
        assert r.status_code == 200
        assert r.json()["id"] == customer["id"]

    def test_update(self, client, admin_token, customer):
        r = client.put(f"/api/v1/customers/{customer['id']}", json={
            "first_name": "Up", "last_name": "Nm", "email": "up@e.com"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert r.json()["first_name"] == "Up"

    def test_delete(self, client, admin_token, customer):
        r = client.delete(f"/api/v1/customers/{customer['id']}", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_not_found(self, client, user_token):
        r = client.get("/api/v1/customers/99999", headers={"Authorization": f"Bearer {user_token}"})
        assert r.status_code == 404