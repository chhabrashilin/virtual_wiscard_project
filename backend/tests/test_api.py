"""End-to-end API tests covering the core product loop and guards."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"


def test_login_success(client):
    resp = client.post(
        "/api/auth/login", data={"username": "jdoe", "password": "password123"}
    )
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["user"]["netid"] == "jdoe"


def test_login_bad_password(client):
    resp = client.post(
        "/api/auth/login", data={"username": "jdoe", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_user(client, auth_header):
    resp = client.get("/api/auth/me", headers=auth_header("jdoe", "password123"))
    assert resp.status_code == 200
    assert resp.json()["student_id"] == "12345678"


def test_get_my_card(client, auth_header):
    resp = client.get("/api/cards/my-card", headers=auth_header("jdoe", "password123"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "John Doe"
    assert body["balances"]["dining"] == 50.0


def test_generate_qr_then_verify_access(client, auth_header):
    """The product's core loop: student generates a token, operator verifies it."""
    headers = auth_header("jdoe", "password123")
    gen = client.post("/api/cards/generate-qr", headers=headers)
    assert gen.status_code == 200
    token = gen.json()["token"]
    assert gen.json()["qr_code"].startswith("data:image/png;base64,")

    # Operator verifies (no auth required on the scanner endpoint)
    verify = client.post(
        "/api/services/access",
        json={"token": token, "service_type": "dining", "action": "entry"},
    )
    assert verify.status_code == 200
    assert verify.json()["success"] is True
    assert verify.json()["user"]["student_id"] == "12345678"


def test_generate_qr_expires_at_is_utc(client, auth_header):
    """expires_at must be UTC-marked so the browser countdown isn't off by the tz offset."""
    headers = auth_header("jdoe", "password123")
    gen = client.post("/api/cards/generate-qr", headers=headers)
    assert gen.status_code == 200
    assert gen.json()["expires_at"].endswith("Z")


def test_verify_invalid_token(client):
    resp = client.post(
        "/api/services/access",
        json={"token": "not-a-real-token", "service_type": "dining"},
    )
    assert resp.status_code == 401


def test_dining_spend_and_history(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post("/api/services/dining/use", json={"amount": 20}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["new_balance"] == 30.0

    hist = client.get("/api/cards/transaction-history", headers=headers)
    assert hist.status_code == 200
    assert any(t["service_type"] == "dining" for t in hist.json()["transactions"])


def test_dining_insufficient_balance(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post("/api/services/dining/use", json={"amount": 99}, headers=headers)
    assert resp.status_code == 400


def test_dining_rejects_negative(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post("/api/services/dining/use", json={"amount": -5}, headers=headers)
    assert resp.status_code == 422


def test_print_spend(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post("/api/services/print/use", json={"amount": 4}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["new_balance"] == 6.0


def test_admin_guard_blocks_student(client, auth_header):
    resp = client.get("/api/admin/users", headers=auth_header("jdoe", "password123"))
    assert resp.status_code == 403


def test_admin_can_list_users(client, auth_header):
    resp = client.get("/api/admin/users", headers=auth_header("admin", "admin123"))
    assert resp.status_code == 200
    netids = {u["netid"] for u in resp.json()["users"]}
    assert {"admin", "jdoe"} <= netids


def test_admin_rejects_negative_balance(client, auth_header):
    headers = auth_header("admin", "admin123")
    resp = client.post(
        "/api/admin/balances",
        json={"user_id": 2, "service_type": "dining", "balance": -10},
        headers=headers,
    )
    assert resp.status_code == 422


def test_blockchain_binary_conversion(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post("/api/blockchain/student-id-to-binary", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["binary"] == bin(12345678)[2:]


# --------------------------------------------------------------------------- #
# Expanded Wiscard capabilities
# --------------------------------------------------------------------------- #

def test_my_card_includes_new_sections(client, auth_header):
    resp = client.get("/api/cards/my-card", headers=auth_header("jdoe", "password123"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_frozen"] is False
    assert body["meal_plan"]["swipes_remaining"] == 3
    assert body["transit_pass"]["status"] == "active"
    assert any(p["resource_key"] == "recwell" for p in body["permissions"])
    assert body["balances"]["wiscard_cash"] == 40.0


def test_wiscard_cash_spend(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post(
        "/api/services/wiscard-cash/use",
        json={"amount": 15, "vendor": "Vending Machine"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["new_balance"] == 25.0


def test_meal_swipe_decrements(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.post("/api/services/dining/swipe", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["swipes_remaining"] == 2


def test_transit_pass_status(client, auth_header):
    headers = auth_header("jdoe", "password123")
    resp = client.get("/api/services/transit/pass", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_door_access_with_permission(client, auth_header):
    token = client.post(
        "/api/cards/generate-qr", headers=auth_header("jdoe", "password123")
    ).json()["token"]
    resp = client.post(
        "/api/services/access",
        json={"token": token, "service_type": "door", "resource": "recwell"},
    )
    assert resp.status_code == 200
    assert resp.json()["resource_name"] == "RecWell"


def test_door_access_denied_without_permission(client, auth_header):
    token = client.post(
        "/api/cards/generate-qr", headers=auth_header("jdoe", "password123")
    ).json()["token"]
    resp = client.post(
        "/api/services/access",
        json={"token": token, "service_type": "door", "resource": "chem_lab"},
    )
    assert resp.status_code == 403


def test_transit_tap_via_verifier(client, auth_header):
    token = client.post(
        "/api/cards/generate-qr", headers=auth_header("jdoe", "password123")
    ).json()["token"]
    resp = client.post(
        "/api/services/access",
        json={"token": token, "service_type": "transit", "action": "tap"},
    )
    assert resp.status_code == 200


def test_freeze_blocks_qr_then_unfreeze(client, auth_header):
    headers = auth_header("jdoe", "password123")
    assert client.post("/api/cards/freeze", headers=headers).json()["is_frozen"] is True
    blocked = client.post("/api/cards/generate-qr", headers=headers)
    assert blocked.status_code == 403
    assert client.post("/api/cards/unfreeze", headers=headers).json()["is_frozen"] is False
    assert client.post("/api/cards/generate-qr", headers=headers).status_code == 200


def test_frozen_card_token_rejected_at_gate(client, auth_header):
    headers = auth_header("jdoe", "password123")
    token = client.post("/api/cards/generate-qr", headers=headers).json()["token"]
    client.post("/api/cards/freeze", headers=headers)
    resp = client.post(
        "/api/services/access",
        json={"token": token, "service_type": "dining"},
    )
    assert resp.status_code == 401


def test_ticket_validate_single_use(client):
    first = client.post("/api/tickets/validate", json={"code": "TEST-TICKET-CODE"})
    assert first.status_code == 200
    assert first.json()["event_name"] == "Badgers vs. Gophers"
    # second scan should be rejected as already used
    second = client.post("/api/tickets/validate", json={"code": "TEST-TICKET-CODE"})
    assert second.status_code == 409


def test_my_tickets(client, auth_header):
    resp = client.get("/api/tickets", headers=auth_header("jdoe", "password123"))
    assert resp.status_code == 200
    assert len(resp.json()["tickets"]) == 1


def test_admin_grant_permission(client, auth_header):
    headers = auth_header("admin", "admin123")
    resp = client.post(
        "/api/admin/permissions",
        json={"user_id": 2, "resource_key": "chem_lab", "resource_name": "Chemistry Lab 301"},
        headers=headers,
    )
    assert resp.status_code == 200
