from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import db, Item, Match, Claim
from routes.user import login_required

matches_bp = Blueprint('matches', __name__)

@matches_bp.route('/matches')
@login_required
def match_results():
    item_id = request.args.get('item_id', type=int)
    min_score = request.args.get('min_score', default=40.0, type=float)
    
    target_item = None
    if item_id:
        target_item = Item.query.get(item_id)

    if target_item:
        if target_item.type == 'lost':
            matches = Match.query.filter(
                Match.lost_item_id == target_item.id,
                Match.match_score >= min_score
            ).order_by(Match.match_score.desc()).limit(5).all()
        else:
            matches = Match.query.filter(
                Match.found_item_id == target_item.id,
                Match.match_score >= min_score
            ).order_by(Match.match_score.desc()).limit(5).all()
    else:
        # Show matches involving current logged in user's items
        user_id = session.get('user_id')
        user_item_ids = [i.id for i in Item.query.filter_by(user_id=user_id).all()]
        
        if user_item_ids:
            matches = Match.query.filter(
                ((Match.lost_item_id.in_(user_item_ids)) | (Match.found_item_id.in_(user_item_ids))),
                Match.match_score >= min_score
            ).order_by(Match.match_score.desc()).all()
        else:
            matches = Match.query.filter(Match.match_score >= min_score).order_by(Match.match_score.desc()).limit(20).all()

    return render_template(
        'matches.html',
        matches=matches,
        target_item=target_item,
        min_score=min_score
    )


@matches_bp.route('/match/<int:match_id>')
@login_required
def match_detail(match_id):
    match = Match.query.get_or_404(match_id)
    user_id = session['user_id']
    
    # Check if user already submitted a claim for this match
    user_claim = Claim.query.filter_by(match_id=match.id, claimant_id=user_id).first()
    
    reasons = match.get_reasons_list()
    
    return render_template(
        'match_detail.html',
        match=match,
        reasons=reasons,
        user_claim=user_claim
    )


@matches_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')
