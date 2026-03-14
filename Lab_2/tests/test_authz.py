class TestAuthz:
    def test_user_no_write(self, client, user_token):
        r = client.post("/api/v1/customers", json={
            "first_name": "T", "last_name": "U", "email": "t@e.com"
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert r.status_code == 403

    def test_admin_write(self, client, admin_token):
        r = client.post("/api/v1/customers", json={
            "first_name": "A", "last_name": "D", "email": "a@e.com"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_no_token(self, client):
        r = client.get("/api/v1/customers")
        assert r.status_code == 401