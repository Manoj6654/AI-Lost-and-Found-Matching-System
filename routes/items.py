import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models.models import db, Item, Match
from routes.user import login_required
from ai.matching_engine import run_matching_for_item

items_bp = Blueprint('items', __name__)

CATEGORY_CHOICES = [
    'Electronics', 'Keys', 'Wallets & Bags', 'Documents & ID',
    'Clothing & Footwear', 'Jewelry & Watches', 'Pets', 'Books & Stationery', 'Other'
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def handle_image_upload(file):
    if not file or file.filename == '':
        return None
        
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{int(datetime.utcnow().timestamp())}.{ext}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        return f"uploads/{unique_filename}"
    else:
        flash('Invalid image file format. Allowed formats: PNG, JPG, JPEG, GIF, WEBP.', 'danger')
        return False

@items_bp.route('/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '').strip()
        brand = request.form.get('brand', '').strip()
        location = request.form.get('location', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        additional_details = request.form.get('additional_details', '').strip()

        if not item_name or not category or not description or not location or not date_str:
            flash('Please fill in all required fields marked with *.', 'danger')
            return render_template('report_lost.html', categories=CATEGORY_CHOICES, form=request.form)

        try:
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('report_lost.html', categories=CATEGORY_CHOICES, form=request.form)

        time_val = None
        if time_str:
            try:
                time_val = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                pass

        if additional_details:
            description += f" Additional details: {additional_details}"

        # Image Upload
        image_path = None
        if 'image' in request.files:
            file_res = handle_image_upload(request.files['image'])
            if file_res is False:
                return render_template('report_lost.html', categories=CATEGORY_CHOICES, form=request.form)
            image_path = file_res

        # Save to database
        new_item = Item(
            user_id=session['user_id'],
            type='lost',
            item_name=item_name,
            category=category,
            description=description,
            color=color,
            brand=brand,
            location=location,
            date=date_val,
            time=time_val,
            image_path=image_path,
            status='active'
        )

        db.session.add(new_item)
        db.session.commit()

        # Trigger AI Matching Engine
        new_matches_count = run_matching_for_item(new_item)

        flash(f'Lost item reported successfully! AI scan complete: found {new_matches_count} prospective matches.', 'success')
        return redirect(url_for('matches.match_results', item_id=new_item.id))

    return render_template('report_lost.html', categories=CATEGORY_CHOICES)


@items_bp.route('/report-found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '').strip()
        brand = request.form.get('brand', '').strip()
        location = request.form.get('location', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        additional_details = request.form.get('additional_details', '').strip()

        if not item_name or not category or not description or not location or not date_str:
            flash('Please fill in all required fields marked with *.', 'danger')
            return render_template('report_found.html', categories=CATEGORY_CHOICES, form=request.form)

        try:
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('report_found.html', categories=CATEGORY_CHOICES, form=request.form)

        time_val = None
        if time_str:
            try:
                time_val = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                pass

        if additional_details:
            description += f" Additional details: {additional_details}"

        # Image Upload
        image_path = None
        if 'image' in request.files:
            file_res = handle_image_upload(request.files['image'])
            if file_res is False:
                return render_template('report_found.html', categories=CATEGORY_CHOICES, form=request.form)
            image_path = file_res

        # Save to database
        new_item = Item(
            user_id=session['user_id'],
            type='found',
            item_name=item_name,
            category=category,
            description=description,
            color=color,
            brand=brand,
            location=location,
            date=date_val,
            time=time_val,
            image_path=image_path,
            status='active'
        )

        db.session.add(new_item)
        db.session.commit()

        # Trigger AI Matching Engine
        new_matches_count = run_matching_for_item(new_item)

        flash(f'Found item reported successfully! AI scan complete: found {new_matches_count} prospective matches.', 'success')
        return redirect(url_for('matches.match_results', item_id=new_item.id))

    return render_template('report_found.html', categories=CATEGORY_CHOICES)


@items_bp.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)


@items_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    item_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    items_query = Item.query

    if query:
        search_filter = f"%{query}%"
        items_query = items_query.filter(
            (Item.item_name.ilike(search_filter)) |
            (Item.description.ilike(search_filter)) |
            (Item.location.ilike(search_filter)) |
            (Item.brand.ilike(search_filter)) |
            (Item.color.ilike(search_filter))
        )

    if category:
        items_query = items_query.filter(Item.category == category)

    if item_type in ['lost', 'found']:
        items_query = items_query.filter(Item.type == item_type)

    if status in ['active', 'claimed', 'resolved']:
        items_query = items_query.filter(Item.status == status)

    results = items_query.order_by(Item.created_at.desc()).all()

    return render_template(
        'search.html',
        items=results,
        query=query,
        category=category,
        item_type=item_type,
        status=status,
        categories=CATEGORY_CHOICES
    )
