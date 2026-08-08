from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import db, Match, Claim, Notification
from routes.user import login_required

claims_bp = Blueprint('claims', __name__)

@claims_bp.route('/match/<int:match_id>/claim', methods=['POST'])
@login_required
def submit_claim(match_id):
    match = Match.query.get_or_404(match_id)
    user_id = session['user_id']
    message = request.form.get('message', '').strip()

    if not message:
        flash('Please provide identifying details or proof of ownership in your claim message.', 'danger')
        return redirect(url_for('matches.match_detail', match_id=match.id))

    existing_claim = Claim.query.filter_by(match_id=match.id, claimant_id=user_id).first()
    if existing_claim:
        flash('You have already submitted a claim for this matched item.', 'warning')
        return redirect(url_for('matches.match_detail', match_id=match.id))

    # Create new Claim
    new_claim = Claim(
        match_id=match.id,
        claimant_id=user_id,
        message=message,
        status='pending'
    )
    
    # Update match status
    match.status = 'claimed'

    db.session.add(new_claim)
    
    # Notify Admin or opposite item owner
    opposite_owner_id = match.found_item.user_id if match.lost_item.user_id == user_id else match.lost_item.user_id
    db.session.add(Notification(
        user_id=opposite_owner_id,
        match_id=match.id,
        message=f"A user has submitted a claim request for the match between '{match.lost_item.item_name}' and '{match.found_item.item_name}'."
    ))

    db.session.commit()

    flash('Claim request submitted successfully! An administrator will review your claim details.', 'success')
    return redirect(url_for('claims.my_claims'))


@claims_bp.route('/my-claims')
@login_required
def my_claims():
    user_id = session['user_id']
    user_claims = Claim.query.filter_by(claimant_id=user_id).order_by(Claim.created_at.desc()).all()
    return render_template('claims.html', claims=user_claims)
