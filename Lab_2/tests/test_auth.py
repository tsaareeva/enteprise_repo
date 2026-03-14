class TestAuth:
    def test_register(self, client):
        r = client.post("/api/auth/register", json={"username": "x", "password": "p123"})
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_ok(self, client):
        client.post("/api/auth/register", json={"username": "x", "password": "p123"})
        r = client.post("/api/auth/login", data={"username": "x", "password": "p123"})
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_bad_pass(self, client):
        client.post("/api/auth/register", json={"username": "x", "password": "p123"})
        r = client.post("/api/auth/login", data={"username": "x", "password": "wrong"})
        assert r.status_code == 401

    def test_login_bad_user(self, client):
        r = client.post("/api/auth/login", data={"username": "no", "password": "p123"})
        assert r.status_code == 401