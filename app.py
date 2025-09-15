import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()
db = SQLAlchemy()
def create_app():
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =
os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "dev-secret")
app.config["JSON_SORT_KEYS"] = False
# CORS
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*")}})
# init
db.init_app(app)
JWTManager(app)
# blueprints
from routes.auth import auth_bp
from routes.events import events_bp
from routes.exports import export_bp
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(events_bp, url_prefix="/api")
app.register_blueprint(export_bp, url_prefix="/api/export")
@app.get("/")
2
def root():
return jsonify(ok=True, service="Online Voting Flask Backend",
version="1.0.0")
with app.app_context():
from routes.models import init_db, seed_admin
init_db()
seed_admin()
return app
if __name__ == "__main__":
app = create_app()
port = int(os.getenv("FLASK_RUN_PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG",
"true").lower()=="true")