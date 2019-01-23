
from flask import Flask
from flask_restplus import Api, Resource, fields, Namespace
import math

app = Flask(__name__)
app.config['SERVER_NAME'] = 'public-api-dot-delta-229415.appspot.com' 
api = Api(app, version='1.0', default='DNN', title='API for Deep Neural Networks',
          description='Low level compuation for Deep Neural Networks',)

cartesion = api.model('Cartersion', {
    'x': fields.Float(description='real component'),
    'y': fields.Float(description='complex component')
})
polar = api.model('Polar', {
    'r': fields.Float(description='real component'),
    'theta': fields.Float(description='complex component')
})

parser = api.parser()
parser.add_argument('x', type=int, help='x value', location='form')

@api.route('/tanh/', endpoint='tanh')
class WithParserResource(Resource):
    @api.expect(parser)
    def put(self):
        args = parser.parse_args()
        x = args['x']
        return {"tanh" : math.tanh(x)}

@api.route('/sigmoid/', endpoint='sigmoid')
class WithParserResource(Resource):
    @api.expect(parser)
    def put(self):
        args = parser.parse_args()
        x = args['x']
        result = 1/(1+math.exp(-x))
        return {"Sigmoid" : result}

parser = api.parser()
parser.add_argument('x', type=int, help='x value', location='form')
parser.add_argument('y', type=int, help='y value', location='form')

@api.route('/l2norm/', endpoint='l2norm')
class WithParserResource(Resource):
    @api.expect(parser)
    def put(self):
        args = parser.parse_args()
        x = args['x']
        y = args['y']
        
        return {"l2norm" : math.hypot(x,y)}

# This class will handle POST to /complex
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
        
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
