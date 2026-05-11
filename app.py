"""
app.py — Meditrack: Expiry Risk Prediction & Drug Wastage Minimization
Entry point for the Flask application.
"""
from flask import Flask
from extensions import db, login_manager
import webbrowser


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.prediction import prediction_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        import models_db  # noqa: F401 — registers ORM models with SQLAlchemy
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Create default admin user on first run."""
    from models_db import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@meditrack.com",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    webbrowser.open('http://localhost:5000')
    app.run(debug=True, port=5000)
