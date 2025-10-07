from flask import Flask
from app.models.user import db


def create_app():

    app = Flask(__name__)
    app.secret_key = "your_secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        from app import routes
        db.create_all()
  
    return app


