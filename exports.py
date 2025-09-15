from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from routes.models import Event, Candidate, Vote
export_bp = Blueprint("export", __name__)
def require_admin(identity):
return identity and identity.get("role") == "admin"
@export_bp.get("/json")
@jwt_required()
def export_json():
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
events = Event.query.all()
data = []
for e in events:
cands = Candidate.query.filter_by(event_id=e.id).all()
votes = Vote.query.filter_by(event_id=e.id).all()
data.append({
"event": {"id": e.id, "name": e.name, "startAt":
e.start_at.isoformat() if e.start_at else None, "endAt": e.end_at.isoformat()
if e.end_at else None, "isActive": e.is_active},
"candidates": [{"id": c.id, "name": c.name} for c in cands],
"votes": [{"userId": v.user_id, "candidateId": v.candidate_id,
"createdAt": v.created_at.isoformat()} for v in votes]
})
return jsonify({"exportedAt":
__import__("datetime").datetime.utcnow().isoformat(), "data": data})
@export_bp.get("/csv")
@jwt_required()
def export_csv():
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
import csv, io
output = io.StringIO()
writer = csv.writer(output)
10
writer.writerow(["eventId","eventName","candidateId","candidateName","votes","start","end","isevents = Event.query.all()
for e in events:
cands = Candidate.query.filter_by(event_id=e.id).all()
for c in cands:
vcount = Vote.query.filter_by(candidate_id=c.id).count()
writer.writerow([e.id, e.name, c.id, c.name, vcount, e.start_at
or "", e.end_at or "", "true" if e.is_active else "false"])
return Response(output.getvalue(), mimetype="text/csv",
headers={"Content-Disposition":"attachment; filename=events.csv"})