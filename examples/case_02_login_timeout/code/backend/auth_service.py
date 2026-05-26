def login(username, password):
    user = query_user(username)
    token = password_provider.verify(username, password)
    return {"token": token, "user": user}
