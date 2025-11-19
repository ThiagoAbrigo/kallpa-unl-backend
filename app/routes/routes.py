from flask import Blueprint

routes_bp = Blueprint('routes', __name__)

@routes_bp.get("/test")
def test():
    return {"message": "COnfrimaaaaa bebe!"}