# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Routes Package
# =====================================================

from backend.routes.auth_routes import auth_bp, login_required
from backend.routes.worker_routes import worker_bp
from backend.routes.complaint_routes import complaint_bp
from backend.routes.employer_routes import employer_bp
from backend.routes.dashboard_routes import dashboard_bp

__all__ = [
    'auth_bp',
    'worker_bp',
    'complaint_bp',
    'employer_bp',
    'dashboard_bp',
    'login_required'
]