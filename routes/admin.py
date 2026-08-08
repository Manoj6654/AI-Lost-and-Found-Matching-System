from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.models import db, User, Item, Match, Claim, Notification

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as Admin.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_lost = Item.query.filter_by(type='lost').count()
    total_found = Item.query.filter_by(type='found').count()
    total_matches = Match.query.count()
    pending_claims = Claim.query.filter_by(status='pending').count()
    resolved_cases = Item.query.filter_by(status='resolved').count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_claims = Claim.query.order_by(Claim.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_lost=total_lost,
        total_found=total_found,
        total_matches=total_matches,
        pending_claims=pending_claims,
        resolved_cases=resolved_cases,
        recent_users=recent_users,
        recent_claims=recent_claims
    )

@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin and User.query.filter_by(role='admin').count() <= 1:
        flash('Cannot delete the sole administrator account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} ({user.email}) deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/items')
@admin_required
def manage_items():
    item_type = request.args.get('type', '')
    status = request.args.get('status', '')

    query = Item.query
    if item_type:
        query = query.filter_by(type=item_type)
    if status:
        query = query.filter_by(status=status)

    items = query.order_by(Item.created_at.desc()).all()
    return render_template('admin/items.html', items=items, current_type=item_type, current_status=status)

@admin_bp.route('/item/<int:item_id>/resolve', methods=['POST'])
@admin_required
def resolve_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.status = 'resolved'
    db.session.commit()
    flash(f'Item #{item.id} ({item.item_name}) marked as resolved.', 'success')
    return redirect(url_for('admin.manage_items'))

@admin_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@admin_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Item #{item.id} deleted.', 'info')
    return redirect(url_for('admin.manage_items'))

@admin_bp.route('/matches')
@admin_required
def manage_matches():
    matches = Match.query.order_by(Match.match_score.desc()).all()
    return render_template('admin/matches.html', matches=matches)

@admin_bp.route('/claims')
@admin_required
def manage_claims():
    claims = Claim.query.order_by(Claim.created_at.desc()).all()
    return render_template('admin/claims.html', claims=claims)

@admin_bp.route('/claim/<int:claim_id>/approve', methods=['POST'])
@admin_required
def approve_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    claim.status = 'approved'
    
    match = claim.match
    match.status = 'resolved'
    match.lost_item.status = 'resolved'
    match.found_item.status = 'resolved'

    lost_owner = match.lost_item.owner
    found_reporter = match.found_item.owner
    claimant = claim.claimant

    # Send Notification to Claimant with contact details
    db.session.add(Notification(
        user_id=claimant.id,
        match_id=match.id,
        message=f"Your claim for '{match.lost_item.item_name}' was APPROVED! Contact the other party: Name: {found_reporter.name}, Email: {found_reporter.email}, Phone: {found_reporter.phone}."
    ))

    # Send Notification to Found Item Reporter
    db.session.add(Notification(
        user_id=found_reporter.id,
        match_id=match.id,
        message=f"Claim approved for item '{match.found_item.item_name}'! Contact claimant: Name: {claimant.name}, Email: {claimant.email}, Phone: {claimant.phone}."
    ))

    db.session.commit()
    flash('Claim approved! Item status set to resolved and contact info shared securely with both parties.', 'success')
    return redirect(url_for('admin.manage_claims'))

@admin_bp.route('/claim/<int:claim_id>/reject', methods=['POST'])
@admin_required
def reject_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    claim.status = 'rejected'
    claim.match.status = 'pending'

    db.session.add(Notification(
        user_id=claim.claimant_id,
        match_id=claim.match_id,
        message=f"Your claim request for '{claim.match.lost_item.item_name}' was reviewed and REJECTED due to insufficient ownership verification."
    ))

    db.session.commit()
    flash('Claim request rejected.', 'warning')
    return redirect(url_for('admin.manage_claims'))
