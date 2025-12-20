def success_response(msg, data=None, status="ok"):
    return {
        "status": status,
        "msg": msg,
        "data": data
    }

def error_response(msg, status="error", data=None):
    return {
        "status": status,
        "msg": msg,
        "data": data
    }
