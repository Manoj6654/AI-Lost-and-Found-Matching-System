import os
from flask import Flask, render_template, session
from config import Config
from models.models import db, User, Item, Match, Notification

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.items import items_bp
    from routes.matches import matches_bp
    from routes.claims import claims_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(claims_bp)
    app.register_blueprint(admin_bp)

    # Context Processor for Navbar Badges & Notifications
    @app.context_processor
    def inject_user_context():
        context = {
            'unread_notifications_count': 0,
            'current_user': None
        }
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                context['current_user'] = user
                context['unread_notifications_count'] = Notification.query.filter_by(
                    user_id=user.id, is_read=False
                ).count()
        return context

    # Home Landing Page
    @app.route('/')
    def index():
        recent_lost = Item.query.filter_by(type='lost', status='active').order_by(Item.created_at.desc()).limit(6).all()
        recent_found = Item.query.filter_by(type='found', status='active').order_by(Item.created_at.desc()).limit(6).all()
        total_items = Item.query.count()
        total_matches = Match.query.filter(Match.match_score >= 50.0).count()
        total_resolved = Item.query.filter_by(status='resolved').count()
        
        return render_template(
            'index.html',
            recent_lost=recent_lost,
            recent_found=recent_found,
            total_items=total_items,
            total_matches=total_matches,
            total_resolved=total_resolved
        )

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return "Uploaded image file is too large. Maximum size allowed is 16MB.", 413

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting AI-Based Lost & Found Matching System...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='127.0.0.1', port=5000, debug=True)
