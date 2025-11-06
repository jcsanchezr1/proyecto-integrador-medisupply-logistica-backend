import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    cors = CORS(app)
    
    from .config.database import create_tables
    create_tables()
    
    configure_routes(app)
    
    return app


def configure_routes(app):
    from .controllers.health_controller import HealthCheckView
    from .controllers.route_controller import RouteCreateController, RouteListController, RouteDetailController, RouteDeleteAllController
    
    api = Api(app)
    
    api.add_resource(HealthCheckView, '/logistics/ping')
    api.add_resource(RouteCreateController, '/logistics/routes')
    api.add_resource(RouteListController, '/logistics/routes')
    api.add_resource(RouteDetailController, '/logistics/routes/<int:route_id>')
    api.add_resource(RouteDeleteAllController, '/logistics/routes/delete-all')

