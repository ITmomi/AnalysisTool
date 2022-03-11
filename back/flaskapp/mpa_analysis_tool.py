import os

from flask import Flask, render_template, g, send_from_directory
# from flask_cors import CORS
from flask_restx import Api

from config.app_config import *
from controller.analysis.controller_analysis import ANALYSIS
from controller.converter.converter import CONVERTER
from controller.dbimport.controller_import import IMPORT
from controller.export.controller_export import EXPORT
from controller.resources.controller_resources import RESOURCES
from controller.setting.controller_setting import SETTING
from controller.preview.controller_preview import PREVIEW
from controller.overlay.controller_overlay import OVERLAY


def create_app(config_filename=None):
    app = Flask(__name__, static_folder='../web/static/', template_folder='../web/static')

    if config_filename is not None:
        app.config.from_pyfile(config_filename)

    app.config.SWAGGER_UI_DOC_EXPANSION = 'none'  # none, list, full
    # app.config.SWAGGER_SUPPORTED_SUBMIT_METHODS = []

    api = Api(app,
              doc='/doc/',
              version=app.config['API_VERSION'],
              title=app.config['API_TITLE'],
              description=app.config['API_DESCRIPTION'],
              license=app.config['API_LICENSE'])

    # 외부 서비스, 포트, 도메인에서의 API요청을 허용
    # CORS(app, resources={r"/api/*": {"origins": "*"}})

    # MPA Analysis Tool 전용 REST API
    api.add_namespace(ANALYSIS, '/api/analysis')
    api.add_namespace(SETTING, '/api/setting')
    api.add_namespace(RESOURCES, '/api/resources')

    # 공용 REST API
    api.add_namespace(CONVERTER, '/api/converter')
    api.add_namespace(IMPORT, '/api/import')
    api.add_namespace(EXPORT, '/api/export')
    api.add_namespace(PREVIEW, '/api/preview')

    # Overlay Analysis REST API
    api.add_namespace(OVERLAY, '/api/overlay')

    @app.route('/main', methods=['GET'])
    def catch_all():
        g.jinja2_test = 'made by gtttpark!'
        return render_template('index.html')

    @app.route('/main/notsupport', methods=['GET'])
    def nosupport():
        return render_template('notsupport.html')

    @app.route('/main/<path:filename>', methods=['GET'])
    def nosupport_svg(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_PATH), filename)

    @app.route('/js/<path:filename>')
    def serve_static_js(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_JS_PATH), filename)

    @app.route('/<path:filename>')
    def serve_static(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_PATH), filename)

    @app.route('/fonts/<path:filename>')
    def serve_static_fonts(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_PONTS_PATH), filename)

    return app
