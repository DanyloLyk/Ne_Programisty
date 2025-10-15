import os
from flask import Flask
from .routes import main

def create_app():
    app = Flask(__name__)
    # Read Google Maps API key from environment (set GOOGLE_MAPS_API_KEY)
    app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')

    # Make the key available in all templates as GOOGLE_MAPS_API_KEY
    @app.context_processor
    def inject_google_maps_key():
        return dict(GOOGLE_MAPS_API_KEY=app.config.get('GOOGLE_MAPS_API_KEY', ''))

    app.register_blueprint(main)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)