from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # Makes the server externally visible
        port=5000,       # Port 5000 is Flask's default
        debug=True       # Enable debug mode for development
    )
