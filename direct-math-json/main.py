
import math
import requests
import yaml
import json

from flask import Flask, Response, jsonify
from flask_restplus import Api, Resource, fields, Namespace, reqparse
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode

#--- Setup websever and API ---#

app = Flask(__name__)
#app.config['SERVER_NAME'] = 'public-api-dot-delta-229415.appspot.com' 
api = Api(app, version='1.0', default='Test API Services', title='API path, query string, request body parameters', 
    description='All responses are JSON, have to complete Header example',)

app.config.SWAGGER_UI_OPERATION_ID = True
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

#--- Path Parameter Example. Will not fail on negative values ---#

sigmoid_parser = reqparse.RequestParser()
sigmoid_parser.add_argument('x', type=float, help='x value', default=1.0)
@api.route('/sigmoid/', endpoint='sigmoid')
class sigmoid(Resource):
    @api.expect(sigmoid_parser)
    def get(self):
        args = sigmoid_parser.parse_args()
        x = args['x']
        result = 1/(1+math.exp(-x))
        return {"Sigmoid" : result}


#--- Path Parameter Example. ---#

@api.route('/echo/<string:name>', endpoint='echo')
class echo(Resource):
    @api.doc(params={'name': 'Example of Path Parameter'})
    def get(self,name):
        result = "hello," + name
        return {"echo": result}


#--- Request Body Parameter Example ---#

cartesion = api.model('Cartersion', {
    'x': fields.Float(description='real component'),
    'y': fields.Float(description='complex component')
})
polar = api.model('Polar', {
    'r': fields.Float(description='real component'),
    'theta': fields.Float(description='complex component')
})

@api.route('/complex')
class Complex(Resource):
    # Ask flask_restplus to validate the incoming payload
    @api.expect(cartesion, validate=True)
    @api.marshal_with(polar)
    def post(self):
        x = api.payload['x']
        y = api.payload['y']
        api.payload['r'] = math.hypot(x, y)
        api.payload['theta'] = math.degrees(math.atan(y/x))
        return api.payload

#--- JSON Generation from Python Code without using Swagger Libraries ---#

@api.route('/json/')
class JSON(Resource):
    def get(self):
        json_data = jsonify(api.__schema__)
        return json_data

#--- Convert JSON to YAML (OpenAPI 3.0) by calling external service ---#

yaml30_parser = reqparse.RequestParser()
yaml30_parser.add_argument('url', type=str, help='url for json', default="https://public-api-dot-delta-229415.appspot.com/swagger.json")
@api.route('/yaml30/', endpoint='yaml30')
class yaml30(Resource):
    @api.doc(parser=yaml30_parser)
    def get(self):
        args = yaml30_parser.parse_args()
        url = args['url']
        conversion_api = 'https://mermade.org.uk/api/v1/convert?url='
        request_string = conversion_api + url
        result = requests.get(request_string).content
        resp = Response(result, mimetype='text/html')
        return resp

#--- Convert JSON to YAML using pyyaml ---#

@api.route('/yaml/')
class YAML(Resource):
    def get(self):
        #app.config["SERVER_NAME"] = HOST
        json_data = json.dumps(api.__schema__)
        #json_data = jsonify(api.__schema__)
        yaml_dump = yaml.dump(json_data, default_flow_style=False).replace('\'','')
        resp = Response(yaml_dump, mimetype='text/plain')
        return resp

#--- JSON Crypto ---#

person = api.model('Person', {
                      'name': fields.String(description='persons name', default="Mamoon"),
                      'age': fields.String(description='age',default='50'),
                      'city': fields.String(default="Newton")})

person_parser = reqparse.RequestParser()
person_parser.add_argument('field_id', type=str, required=True, default="name", choices=['name','age','city'])

@api.route('/person/')
class Person(Resource):
    # Ask flask_restplus to validate the incoming payload
    @api.doc(parser=person_parser,body=person, validate=True)
    @api.marshal_with(person)
    def post(self):
        args = person_parser.parse_args()
        field_id = args['field_id']
        
        # json value to encrypt based on field_id passed in url
        segment = api.payload[field_id]
        key = jwk.JWK.generate(kty='oct', size=256)
        jwetoken = jwe.JWE(segment.encode('utf-8'), json_encode({"alg": "A256KW", "enc": "A256CBC-HS512"}))
        jwetoken.add_recipient(key)
        segment_enc = jwetoken.serialize()

        #set encrypted value to return
        api.payload[field_id] = segment_enc

        return api.payload

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='0.0.0.0', port=9999, debug=True)
# [END gae_python37_app]
