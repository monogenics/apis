import json
from flask import json,jsonify
import yaml
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode
from flask import Flask
from flask_restplus import Api, Resource, fields, Namespace, reqparse

HOST = '0.0.0.0'

app = Flask(__name__)

app.config.SWAGGER_UI_OPERATION_ID = True
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

api = Api(app, version='1.1', default='JSON Crypto', title='API for JSON Crypto', description='API to experiment with JWE, JWS',)

person = api.model('Person', {
                      'name': fields.String(description='persons name', default="Mamoon"),
                      'age': fields.String(description='age',default='50'),
                      'city': fields.String(default="Newton")})

parser = reqparse.RequestParser()
parser.add_argument('field_id', type=str, required=True, default="name", choices=['name','age','city'])

@api.route('/person/')
class Person(Resource):
    
    # Ask flask_restplus to validate the incoming payload
    @api.doc(parser=parser,body=person, validate=True)
    @api.marshal_with(person)
    def post(self):
        args = parser.parse_args()
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

@api.route('/json/')
class JSON(Resource):
    def get(self):
        #app.config["SERVER_NAME"] = HOST
        return api.__schema__

@api.route('/yaml/')
class YAML(Resource):
    def get(self):
        #app.config["SERVER_NAME"] = HOST
        import yaml
        json_data = api.__schema__
        print(json_data)
        yaml_dump = yaml.dump(json_data, default_flow_style=False,line_break=None)
        formatted_yaml=yaml_dump.split('\n')
        str1 = '\\n'.join(formatted_yaml)
        print(yaml_dump)
        return str1

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host=HOST, port=9999, debug=True)
