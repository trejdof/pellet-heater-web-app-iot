import os
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.abspath('templates'),
                static_folder=os.path.abspath('static'),  # Explicitly set static folder


    )
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
