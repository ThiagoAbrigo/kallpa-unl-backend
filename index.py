from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config
from app.routes.routes import routes_bp

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return "API Flask - Kallpa Backendd"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)