from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app import db
from routes.models import User, Admin
auth_bp = Blueprint("auth", __name__)
@auth_bp.post("/register")
def user_register():
4
data = request.get_json() or {}
required = ["name","email","phone","voterId","password"]
if any(k not in data or not data[k] for k in required):
return jsonify(error="Missing fields"), 400
if User.query.filter_by(voter_id=data["voterId"]).first():
return jsonify(error="Voter ID already exists"), 409
user = User(
voter_id=data["voterId"],
name=data["name"],
email=data["email"],
phone=data["phone"],
password_hash=generate_password_hash(data["password"]),
)
db.session.add(user)
db.session.commit()
return jsonify(ok=True, id=user.id)
@auth_bp.post("/login")
def user_login():
data = request.get_json() or {}
voter_id = data.get("voterId"); password = data.get("password")
if not voter_id or not password: return jsonify(error="Missing fields"),
400
user = User.query.filter_by(voter_id=voter_id).first()
if not user or not check_password_hash(user.password_hash, password):
return jsonify(error="Invalid credentials"), 401
token = create_access_token(
identity={"role":"user","id":user.id,"voterId":user.voter_id,"name":user.name},
expires_delta=timedelta(days=7),
)
return jsonify(token=token, user={
"id": user.id,
"voterId": user.voter_id,
"name": user.name,
"email": user.email,
"phone": user.phone,
"createdAt": user.created_at.isoformat()
})
@auth_bp.post("/admin/register")
def admin_register():
data = request.get_json() or {}
required = ["name","email","password"]
if any(k not in data or not data[k] for k in required):
return jsonify(error="Missing fields"), 400
if Admin.query.filter_by(email=data["email"]).first():
return jsonify(error="Admin already exists"), 409
admin = Admin(
name=data["name"],
email=data["email"],
5
password_hash=generate_password_hash(data["password"]),
)
db.session.add(admin)
db.session.commit()
return jsonify(ok=True, id=admin.id)
@auth_bp.post("/admin/login")
def admin_login():
data = request.get_json() or {}
email = data.get("email"); password = data.get("password")
if not email or not password: return jsonify(error="Missing fields"), 400
admin = Admin.query.filter_by(email=email).first()
if not admin or not check_password_hash(admin.password_hash, password):
return jsonify(error="Invalid credentials"), 401
token = create_access_token(
identity={"role":"admin","id":admin.id,"email":admin.email,"name":admin.name},
expires_delta=timedelta(days=7),
)
return jsonify(token=token, admin={
"id": admin.id,
"name": admin.name,
"email": admin.email,
"createdAt": admin.created_at.isoformat()
})
