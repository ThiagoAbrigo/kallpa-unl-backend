"""Utility functions for standardized responses"""

def success_response(msg, data=None, origen="db", status_code=200):
    """Create a standardized success response"""
    response = {
        "status": "ok",
        "origen": origen,
        "msg": msg
    }
    if data is not None:
        response["data"] = data
    return response, status_code


def error_response(msg, status_code=400, origen="db"):
    """Create a standardized error response"""
    return {
        "status": "error",
        "origen": origen,
        "msg": msg
    }, status_code


def validation_error_response(errors, mensaje="Error de validación"):
    """Create a validation error response"""
    return {
        "status": "error",
        "origen": "validation",
        "msg": mensaje,
        "errors": errors
    }, 422
