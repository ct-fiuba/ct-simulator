from flask import Flask, request, jsonify
#from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

from simulator import Simulator

'''
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
'''


app = Flask(__name__)
CORS(app)
#setup_swaggerui(app)

sim = Simulator()

rules = [
    {
    "contagionRisk": 2,
    "durationValue": 20,
    "durationCmp": ">",
    "m2Value": None,
    "m2Cmp": None,
    "openSpace": None
    },
    {
    "contagionRisk": 1,
    "m2Value": 20,
    "m2Cmp": "<",
    "durationValue": None,
    "durationCmp": None,
    "openSpace": None
    },
]

restricted_rules = [
    {
    "contagionRisk": 2,
    "durationValue": 1,
    "durationCmp": ">",
    "m2Value": None,
    "m2Cmp": None,
    "openSpace": None
    },
]

free_rules = [
    {
    "contagionRisk": 0,
    "durationValue": 1000,
    "durationCmp": ">",
    "m2Value": None,
    "m2Cmp": None,
    "openSpace": None
    },
]


'''
Params of simulation:
- N: size of population [int]
- T: time to simulate [int]
- rules: array of rules [array of object]
- seed: to be able to recreate simulations [int]
'''

@app.route("/simulation", methods=['POST'])
def simulation():
    body = request.get_json()
    print(body)
    init_infected = body["infectedUsers"] / body["users"] 
    print(init_infected)
    return jsonify(sim.run(rules_info=body["rules"], t=body["days"], n_pop=body["users"], n_places=body["establishments"], init_infected=init_infected))

app.run(host="0.0.0.0", port=5000)