from flask import Flask
from flask_mail import Mail

def create_app():
    app = Flask(__name__)
    app.config['DATABASE'] = {
        'dbname': 'your_dbname',
        'user': 'your_user',
        'password': 'your_password',
        'host': 'localhost',  # Or your host
        'port': '5432'  # Default PostgreSQL port
    }
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '@gmail.com'  
    app.config['MAIL_PASSWORD'] = 'your_email_password'  
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    mail = Mail(app) 
    @app.before_request
    def before_request():
        """Open a new database connection if there is none yet for the current app context."""
        g.db = psycopg2.connect(
            dbname=app.config['DATABASE']['dbname'],
            user=app.config['DATABASE']['user'],
            password=app.config['DATABASE']['password'],
            host=app.config['DATABASE']['host'],
            port=app.config['DATABASE']['port']
        )

    # Close the database connection after the request
    @app.teardown_request
    def teardown_request(exception=None):
        """Close the database connection."""
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()
    from .routes import main
    app.register_blueprint(main)

    return app
