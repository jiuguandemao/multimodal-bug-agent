def require_permission(user, permission):
    if permission not in user.permissions:
        return False
    return True
