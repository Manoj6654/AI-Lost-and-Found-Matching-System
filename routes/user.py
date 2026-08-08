from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.models import db, User, Item, Match, Notification

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # User's items stats
    my_lost_count = Item.query.filter_by(user_id=user_id, type='lost').count()
    my_found_count = Item.query.filter_by(user_id=user_id, type='found').count()
    
    # User item IDs
    user_item_ids = [item.id for item in user.items]
    
    # Matches involving user items
    if user_item_ids:
        possible_matches = Match.query.filter(
            ((Match.lost_item_id.in_(user_item_ids)) | (Match.found_item_id.in_(user_item_ids))),
            Match.match_score >= 50.0
        ).order_by(Match.match_score.desc()).all()
    else:
        possible_matches = []

    resolved_count = Item.query.filter_by(user_id=user_id, status='resolved').count()
    recent_reports = Item.query.filter_by(user_id=user_id).order_by(Item.created_at.desc()).limit(5).all()
    unread_notifications = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    # System-wide overall stats for dashboard header
    total_system_lost = Item.query.filter_by(type='lost').count()
    total_system_found = Item.query.filter_by(type='found').count()

    return render_template(
        'dashboard.html',
        user=user,
        my_lost_count=my_lost_count,
        my_found_count=my_found_count,
        possible_matches=possible_matches[:5],
        possible_matches_count=len(possible_matches),
        resolved_count=resolved_count,
        recent_reports=recent_reports,
        unread_notifications=unread_notifications,
        total_system_lost=total_system_lost,
        total_system_found=total_system_found
    )

@user_bp.route('/my-reports')
@login_required
def my_reports():
    user_id = session['user_id']
    items = Item.query.filter_by(user_id=user_id).order_by(Item.created_at.desc()).all()
    return render_template('my_reports.html', items=items)

@user_bp.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read when page is visited
    for n in notifs:
        n.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifs)
