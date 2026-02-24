# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Flask Main Application - Using PyMySQL
# =====================================================

from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sys

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add project root to path for imports
sys.path.insert(0, PROJECT_ROOT)

from backend.config import config
from backend.routes.auth_routes import auth_bp
from backend.routes.worker_routes import worker_bp
from backend.routes.complaint_routes import complaint_bp
from backend.routes.employer_routes import employer_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.job_routes import job_bp
from backend.routes.admin_routes import admin_bp


def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                static_folder=PROJECT_ROOT,
                static_url_path='')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(worker_bp, url_prefix='/api')
    app.register_blueprint(complaint_bp, url_prefix='/api/complaint')
    app.register_blueprint(employer_bp, url_prefix='/api/employers')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(job_bp, url_prefix='/api/jobs')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Serve index.html for root
    @app.route('/')
    def index():
        return send_file(os.path.join(PROJECT_ROOT, 'index.html'))
    
    # Serve pages directory
    @app.route('/pages/<path:filename>')
    def serve_pages(filename):
        return send_from_directory(os.path.join(PROJECT_ROOT, 'pages'), filename)
    
    # Serve css directory
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(PROJECT_ROOT, 'css'), filename)
    
    # Serve js directory
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(PROJECT_ROOT, 'js'), filename)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'MLGMS API is running',
            'version': '1.0.0'
        }), 200
    
    # Handle favicon.ico
    @app.route('/favicon.ico')
    def favicon():
        return '', 204
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request'
        }), 400
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Get configuration from environment
    env = os.environ.get('FLASK_ENV', 'development')
    
    print("=" * 60)
    print("Migrant Labor & Grievance Management System (MLGMS)")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Project Root: {PROJECT_ROOT}")
    print("Server running on: http://localhost:5000")
    print("API Base URL: http://localhost:5000/api")
    print("=" * 60)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True if env == 'development' else False
    )