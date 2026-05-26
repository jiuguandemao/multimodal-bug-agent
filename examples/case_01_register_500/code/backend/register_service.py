def register_user(payload):
    username = payload.get("username")
    password = payload.get("password")
    birthday = payload["birthday"]
    if not username or not password:
        raise ValueError("username and password required")
    return {"id": 1, "username": username, "birthday": birthday}
