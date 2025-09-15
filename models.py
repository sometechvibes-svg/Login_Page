from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash
from app import db
class Admin(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(120), nullable=False)
email = db.Column(db.String(120), unique=True, nullable=False)
password_hash = db.Column(db.String(255), nullable=False)
created_at = db.Column(db.DateTime, default=datetime.utcnow,
nullable=False)
class User(db.Model):
id = db.Column(db.Integer, primary_key=True)
voter_id = db.Column(db.String(120), unique=True, nullable=False)
name = db.Column(db.String(120), nullable=False)
email = db.Column(db.String(120), nullable=False)
phone = db.Column(db.String(50), nullable=False)
password_hash = db.Column(db.String(255), nullable=False)
created_at = db.Column(db.DateTime, default=datetime.utcnow,
nullable=False)
class Event(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(200), nullable=False)
start_at = db.Column(db.DateTime, nullable=True)
3
end_at = db.Column(db.DateTime, nullable=True)
is_active = db.Column(db.Boolean, default=False, nullable=False)
class Candidate(db.Model):
id = db.Column(db.Integer, primary_key=True)
event_id = db.Column(db.Integer, db.ForeignKey("event.id",
ondelete="CASCADE"), nullable=False)
name = db.Column(db.String(200), nullable=False)
class Vote(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer, db.ForeignKey("user.id",
ondelete="CASCADE"), nullable=False)
event_id = db.Column(db.Integer, db.ForeignKey("event.id",
ondelete="CASCADE"), nullable=False)
candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id",
ondelete="CASCADE"), nullable=False)
created_at = db.Column(db.DateTime, default=datetime.utcnow,
nullable=False)
__table_args__ = (UniqueConstraint('user_id', 'event_id',
name='uq_user_event'),)
def init_db():
db.create_all()
def seed_admin():
if Admin.query.count() == 0:
admin = Admin(
name="Super Admin",
email="admin@example.com",
password_hash=generate_password_hash("admin123"),
)
db.session.add(admin)
db.session.commit()