from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('Item', backref='owner', lazy=True, cascade='all, delete-orphan')
    claims = db.relationship('Claim', backref='claimant', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'lost' or 'found'
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(50), nullable=True)
    brand = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active') # 'active', 'claimed', 'resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    lost_matches = db.relationship('Match', foreign_keys='Match.lost_item_id', backref='lost_item', lazy=True, cascade='all, delete-orphan')
    found_matches = db.relationship('Match', foreign_keys='Match.found_item_id', backref='found_item', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Item #{self.id} {self.type.upper()}: {self.item_name}>'


class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False) # 0.0 to 100.0
    match_reason = db.Column(db.Text, nullable=False) # JSON formatted reasons & breakdown
    status = db.Column(db.String(20), nullable=False, default='pending') # 'pending', 'claimed', 'resolved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    claims = db.relationship('Claim', backref='match', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='match', lazy=True)

    @property
    def badge_class(self):
        if self.match_score >= 90.0:
            return 'bg-success'
        elif self.match_score >= 75.0:
            return 'bg-info text-dark'
        elif self.match_score >= 50.0:
            return 'bg-warning text-dark'
        else:
            return 'bg-secondary'

    @property
    def badge_label(self):
        if self.match_score >= 90.0:
            return 'Very High Match'
        elif self.match_score >= 75.0:
            return 'High Match'
        elif self.match_score >= 50.0:
            return 'Possible Match'
        else:
            return 'Low Match'

    def get_reasons_list(self):
        try:
            return json.loads(self.match_reason)
        except Exception:
            return [self.match_reason]

    def __repr__(self):
        return f'<Match #{self.id}: Lost #{self.lost_item_id} vs Found #{self.found_item_id} ({self.match_score:.1f}%)>'


class Claim(db.Model):
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Claim #{self.id} for Match #{self.match_id} by User #{self.claimant_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification #{self.id} for User #{self.user_id}>'
