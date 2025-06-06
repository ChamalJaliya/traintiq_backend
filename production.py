from waitress import serve
from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    print('Starting production server...')
    print('Server will be available at: http://localhost:8000')
    serve(app, host='0.0.0.0', port=8000, threads=4) 