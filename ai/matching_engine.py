import json
from datetime import datetime
from config import Config
from models.models import db, Item, Match, Notification
from ai.text_matching import calculate_text_similarity, calculate_field_fuzzy_similarity, preprocess_text
from ai.image_matching import calculate_image_similarity

def calculate_date_similarity(date1, date2):
    """
    Exponential decay based on absolute day difference between dates.
    Same day = 1.0 (100%), 1 day diff = 0.85, 3 days = 0.55, >7 days = 0.0
    """
    if not date1 or not date2:
        return 0.5
        
    delta_days = abs((date1 - date2).days)
    if delta_days == 0:
        return 1.0
    elif delta_days <= 7:
        return max(0.0, 1.0 - (delta_days / 7.0))
    else:
        return 0.0

def compute_item_match_score(lost_item, found_item):
    """
    Multi-attribute weighted matching score between a Lost item and a Found item.
    Returns tuple: (total_score_percentage, list_of_reason_strings)
    """
    weights = Config.MATCHING_WEIGHTS.copy()
    reasons = []
    
    # 1. Category Similarity (20%)
    cat1 = preprocess_text(lost_item.category)
    cat2 = preprocess_text(found_item.category)
    if cat1 == cat2:
        category_score = 1.0
        reasons.append(f"✓ Exact Category Match: {lost_item.category}")
    elif cat1 in cat2 or cat2 in cat1:
        category_score = 0.7
        reasons.append(f"✓ Related Category: {lost_item.category} / {found_item.category}")
    else:
        category_score = 0.0

    # 2. Text / Description Similarity (35%)
    # Combine item name and description for broad NLP matching
    lost_full_text = f"{lost_item.item_name} {lost_item.description} {lost_item.brand or ''} {lost_item.color or ''}"
    found_full_text = f"{found_item.item_name} {found_item.description} {found_item.brand or ''} {found_item.color or ''}"
    text_score = calculate_text_similarity(lost_full_text, found_full_text)
    
    if text_score >= 0.75:
        reasons.append(f"✓ High Description Similarity ({text_score*100:.0f}%)")
    elif text_score >= 0.40:
        reasons.append(f"✓ Moderate Text Description Overlap ({text_score*100:.0f}%)")
    elif text_score >= 0.20:
        reasons.append(f"✓ Partial Keyword Match ({text_score*100:.0f}%)")

    # 3. Color & Brand Similarity (15%)
    color_score = 0.0
    brand_score = 0.0
    
    if lost_item.color and found_item.color:
        color_score = calculate_field_fuzzy_similarity(lost_item.color, found_item.color)
        if color_score >= 0.7:
            reasons.append(f"✓ Matching Color: {lost_item.color}")
            
    if lost_item.brand and found_item.brand:
        brand_score = calculate_field_fuzzy_similarity(lost_item.brand, found_item.brand)
        if brand_score >= 0.7:
            reasons.append(f"✓ Matching Brand: {lost_item.brand}")

    # Combine color and brand scores
    if (lost_item.color and found_item.color) and (lost_item.brand and found_item.brand):
        color_brand_score = (color_score + brand_score) / 2.0
    elif lost_item.color and found_item.color:
        color_brand_score = color_score
    elif lost_item.brand and found_item.brand:
        color_brand_score = brand_score
    else:
        color_brand_score = 0.5 # Neutral if neither specified

    # 4. Location Similarity (15%)
    loc_score = calculate_field_fuzzy_similarity(lost_item.location, found_item.location)
    if loc_score >= 0.7:
        reasons.append(f"✓ Nearby Location Match: '{lost_item.location}' vs '{found_item.location}'")
    elif loc_score >= 0.4:
        reasons.append(f"✓ Similar Location Context")

    # 5. Date / Time Similarity (10%)
    date_score = calculate_date_similarity(lost_item.date, found_item.date)
    delta_days = abs((lost_item.date - found_item.date).days)
    if delta_days == 0:
        reasons.append("✓ Exact Same Date Reported")
    elif delta_days <= 3:
        reasons.append(f"✓ Dates Matched within {delta_days} days")

    # 6. Image Similarity (5%)
    img_score = calculate_image_similarity(lost_item.image_path, found_item.image_path)
    
    if img_score is not None:
        if img_score >= 0.75:
            reasons.append(f"✓ High Image Feature Match ({img_score*100:.0f}%)")
        elif img_score >= 0.50:
            reasons.append(f"✓ Image Color Profile Match ({img_score*100:.0f}%)")
    else:
        # Reallocate 5% image weight to text (3.5%) and category (1.5%) if image missing
        weights['text_similarity'] += 0.035
        weights['category_similarity'] += 0.015
        img_score = 0.0

    # Calculate final weighted total
    total_score = (
        (text_score * weights['text_similarity']) +
        (category_score * weights['category_similarity']) +
        (color_brand_score * weights['color_brand_similarity']) +
        (loc_score * weights['location_similarity']) +
        (date_score * weights['datetime_similarity']) +
        (img_score * (weights['image_similarity'] if img_score is not None else 0.0))
    ) * 100.0

    # Ensure total score bounded between 0 and 100
    total_score = round(max(0.0, min(100.0, total_score)), 1)
    
    if not reasons:
        reasons.append("• Low structural correlation between item attributes.")

    return total_score, reasons


def run_matching_for_item(target_item):
    """
    Executes AI matching pipeline for a newly submitted or updated item
    against all active records of the opposite type.
    Creates or updates Match records and triggers notifications.
    """
    opposite_type = 'found' if target_item.type == 'lost' else 'lost'
    candidate_items = Item.query.filter(
        Item.type == opposite_type,
        Item.status == 'active'
    ).all()

    record_threshold = Config.MATCH_SCORE_THRESHOLDS['RECORD_THRESHOLD']
    notification_threshold = Config.MATCH_SCORE_THRESHOLDS['NOTIFICATION_THRESHOLD']

    new_matches_count = 0

    for candidate in candidate_items:
        if target_item.type == 'lost':
            lost_item, found_item = target_item, candidate
        else:
            lost_item, found_item = candidate, target_item

        score, reasons = compute_item_match_score(lost_item, found_item)

        if score >= record_threshold:
            # Check for existing match entry
            match = Match.query.filter_by(
                lost_item_id=lost_item.id,
                found_item_id=found_item.id
            ).first()

            reason_json = json.dumps(reasons)

            if not match:
                match = Match(
                    lost_item_id=lost_item.id,
                    found_item_id=found_item.id,
                    match_score=score,
                    match_reason=reason_json,
                    status='pending'
                )
                db.session.add(match)
                db.session.flush() # Populate match.id
                new_matches_count += 1
            else:
                match.match_score = score
                match.match_reason = reason_json

            # Create High Confidence Notifications if score >= 75%
            if score >= notification_threshold:
                # Notify Lost Item Owner
                lost_user_id = lost_item.user_id
                existing_lost_notif = Notification.query.filter_by(
                    user_id=lost_user_id, match_id=match.id
                ).first()
                if not existing_lost_notif:
                    db.session.add(Notification(
                        user_id=lost_user_id,
                        match_id=match.id,
                        message=f"High Confidence AI Match ({score:.0f}%) found for your lost item '{lost_item.item_name}'!"
                    ))

                # Notify Found Item Reporter
                found_user_id = found_item.user_id
                existing_found_notif = Notification.query.filter_by(
                    user_id=found_user_id, match_id=match.id
                ).first()
                if not existing_found_notif:
                    db.session.add(Notification(
                        user_id=found_user_id,
                        match_id=match.id,
                        message=f"High Confidence AI Match ({score:.0f}%) found for your reported found item '{found_item.item_name}'!"
                    ))

    db.session.commit()
    return new_matches_count
