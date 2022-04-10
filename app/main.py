from flask import Flask, request
from flask_swagger_ui import get_swaggerui_blueprint

from simulator import Simulator


def setup_swaggerui(app):
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.yaml'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "CT-Simulator"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

app = Flask(__name__)
setup_swaggerui(app)


'''
Params of simulation:
- N: size of population [int]
- T: time to simulate [int]
- rules: array of rules [array of object]
- seed: to be able to recreate simulations [int]
'''

@app.route("/simulation", methods=['GET'])
def simulation():
    body = request.get_json()
    return Simulator.run(**body)