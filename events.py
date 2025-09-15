from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from routes.models import Event, Candidate, Vote
events_bp = Blueprint("events", __name__)
@events_bp.get("/events")
def list_events():
events = Event.query.order_by(Event.id.desc()).all()
data = []
for e in events:
cands = Candidate.query.filter_by(event_id=e.id).all()
data.append({
"id": e.id,
"name": e.name,
"start_at": e.start_at.isoformat() if e.start_at else None,
"end_at": e.end_at.isoformat() if e.end_at else None,
"is_active": e.is_active,
6
"candidates": [{"id": c.id, "name": c.name} for c in cands]
})
return jsonify(data)
@events_bp.get("/events/active")
def active_event():
e = Event.query.filter_by(is_active=True).first()
if not e: return jsonify(None)
cands = Candidate.query.filter_by(event_id=e.id).all()
return jsonify({
"id": e.id,
"name": e.name,
"start_at": e.start_at.isoformat() if e.start_at else None,
"end_at": e.end_at.isoformat() if e.end_at else None,
"is_active": e.is_active,
"candidates": [{"id": c.id, "name": c.name} for c in cands]
})
# ------- Admin ops -------
def require_admin(identity):
return identity and identity.get("role") == "admin"
@events_bp.post("/admin/events")
@jwt_required()
def create_event():
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
data = request.get_json() or {}
name = data.get("name"); candidates = data.get("candidates", [])
if not name or not candidates: return jsonify(error="Missing name/
candidates"), 400
start = data.get("startAt"); end = data.get("endAt")
e = Event(name=name,
start_at=datetime.fromisoformat(start) if start else None,
end_at=datetime.fromisoformat(end) if end else None,
is_active=False)
db.session.add(e); db.session.flush()
for c in candidates:
nm = c["name"] if isinstance(c, dict) else str(c)
db.session.add(Candidate(event_id=e.id, name=nm))
db.session.commit()
return jsonify(ok=True, id=e.id)
@events_bp.patch("/admin/events/<int:ev_id>")
@jwt_required()
def patch_event(ev_id):
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
e = Event.query.get(ev_id)
if not e: return jsonify(error="Event not found"), 404
7
d = request.get_json() or {}
if "name" in d and d["name"]: e.name = d["name"]
if "startAt" in d: e.start_at = datetime.fromisoformat(d["startAt"]) if
d["startAt"] else None
if "endAt" in d: e.end_at = datetime.fromisoformat(d["endAt"]) if
d["endAt"] else None
db.session.commit()
return jsonify(ok=True)
@events_bp.delete("/admin/events/<int:ev_id>")
@jwt_required()
def delete_event(ev_id):
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
e = Event.query.get(ev_id)
if not e: return jsonify(error="Event not found"), 404
db.session.delete(e); db.session.commit()
return jsonify(ok=True)
@events_bp.post("/admin/events/<int:ev_id>/active")
@jwt_required()
def set_active(ev_id):
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
Event.query.update({Event.is_active: False})
e = Event.query.get(ev_id)
if not e: return jsonify(error="Event not found"), 404
e.is_active = True; db.session.commit()
return jsonify(ok=True)
@events_bp.post("/admin/events/<int:ev_id>/candidates")
@jwt_required()
def add_candidate(ev_id):
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
d = request.get_json() or {}
name = d.get("name");
if not name: return jsonify(error="Missing name"), 400
c = Candidate(event_id=ev_id, name=name)
db.session.add(c); db.session.commit()
return jsonify(ok=True, id=c.id)
@events_bp.delete("/admin/candidates/<int:cand_id>")
@jwt_required()
def remove_candidate(cand_id):
ident = get_jwt_identity()
if not require_admin(ident): return jsonify(error="Invalid role"), 403
c = Candidate.query.get(cand_id)
if not c: return jsonify(error="Not found"), 404
db.session.delete(c); db.session.commit()
return jsonify(ok=True)
8
# ------- Voting (user) -------
@events_bp.post("/events/<int:ev_id>/vote")
@jwt_required()
def vote(ev_id):
ident = get_jwt_identity()
if ident.get("role") != "user": return jsonify(error="Invalid role"), 403
user_id = ident.get("id")
data = request.get_json() or {}
cand_id = data.get("candidateId")
e = Event.query.get(ev_id)
if not e: return jsonify(error="Event not found"), 404
now = datetime.utcnow()
if e.start_at and now < e.start_at: return jsonify(error="Event not
started"), 400
if e.end_at and now > e.end_at: return jsonify(error="Event ended"), 400
cand = Candidate.query.filter_by(id=cand_id, event_id=ev_id).first()
if not cand: return jsonify(error="Invalid candidate"), 400
# one vote per (user,event)
if Vote.query.filter_by(user_id=user_id, event_id=ev_id).first():
return jsonify(error="Already voted in this event"), 409
v = Vote(user_id=user_id, event_id=ev_id, candidate_id=cand_id)
db.session.add(v); db.session.commit()
return jsonify(ok=True)
@events_bp.get("/events/<int:ev_id>/results")
def results(ev_id):
from sqlalchemy.sql import func
e = Event.query.get(ev_id)
if not e: return jsonify(error="Event not found"), 404
rows = db.session.query(
Candidate.id.label("candidateId"),
Candidate.name.label("candidateName"),
func.count(Vote.id).label("votes")
).join(Vote, Vote.candidate_id==Candidate.id, isouter=True).filter(
Candidate.event_id==ev_id
).group_by(Candidate.id).order_by(func.count(Vote.id).desc(),
Candidate.id.asc()).all()
total = sum([r.votes for r in rows])
return jsonify({
"event": {"id": e.id, "name": e.name, "startAt":
e.start_at.isoformat() if e.start_at else None, "endAt": e.end_at.isoformat()
if e.end_at else None},
"totalVotes": int(total),
"candidates": [{"candidateId": r.candidateId, "candidateName":
r.candidateName, "votes": int(r.votes)} for r in rows]
})
@events_bp.get("/events/<int:ev_id>/my-vote")
@jwt_required()
def my_vote(ev_id):
9
ident = get_jwt_identity()
if ident.get("role")!="user": return jsonify(error="Invalid role"), 403
v = Vote.query.filter_by(event_id=ev_id, user_id=ident.get("id")).first()
if not v: return jsonify(None)
return jsonify({"candidateId": v.candidate_id})